from __future__ import annotations

import re
from typing import List

from src.core.models import DocumentChunk

try:
    import faiss  # type: ignore
    import numpy as np
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except Exception:
    faiss = None
    np = None
    SentenceTransformer = None
    EMBEDDINGS_AVAILABLE = False


class VectorKnowledgeBase:
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2") -> None:
        self.docs: List[DocumentChunk] = []
        self.index = None
        self.model = None
        self.matrix = None
        if EMBEDDINGS_AVAILABLE:
            self.model = SentenceTransformer(embedding_model)

    def add_documents(self, docs: List[DocumentChunk]) -> None:
        self.docs.extend(docs)
        if not self.docs:
            return
        if EMBEDDINGS_AVAILABLE and self.model is not None:
            embeddings = self.model.encode([d.text for d in self.docs], normalize_embeddings=True)
            self.matrix = np.array(embeddings).astype("float32")
            self.index = faiss.IndexFlatIP(self.matrix.shape[1])
            self.index.add(self.matrix)

    def search(self, query: str, top_k: int = 3) -> List[DocumentChunk]:
        if not self.docs:
            return []

        if EMBEDDINGS_AVAILABLE and self.index is not None and self.model is not None:
            q = self.model.encode([query], normalize_embeddings=True)
            q = np.array(q).astype("float32")
            scores, idxs = self.index.search(q, min(top_k, len(self.docs)))
            return [self.docs[i] for i in idxs[0] if i >= 0]

        query_terms = set(re.findall(r"\w+", query.lower()))
        scored = []
        for doc in self.docs:
            doc_terms = set(re.findall(r"\w+", doc.text.lower()))
            scored.append((len(query_terms & doc_terms), doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored[:top_k] if score > 0] or self.docs[:1]
