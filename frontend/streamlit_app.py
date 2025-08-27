import os, requests, streamlit as st
from io import BytesIO
import base64, pandas as pd

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="TerraSynapse", layout="wide")
st.title("🌱 TerraSynapse — Demo Enterprise")

with st.sidebar:
    st.markdown("### Módulos")
    opt = st.radio("Escolha:", ["QA por documento", "ExG (Índice de Vegetação)", "Gerar PDF"])

if opt == "QA por documento":
    st.subheader("Perguntas por documento (TF-IDF simples)")
    q = st.text_input("Pergunta")
    default_glob = st.text_input("Padrão de documentos (glob)", "shared/sample_data/docs/*.md")
    top_k = st.slider("Top K", 1, 10, 5)
    if st.button("Responder"):
        payload = {"question": q, "doc_paths": [default_glob], "top_k": top_k}
        r = requests.post(f"{API_URL}/qa", json=payload, timeout=60)
        if r.ok:
            data = r.json()
            st.success(data["answer"])
            st.write("Fontes:")
            st.write(data["sources"])
        else:
            st.error(r.text)

elif opt == "ExG (Índice de Vegetação)":
    st.subheader("Análise ExG (carregue uma imagem RGB)")
    f = st.file_uploader("Imagem", type=["jpg","jpeg","png"])
    if f and st.button("Calcular ExG"):
        files = {"file": (f.name, f.getvalue(), f.type)}
        r = requests.post(f"{API_URL}/exg", files=files, timeout=60)
        if r.ok:
            data = r.json()
            st.metric("ExG médio", f"{data['exg_mean']:.4f}")
            img_b64 = data["preview_png_base64"]
            st.image(BytesIO(base64.b64decode(img_b64)), caption="Preview ExG")
        else:
            st.error(r.text)

else:
    st.subheader("Gerar PDF (laudo simples)")
    title = st.text_input("Título", "Laudo TerraSynapse")
    body = st.text_area("Conteúdo", "Resultados e observações...")
    if st.button("Gerar PDF"):
        r = requests.post(f"{API_URL}/pdf", data={"title": title, "body": body}, timeout=60)
        if r.ok:
            data = r.json()
            b = base64.b64decode(data["pdf_base64"])
            st.download_button("Baixar PDF", b, file_name=data["filename"], mime="application/pdf")
        else:
            st.error(r.text)
