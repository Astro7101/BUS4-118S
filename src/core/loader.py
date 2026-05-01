from __future__ import annotations

from pathlib import Path
from typing import List

from src.core.models import DocumentChunk


def load_txt_documents(data_dir: str) -> List[DocumentChunk]:
    docs: List[DocumentChunk] = []
    root = Path(data_dir)
    for path in sorted(root.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        for idx, block in enumerate([b.strip() for b in text.split("\n\n") if b.strip()]):
            docs.append(DocumentChunk(text=block, metadata={"source": path.name, "chunk": idx}))
    return docs
