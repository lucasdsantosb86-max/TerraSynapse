import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from io import BytesIO
from PIL import Image
import numpy as np
import base64

from .services.qa import answer_question_by_document
from .services import chat
from .services.exg import compute_exg
from .services.pdf import build_simple_pdf

def _parse_allowed_origins():
    raw = os.environ.get("ALLOWED_ORIGINS", "")
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    if not origins:
        origins = [
            "https://app.terrasynapse.com",
        ]
    return origins

app = FastAPI(title="TerraSynapse API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QARequest(BaseModel):
    question: str
    doc_paths: Optional[List[str]] = None
    top_k: int = 5

class QAResponse(BaseModel):
    answer: str
    sources: List[str]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/qa", response_model=QAResponse)
def qa(req: QARequest):
    answer, sources = answer_question_by_document(
        question=req.question,
        doc_paths=req.doc_paths,
        top_k=req.top_k
    )
    return QAResponse(answer=answer, sources=sources)

@app.post("/exg")
async def exg(file: UploadFile = File(...)):
    try:
        img_bytes = await file.read()
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        exg_map, exg_mean = compute_exg(np.array(img))
        preview = Image.fromarray((255*(exg_map - exg_map.min())/(exg_map.ptp()+1e-9)).astype(np.uint8))
        buf = BytesIO(); preview.save(buf, format="PNG")
        preview_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return {"exg_mean": float(exg_mean), "preview_png_base64": preview_b64}
    except Exception as e:
        raise HTTPException(400, f"Erro no EXG: {e}")

@app.post("/pdf")
async def pdf_report(title: str = Form(...), body: str = Form(...)):
    pdf_bytes = build_simple_pdf(title, body)
    b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    return {"pdf_base64": b64, "filename": "relatorio_terrasynapse.pdf"}

@app.post("/upload_doc")
async def upload_doc(file: UploadFile = File(...)):
    # aceita .md, .txt, .pdf e grava em repo_root/data/docs
    ext = Path(file.filename).suffix.lower()
    if ext not in (".md", ".txt", ".pdf"):
        raise HTTPException(400, "Formato não suportado. Use .md, .txt ou .pdf")
    try:
        repo_root = Path(__file__).resolve().parents[2]  # .../backend
        docs_dir = repo_root.parent / "data" / "docs" if (repo_root.name == "backend") else repo_root / "data" / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        safe_name = Path(file.filename).name.replace("..","_")
        dest = docs_dir / safe_name
        content = await file.read()
        with open(dest, "wb") as f:
            f.write(content)
        return {"saved": str(dest)}
    except Exception as e:
        raise HTTPException(500, f"Falha ao salvar: {e}")


from typing import Optional
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list
    doc_paths: Optional[list] = None
    top_k: int = 4

class ChatResponse(BaseModel):
    assistant: str
    sources: list

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    try:
        assistant, sources = chat.answer_chat(req.messages, req.doc_paths, top_k=req.top_k)
        return ChatResponse(assistant=assistant, sources=sources)
    except Exception as e:
        raise HTTPException(400, f"Erro no chat: {e}")

