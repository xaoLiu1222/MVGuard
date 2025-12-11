import os
import shutil
from pathlib import Path
from config import SUPPORTED_FORMATS


def ensure_dir(path: str) -> Path:
    """Ensure directory exists."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_video_files(path: str) -> list[Path]:
    """Get all video files from path (file or directory)."""
    p = Path(path)
    if p.is_file() and p.suffix.lower() in SUPPORTED_FORMATS:
        return [p]
    if p.is_dir():
        files = []
        for fmt in SUPPORTED_FORMATS:
            files.extend(p.glob(f"*{fmt}"))
            files.extend(p.glob(f"*{fmt.upper()}"))
        return sorted(files)
    return []


def move_file(src: str, dest_dir: str) -> str:
    """Move file to destination directory."""
    src_path = Path(src)
    if not src_path.exists():
        return ""

    ensure_dir(dest_dir)
    dest_path = Path(dest_dir) / src_path.name

    # Handle duplicate names
    counter = 1
    while dest_path.exists():
        dest_path = Path(dest_dir) / f"{src_path.stem}_{counter}{src_path.suffix}"
        counter += 1

    shutil.move(src_path, dest_path)
    return str(dest_path)
