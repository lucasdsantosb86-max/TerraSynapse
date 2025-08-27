import os, glob, re
from typing import List, Tuple
from pathlib import Path

def _read_text_from_docs(doc_paths: List[str]) -> List[Tuple[str, str]]:
    texts = []
    for p in doc_paths:
        for f in glob.glob(p, recursive=True):
            if os.path.isfile(f) and f.lower().endswith((".txt", ".md")):
                with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                    texts.append((f, fh.read()))
    return texts

def _simple_score(q: str, text: str) -> float:
    q_terms = [t for t in re.findall(r"\w+", q.lower()) if len(t) > 2]
    t_terms = re.findall(r"\w+", text.lower())
    if not q_terms: return 0.0
    hits = sum(t_terms.count(t) for t in q_terms)
    return hits / (len(t_terms) + 1e-9)

def answer_question_by_document(question: str, doc_paths: List[str] = None, top_k: int = 5):
    if not doc_paths:
        base = Path(__file__).resolve().parents[2] / "shared" / "sample_data" / "docs"
        doc_paths = [str(base / "*.md")]

    docs = _read_text_from_docs(doc_paths)
    if not docs:
        return ("Nenhum documento encontrado.", [])

    scored = []
    for fp, txt in docs:
        scored.append((fp, _simple_score(question, txt), txt))
    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:top_k]

    best_file, best_score, best_txt = top[0]
    snippet = best_txt[:600].replace("\n", " ")
    answer = f"Melhor fonte: {os.path.basename(best_file)} | Score={best_score:.3f}. Trecho: {snippet} ..."
    sources = [f for f,_,_ in top]
    return answer, sources
