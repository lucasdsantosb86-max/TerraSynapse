import os, requests, streamlit as st
from io import BytesIO
import base64
from pathlib import Path
from PIL import Image

API_URL = os.environ.get("API_URL", "http://localhost:8000")

LOGO_PATH = Path(__file__).parent / "assets" / "logo.png"
PAGE_ICON = "🌱"
if LOGO_PATH.exists():
    try:
        PAGE_ICON = Image.open(LOGO_PATH)
    except Exception:
        PAGE_ICON = "🌱"

st.set_page_config(
    page_title="TerraSynapse",
    page_icon=PAGE_ICON,
    layout="wide"
)

# ======= CSS mínimo só pra acabamento =======
st.markdown("""
<style>
.block-container { padding-top: 3.2rem !important; padding-bottom: 1.0rem; }
.stButton>button { padding:.5rem 1rem; border-radius:.75rem; }
.stTextInput>div>div>input, .stTextArea>div>div>textarea { border-radius:.75rem; }
</style>
""", unsafe_allow_html=True)

# ======= BRANDING (sem HTML complexo) =======
left, right = st.columns([0.06, 0.94])
with left:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=44)
    else:
        st.markdown("🌱", unsafe_allow_html=True)
with right:
    st.markdown("### TerraSynapse")
    st.caption("Plataforma de IA para o agronegócio — QA por documento, ExG e Laudo PDF.")
tabs = st.tabs(["🔎 Buscar respostas", "🌿 ExG", "📝 Laudo PDF", "🌤️ Clima (em breve)"])

# ---------- TAB: Buscar respostas ----------
with tabs[0]:
    st.subheader("Buscar respostas por documento")
    st.write("Envie arquivos de conhecimento (.md, .txt, .pdf) e faça perguntas. Enquanto o banco cresce, o app usa os docs enviados + exemplos.")

    with st.expander("➕ Enviar documentos", expanded=False):
        up = st.file_uploader("Arquivos (.md, .txt, .pdf)", type=["md","txt","pdf"], accept_multiple_files=True)
        if up and st.button("Enviar para a IA"):
            ok_cnt, fail_cnt = 0, 0
            for f in up:
                files = {"file": (f.name, f.getvalue(), f"type")}
                try:
                    r = requests.post(f"{API_URL}/upload_doc", files=files, timeout=120)
                    ok_cnt += 1 if r.ok else 0
                    fail_cnt += 0 if r.ok else 1
                except Exception:
                    fail_cnt += 1
            st.success(f"Uploads concluídos. Sucesso: {ok_cnt} • Falhas: {fail_cnt}")

    q = st.text_input("Sua pergunta", placeholder="Ex.: Como ajustar manejo em período de seca?")
    st.caption("Fontes padrão: docs enviados (data/docs) + exemplos internos. Pode informar um padrão de busca abaixo.")
    custom_glob = st.text_input("Padrão de documentos (opcional)", value="", placeholder="Deixe vazio para usar padrão automático")
    top_k = st.slider("Quantas fontes considerar (Top K)", 1, 10, 5)

    if st.button("Buscar resposta"):
        payload = {"question": q, "doc_paths": [custom_glob] if custom_glob else None, "top_k": top_k}
        r = requests.post(f"{API_URL}/qa", json=payload, timeout=120)
        if r.ok:
            data = r.json()
            st.success("✅ Resposta encontrada:")
            st.write(data["answer"])
            st.write("**Fontes utilizadas:**")
            for s in data["sources"]:
                st.write(f"- {s}")
        else:
            st.error(r.text)

# ---------- TAB: ExG ----------
with tabs[1]:
    st.subheader("Índice de Vegetação ExG")
    f = st.file_uploader("Imagem RGB", type=["jpg","jpeg","png"], key="exg_upl")
    if f and st.button("Calcular ExG"):
        files = {"file": (f.name, f.getvalue(), f.type)}
        r = requests.post(f"{API_URL}/exg", files=files, timeout=120)
        if r.ok:
            data = r.json()
            st.metric("ExG médio", f"{data['exg_mean']:.4f}")
            st.image(BytesIO(base64.b64decode(data["preview_png_base64"])), caption="Preview ExG")
        else:
            st.error(r.text)

# ---------- TAB: Laudo PDF ----------
with tabs[2]:
    st.subheader("Gerar Laudo PDF")
    title = st.text_input("Título", "Laudo TerraSynapse")
    body = st.text_area("Conteúdo", "Resultados e observações... (cole aqui)")

    if st.button("Gerar PDF"):
        r = requests.post(f"{API_URL}/pdf", data={"title": title, "body": body}, timeout=120)
        if r.ok:
            data = r.json()
            b = base64.b64decode(data["pdf_base64"])
            st.download_button("Baixar PDF", b, file_name=data["filename"], mime="application/pdf")
        else:
            st.error(r.text)

# ---------- TAB: Clima (placeholder) ----------
with tabs[3]:
    st.info("Módulo de clima será integrado em breve (dados públicos + alertas).")
