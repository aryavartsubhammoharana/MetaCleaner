import os
import zipfile
import xml.etree.ElementTree as ET
import tempfile
import shutil

class OfficeService:
    # Namespaces used in docProps/core.xml
    NAMESPACES = {
        'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'dcterms': 'http://purl.org/dc/terms/',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    @staticmethod
    def read_metadata(filepath):
        """
        Reads metadata from docProps/core.xml within OpenXML zip files (docx, xlsx, pptx).
        """
        metadata = {}
        if not zipfile.is_zipfile(filepath):
            return metadata

        try:
            with zipfile.ZipFile(filepath, 'r') as z:
                # Core metadata is in docProps/core.xml
                if 'docProps/core.xml' in z.namelist():
                    core_xml = z.read('docProps/core.xml')
                    root = ET.fromstring(core_xml)
                    
                    # Mapping of tag (without namespace prefix) to UI display name
                    tag_mapping = {
                        'title': 'Title',
                        'subject': 'Subject',
                        'creator': 'Author/Creator',
                        'lastModifiedBy': 'Last Modified By',
                        'created': 'Date Created',
                        'modified': 'Date Modified',
                        'keywords': 'Keywords',
                        'description': 'Description',
                        'revision': 'Revision Number'
                    }

                    # Walk through the elements
                    for key, display_name in tag_mapping.items():
                        # Search under various namespaces
                        found_elem = None
                        for ns_prefix, ns_uri in OfficeService.NAMESPACES.items():
                            found_elem = root.find(f'.//{{{ns_uri}}}{key}')
                            if found_elem is not None:
                                break
                        
                        if found_elem is not None and found_elem.text:
                            metadata[display_name] = found_elem.text.strip()
        except Exception as e:
            print(f"Error reading Office metadata: {e}")
            
        return metadata

    @staticmethod
    def clean_metadata(input_path, output_path):
        """
        Cleans metadata from docProps/core.xml and docProps/custom.xml.
        Creates a new ZIP file copying all original content except the metadata files
        which are written with empty properties.
        """
        if not zipfile.is_zipfile(input_path):
            return False

        try:
            blank_core = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
                'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
                'xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
                '  <dc:title></dc:title>\n'
                '  <dc:subject></dc:subject>\n'
                '  <dc:creator></dc:creator>\n'
                '  <cp:keywords></cp:keywords>\n'
                '  <dc:description></dc:description>\n'
                '  <cp:lastModifiedBy></cp:lastModifiedBy>\n'
                '  <cp:revision>1</cp:revision>\n'
                '  <dcterms:created xsi:type="dcterms:W3CDTF">1970-01-01T00:00:00Z</dcterms:created>\n'
                '  <dcterms:modified xsi:type="dcterms:W3CDTF">1970-01-01T00:00:00Z</dcterms:modified>\n'
                '</cp:coreProperties>'
            )

            blank_custom = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/custom-properties" '
                'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">\n'
                '</Properties>'
            )

            with zipfile.ZipFile(input_path, 'r') as z_in:
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as z_out:
                    for item in z_in.infolist():
                        filename = item.filename
                        
                        if filename == 'docProps/core.xml':
                            # Overwrite core metadata with blank
                            z_out.writestr(filename, blank_core)
                        elif filename == 'docProps/custom.xml':
                            # Overwrite custom metadata with blank
                            z_out.writestr(filename, blank_custom)
                        elif filename.startswith('docProps/thumbnail.'):
                            # Skip thumbnail if it could contain document preview screenshots
                            continue
                        else:
                            # Copy the original file unmodified
                            z_out.writestr(item, z_in.read(filename))
            return True
        except Exception as e:
            print(f"Error cleaning Office metadata: {e}")
            return False
