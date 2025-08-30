import os, re, glob, json
from typing import List, Tuple, Optional
from pathlib import Path
from pypdf import PdfReader

def _read_text_one(fp: str) -> str:
    low = fp.lower()
    try:
        if low.endswith((".md",".txt")):
            return Path(fp).read_text(encoding="utf-8", errors="ignore")
        if low.endswith(".pdf"):
            buf = []
            reader = PdfReader(fp)
            for p in reader.pages:
                try:
                    buf.append(p.extract_text() or "")
                except Exception:
                    pass
            return "\n".join(buf)
    except Exception:
        return ""
    return ""

def _read_text_globs(patterns: List[str]) -> List[Tuple[str,str]]:
    out = []
    for pat in patterns:
        for fp in glob.glob(pat, recursive=True):
            if os.path.isfile(fp):
                txt = _read_text_one(fp)
                if txt:
                    out.append((fp, txt))
    return out

def _simple_score(q: str, text: str) -> float:
    q_terms = [t for t in re.findall(r"\w+", q.lower()) if len(t) > 2]
    t_terms = re.findall(r"\w+", text.lower())
    if not q_terms:
        return 0.0
    hits = sum(t_terms.count(t) for t in q_terms)
    return hits / (len(t_terms) + 1e-9)

def retrieve_context(question: str, doc_paths: Optional[List[str]], top_k: int = 4, max_chars: int = 6000):
    repo_root = Path(__file__).resolve().parents[3]
    if doc_paths:
        pats = doc_paths
    else:
        pats = [
            str(repo_root / "data" / "docs" / "**" / "*.md"),
            str(repo_root / "data" / "docs" / "**" / "*.txt"),
            str(repo_root / "data" / "docs" / "**" / "*.pdf"),
            str(repo_root / "shared" / "sample_data" / "docs" / "*.md"),
        ]
    docs = _read_text_globs(pats)
    if not docs:
        return "", []

    scored = []
    for fp, txt in docs:
        scored.append((fp, _simple_score(question, txt), txt))
    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:max(1, top_k)]

    sources = [fp for fp,_,_ in top]
    ctx_parts, total = [], 0
    for fp, score, txt in top:
        cut = txt[:2000]
        ctx_parts.append(f"\n### {Path(fp).name}\n{cut}\n")
        total += len(cut)
        if total >= max_chars:
            break
    return "\n".join(ctx_parts), sources

def call_llm_openai(messages: list, system_prompt: str, api_key: str, model: str = None, temperature: float = 0.3) -> str:
    import requests
    url = "https://api.openai.com/v1/chat/completions"
    mdl = model or os.environ.get("LLM_MODEL","gpt-4o-mini")
    payload = {
        "model": mdl,
        "temperature": temperature,
        "messages": [{"role":"system","content": system_prompt}] + messages
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()

def answer_chat(messages: List[dict], doc_paths: Optional[List[str]], top_k: int = 4) -> Tuple[str, List[str]]:
    user_utterances = [m["content"] for m in messages if m.get("role") == "user"]
    question = user_utterances[-1] if user_utterances else ""
    context, sources = retrieve_context(question, doc_paths, top_k=top_k, max_chars=6000)

    system_prompt = (
        "Você é a IA TerraSynapse. Responda EM PORTUGUÊS DO BRASIL de forma concisa, "
        "citando fatos APENAS do CONTEXTO quando pertinente. Se algo não estiver no contexto, "
        "explique brevemente que não há dados suficientes e sugira pedir mais detalhes. "
        "Mantenha tom profissional e objetivo."
        "\n\n=== CONTEXTO ===\n"
        f"{context}\n"
        "=== FIM DO CONTEXTO ===\n"
    )

    api_key = os.environ.get("OPENAI_API_KEY","").strip()
    model = os.environ.get("LLM_MODEL","gpt-4o-mini")
    if api_key:
        try:
            return call_llm_openai(messages, system_prompt, api_key, model=model), sources
        except Exception:
            pass

    if context.strip():
        safe = context[:800].replace("\n"," ")
        return (f"(Sem LLM) Com base nas fontes, aqui vai um resumo: {safe} ...", sources)
    else:
        return ("(Sem LLM) Não encontrei contexto suficiente nos documentos. "
                "Envie mais arquivos ou refine o padrão de documentos.", sources)
