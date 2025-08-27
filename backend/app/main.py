import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from io import BytesIO
from PIL import Image
import numpy as np
import base64

from .services.qa import answer_question_by_document
from .services.exg import compute_exg
from .services.pdf import build_simple_pdf

def _parse_allowed_origins():
    raw = os.environ.get("ALLOWED_ORIGINS", "")
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    # fallback seguro (se env faltar)
    if not origins:
        origins = [
            "https://app.terrasynapse.com",
            "https://terrasynapse-app-3sja.onrender.com",
        ]
    return origins

app = FastAPI(title="TerraSynapse API", version="1.0.0")

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
