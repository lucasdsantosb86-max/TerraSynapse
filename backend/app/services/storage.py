from __future__ import annotations
import os, re, json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
from fastapi import UploadFile

SAFE_DIR = re.compile(r"[^a-z0-9_\-]", re.I)

def _safe_name(name: str) -> str:
    # mantém extensão, saneando o nome
    p = Path(name)
    base = SAFE_DIR.sub("_", p.stem)
    ext  = SAFE_DIR.sub("", p.suffix)  # mantém o ponto
    return (base or "arquivo") + ext

def _safe_dir(name: Optional[str]) -> str:
    if not name: return "_inbox"
    name = SAFE_DIR.sub("_", name.strip())
    return name or "_inbox"

def save_upload(root: Path, file: UploadFile, library: Optional[str]) -> Tuple[Path, int]:
    lib = _safe_dir(library)
    today = datetime.utcnow()
    dst_dir = root / "data" / "docs" / lib / f"{today:%Y}" / f"{today:%m}"
    dst_dir.mkdir(parents=True, exist_ok=True)

    filename = _safe_name(file.filename or "arquivo")
    dst_path = dst_dir / filename

    size = 0
    with dst_path.open("wb") as out:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk: break
            out.write(chunk)
            size += len(chunk)

    # grava índice
    idx = {
        "filename": filename,
        "path": str(dst_path.relative_to(root)),
        "size": size,
        "mime": file.content_type or "",
        "library": lib,
        "uploaded_at": today.isoformat()+"Z",
    }
    index_dir = root / "data" / "docs" / "_index"
    index_dir.mkdir(parents=True, exist_ok=True)
    with (index_dir / "docs.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(idx, ensure_ascii=False) + "\n")

    return dst_path, size
