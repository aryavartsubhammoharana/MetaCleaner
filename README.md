# MetaCleaner

MetaCleaner is a modern, production-ready, dark-mode-first **Metadata Cleaner** web application. It allows users to upload various file formats, preview their metadata, strip all tracking and identification tags, and download clean files. 

For absolute privacy, files are stored temporarily and **wiped automatically** from the disk immediately upon downloading, or pruned after 15 minutes of inactivity.

---

## 🌟 Key Features
- **Comprehensive Metadata Previews:** Inspect GPS coordinates, camera model, author signatures, creating application, software tags, and timestamps before processing.
- **Robust Multi-format Cleaning:**
  - **Images:** JPG, JPEG, PNG, TIFF, WebP, HEIC (with Pillow & `pi-heif`).
  - **Documents:** PDF (via `pypdf`), DOCX, XLSX, PPTX (via ZIP/XML direct stream editing).
  - **Media:** MP3, MP4, MOV, AVI (via Mutagen and optional FFmpeg stream copies).
- **Dual-Layer Architecture:** Pure Python fallback processors combined with optional CLI wrappers (`exiftool`, `ffmpeg`) for system integration.
- **Zero-Trust Privacy:** 
  - Real-time disk purging after download.
  - Periodic sweeps for abandoned files.
  - SSL/TLS security & secure name hashing.
- **Futuristic 3D Glassmorphic Interface:** Fully responsive UI featuring animated particle grids, mouse-based parallax card tilt, glowing neon accents, and smooth transitions.

---

## 📂 Project Structure
```
metacleaner/
├── app.py                     # Flask entry point
├── config.py                  # App configuration
├── requirements.txt           # Package dependencies
├── README.md                  # Documentation
├── .gitignore                 # Excluded directories
│
├── temp/                      # Temporary uploads & cleaned folders
│   ├── uploads/
│   └── cleaned/
│
├── core/
│   ├── __init__.py
│   ├── detector.py            # MIME-type and category detection
│   ├── validator.py           # File validation & security checking
│   ├── metadata_reader.py     # Router to read metadata
│   ├── cleaner.py             # Router to clean metadata
│   ├── response.py            # JSON responses & streaming cleanup
│   └── utils.py               # Conversions and stale file sweeps
│
├── cleaners/
│   ├── __init__.py
│   ├── generic.py             # Fallback generic metadata cleaner
│   ├── image/
│   │   ├── __init__.py
│   │   └── [jpg.py, png.py, jpeg.py, webp.py, tiff.py, heic.py]
│   ├── documents/
│   │   ├── __init__.py
│   │   └── [pdf.py, docx.py, pptx.py, xlsx.py]
│   └── media/
│       ├── __init__.py
│       └── [audio.py, video.py]
│
├── services/
│   ├── exif_service.py        # Image EXIF processing
│   ├── exiftool_service.py    # Fallback CLI Exiftool reader/cleaner
│   ├── ffmpeg_service.py      # Fallback CLI FFmpeg video cleaner
│   ├── pdf_service.py         # PDF page-copy rebuilder
│   ├── mutagen_service.py     # MP3/MP4 tag purger
│   └── office_service.py      # Office doc ZIP/XML modifier
│
├── static/
│   ├── css/
│   │   └── style.css          # Styling grid & neon layout
│   └── js/
│       └── script.js          # DOM binding & ajax operations
│
└── templates/
    ├── base.html              # Layout scaffold & glowing blobs
    ├── index.html             # Workspace dashboard
    ├── privacy.html           # Zero-trust privacy disclosure
    ├── about.html             # Educational background information
    └── 404.html               # Custom error page
```

---

## 🚀 Setup & Execution

### Prerequisites
Make sure Python 3.9+ is installed.

### Installation
1. Clone this repository or open the project folder.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. *(Optional)* For advanced media support, install [FFmpeg](https://ffmpeg.org/) and [ExifTool](https://exiftool.org/) and add them to your system's PATH.

### Running the App
Start the Flask development server:
```bash
python app.py
```
The app will run locally at [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## 🔒 Privacy Architecture
- **In-memory Stream Deletion:** Standard file system locks are bypassed using Flask generator yields. The disk delete operations occur within a `finally` block executing immediately after client output closes.
- **Cron sweeps:** If a client drops their connection before downloading, the scheduled file sweeps prune uploaded resources older than 15 minutes.
- **Security Sanitization:** Custom UUID hashing blocks parameter tampering or directories lookup vulnerabilities during request resolution.
