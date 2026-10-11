import pathlib
import re

PROJECT_ROOT = pathlib.Path(__file__).parents[1]

COMMENT_PATTERNS = {
    ".py": re.compile(r"^[ \t]*#.*$"),
    ".yml": re.compile(r"^[ \t]*#.*$"),
    ".yaml": re.compile(r"^[ \t]*#.*$"),
    ".md": re.compile(r"^[ \t]*#.*$"),
    ".html": re.compile(r"<!--.*?-->", re.DOTALL),
    ".css": re.compile(r"/\*.*?\*/", re.DOTALL),
    ".js": re.compile(r"//.*?$|/\*.*?\*/", re.MULTILINE | re.DOTALL),
    ".sh": re.compile(r"^[ \t]*#.*$"),
    ".gitignore": re.compile(r"^[ \t]*#.*$"),
}

def strip_comments_from_file(path: pathlib.Path):
    ext = path.suffix.lower()
    pattern = COMMENT_PATTERNS.get(ext)
    if not pattern:
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return False
    original = text
    if ext in {".html", ".css", ".js"}:
        cleaned = pattern.sub("", text)
        cleaned = "\n".join([line.rstrip() for line in cleaned.splitlines() if line.strip() != ""]) + "\n"
    else:
        cleaned_lines = []
        for line in text.splitlines():
            if not pattern.match(line):
                cleaned_lines.append(line)
        cleaned = "\n".join(cleaned_lines) + "\n"
    if cleaned != original:
        path.write_text(cleaned, encoding="utf-8")
        return True
    return False

if __name__ == "__main__":
    changed = []
    for path in PROJECT_ROOT.rglob("*.*"):
        if path.is_file() and path.suffix.lower() in COMMENT_PATTERNS:
            if strip_comments_from_file(path):
                changed.append(str(path))
    print(f"Removed comments from {len(changed)} files.")
    for p in changed:
        print(p)
