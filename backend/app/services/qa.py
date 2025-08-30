import os, glob, re
from typing import List, Tuple
from pathlib import Path

def _read_text_from_docs(patterns: List[str]) -> List[Tuple[str, str]]:
    texts = []
    for p in patterns:
        for f in glob.glob(p, recursive=True):
            if os.path.isfile(f):
                low = f.lower()
                try:
                    if low.endswith((".txt", ".md")):
                        with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                            texts.append((f, fh.read()))
                    elif low.endswith(".pdf"):
                        from pypdf import PdfReader
                        text_buf = []
                        reader = PdfReader(f)
                        for page in reader.pages:
                            try:
                                text_buf.append(page.extract_text() or "")
                            except Exception:
                                pass
                        texts.append((f, "\n".join(text_buf)))
                except Exception:
                    pass
    return texts

def _simple_score(q: str, text: str) -> float:
    q_terms = [t for t in re.findall(r"\w+", q.lower()) if len(t) > 2]
    t_terms = re.findall(r"\w+", text.lower())
    if not q_terms: return 0.0
    hits = sum(t_terms.count(t) for t in q_terms)
    return hits / (len(t_terms) + 1e-9)

def answer_question_by_document(question: str, doc_paths: List[str] = None, top_k: int = 5):
    repo_root = Path(__file__).resolve().parents[3]

    if doc_paths:
        patterns = doc_paths
        docs = _read_text_from_docs(patterns)
    else:
        data_globs = [
            str(repo_root / "data" / "docs" / "**" / "*.md"),
            str(repo_root / "data" / "docs" / "**" / "*.txt"),
            str(repo_root / "data" / "docs" / "**" / "*.pdf"),
        ]
        docs = _read_text_from_docs(data_globs)

        # Fallback apenas se data/docs estiver vazio
        if not docs:
            sample_globs = [str(repo_root / "shared" / "sample_data" / "docs" / "*.md")]
            docs = _read_text_from_docs(sample_globs)

    if not docs:
        return ("Nenhum documento encontrado. Envie arquivos ou informe um padrão como data/docs/**/*.md.", [])

    scored = [(fp, _simple_score(question, txt), txt) for fp, txt in docs]
    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:max(1, top_k)]

    best_file, best_score, best_txt = top[0]
    snippet = best_txt[:700].replace("\n", " ")
    answer = f"Melhor fonte: {os.path.basename(best_file)} | Score={best_score:.3f}. Trecho: {snippet} ..."
    sources = [f for f,_,_ in top]
    return answer, sources
