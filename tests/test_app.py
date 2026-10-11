import pytest
import io
import os
import json
from app import app
from core.validator import validate_file
from core.detector import detect_file_type
from core.cleaner import clean_file_metadata

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_homepage_loads(client):
    res = client.get('/')
    assert res.status_code == 200
    assert b"MetaCleaner" in res.data
    assert b"Developed by" in res.data

def test_about_page(client):
    res = client.get('/about')
    assert res.status_code == 200
    assert b"About" in res.data

def test_privacy_page(client):
    res = client.get('/privacy')
    assert res.status_code == 200
    assert b"Privacy" in res.data

def test_security_headers_and_csp(client):
    res = client.get('/')
    csp = res.headers.get('Content-Security-Policy')
    assert csp is not None
    assert "default-src 'self'" in csp
    assert res.headers.get('X-Content-Type-Options') == 'nosniff'

def test_static_dlm_logo(client):
    res = client.get('/static/images/dlm.png')
    assert res.status_code == 200
    assert len(res.data) > 0

def test_upload_empty_request(client):
    res = client.post('/upload', data={})
    assert res.status_code == 400
    data = json.loads(res.data)
    assert data['success'] is False

def test_upload_and_clean_text_file(client, tmp_path):
    data = {
        'file': (io.BytesIO(b"Hello world! This is a test file."), 'sample.txt')
    }
    res = client.post('/upload', data=data, content_type='multipart/form-data')
    assert res.status_code == 200
    res_json = json.loads(res.data)
    assert res_json['success'] is True
    file_id = res_json['data']['file_id']

    clean_res = client.post('/clean', json={'file_id': file_id})
    assert clean_res.status_code == 200
    clean_json = json.loads(clean_res.data)
    assert clean_json['success'] is True
    cleaned_file_id = clean_json['data']['cleaned_file_id']

    download_res = client.get(f'/download/{cleaned_file_id}?name=sample.txt')
    assert download_res.status_code == 200
    assert b"Hello world" in download_res.data

def test_validator_rejects_empty_file(tmp_path):
    empty_file = tmp_path / "empty.txt"
    empty_file.write_bytes(b"")
    is_valid, msg = validate_file(str(empty_file))
    assert is_valid is False
    assert "empty" in msg.lower()

def test_health_check(client):
    res = client.get('/health')
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'MetaCleaner'

def test_hardened_security_headers(client):
    res = client.get('/')
    assert res.headers.get('X-Frame-Options') == 'DENY'
    assert res.headers.get('Referrer-Policy') == 'strict-origin-when-cross-origin'
    assert 'geolocation=()' in res.headers.get('Permissions-Policy', '')

def test_validator_rejects_executable_extension(tmp_path):
    fake_exe = tmp_path / "malicious.exe"
    fake_exe.write_bytes(b"MZfakeexecutablepayload")
    is_valid, msg = validate_file(str(fake_exe))
    assert is_valid is False
    assert "unsupported" in msg.lower()

def test_custom_404_page(client):
    res = client.get('/nonexistent-page-random')
    assert res.status_code == 404
    assert b"404" in res.data
    assert b"Return to Clean" in res.data

