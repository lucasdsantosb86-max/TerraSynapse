import os
import base64
from io import BytesIO
from pathlib import Path

import requests
import streamlit as st
from PIL import Image

API_URL = os.environ.get("API_URL", "http://localhost:8000")
LOGO_PATH = Path(__file__).parent / "assets" / "logo.png"

PAGE_ICON = ""
if LOGO_PATH.exists():
    try:
        PAGE_ICON = Image.open(LOGO_PATH)
    except Exception:
        PAGE_ICON = ""

st.set_page_config(
    page_title="TerraSynapse",
    page_icon=PAGE_ICON,
    layout="wide",
)

# ---------- CSS global ----------
st.markdown("""
<style>
:root{
  --ts-bg:#29291F;
  --ts-bg-2:#403F2B;
  --ts-ink:#CFCBC0;
  --ts-ink-soft:#9F9D8E;
  --ts-accent:#F3F1C4;
  --ts-line:#706E5D;
}
header[data-testid="stHeader"] { display:none !important; }
div[data-testid="stToolbar"] { display:none !important; }
#MainMenu, footer { visibility:hidden; height:0; }

.block-container { padding-top: 0.9rem !important; padding-bottom: 1.0rem; }

.ts-brand { display:flex; align-items:center; gap:.8rem; margin:.10rem 0 .15rem 0; }
.ts-logo { width:46px; height:46px; object-fit:contain; border-radius:8px; display:block; }
.ts-title { font-weight:800; font-size:1.30rem; line-height:1.1; margin:0; padding:0; }
.ts-tagline { color:var(--ts-ink-soft); margin-top:.10rem; font-size:.96rem; }
.ts-rule { height:1px; background: var(--ts-line); opacity:.35; margin:.55rem 0 1.05rem 0; }

.stTextInput > div > div, .stTextArea > div > div { background:#403F2B; border:1px solid #706E5D; border-radius:.75rem; }
.stTextInput > div > div:focus-within, .stTextArea > div > div:focus-within { box-shadow:0 0 0 2px rgba(243,241,196,.35); }
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color:#9F9D8E; opacity:.95; }

.stSelectbox > div > div { background:#403F2B; border:1px solid #706E5D; border-radius:.75rem; }
.stSelectbox [data-baseweb="select"] [role="combobox"] { color:#CFCBC0; }

.stSlider [data-baseweb="slider"] > div > div { background:#403F2B; }
.stSlider [role="slider"] { background:#F3F1C4; }

.stDownloadButton > button, .stButton > button {
  background:#F3F1C4; color:#1b1b1b; border:0; border-radius:.8rem;
  padding:.55rem 1.05rem; font-weight:700;
}
.stDownloadButton > button:disabled, .stButton > button:disabled {
  filter:grayscale(.5) brightness(.85); opacity:.75; cursor:not-allowed;
}
.stDownloadButton > button:hover:not(:disabled), .stButton > button:hover:not(:disabled) { filter:brightness(.96); }

[data-testid="stFileUploader"] > div:first-child { background:#403F2B; border:1px dashed #706E5D; border-radius:.8rem; }

.stTabs [data-baseweb="tab-list"] { gap:.5rem; }
.stTabs [data-baseweb="tab"]{ background:var(--ts-bg-2); color:var(--ts-ink); border-radius:.75rem; padding:.35rem .9rem; }
.stTabs [aria-selected="true"]{ background:var(--ts-line); color:var(--ts-accent); font-weight:800; }

/* Badge "em breve" por CSS na 4ª aba */
.stTabs [data-baseweb="tab-list"] [data-baseweb="tab"]:nth-child(4){ position: relative; }
.stTabs [data-baseweb="tab-list"] [data-baseweb="tab"]:nth-child(4)::after{
  content: "em breve"; display:inline-block; margin-left:.45rem; padding:.05rem .40rem;
  border-radius:.50rem; background:#706E5D; color:#F3F1C4; font-size:.80rem; font-weight:700;
}

.ts-source { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size:.9rem; color:var(--ts-ink); opacity:.9; }

@media (max-width: 640px){
  .block-container { padding-top: .6rem !important; }
  .ts-logo { width:40px; height:40px; }
  .ts-title { font-size:1.18rem; }
}
</style>
""", unsafe_allow_html=True)

# Favicon dedicado
try:
    if LOGO_PATH.exists():
        _b64fav = base64.b64encode(open(LOGO_PATH, "rb").read()).decode("utf-8")
        st.markdown(f"<link rel='icon' type='image/png' href='data:image/png;base64,{_b64fav}'>", unsafe_allow_html=True)
except Exception:
    pass

# Branding
def render_brand():
    if LOGO_PATH.exists():
        try:
            b64 = base64.b64encode(open(LOGO_PATH, "rb").read()).decode("utf-8")
            logo_html = f'<img class="ts-logo" src="data:image/png;base64,{b64}" alt="TerraSynapse logo" />'
        except Exception:
            logo_html = '<span class="ts-logo"></span>'
    else:
        logo_html = '<span class="ts-logo"></span>'

    st.markdown(
        f"""
        <div class="ts-brand">
          {logo_html}
          <div>
            <div class="ts-title">TerraSynapse</div>
            <div class="ts-tagline">Plataforma de IA para o agronegócio  QA por documento, ExG e Laudo PDF.</div>
          </div>
        </div>
        <div class="ts-rule"></div>
        """,
        unsafe_allow_html=True
    )

render_brand()

# Abas
tabs = st.tabs(["Buscar respostas", "ExG", "Laudo PDF", "Clima"])

# === Estado de chat ===
if 'chat_messages' not in st.session_state:
    st.session_state['chat_messages'] = []

# ===================== TAB 1: Chat =====================
with tabs[0]:
    st.subheader("Chat  TerraSynapse (RAG)")

    with st.expander(" Enviar documentos", expanded=False):
        uploads = library = st.selectbox('Biblioteca', ['_inbox (padrão)','manuals','agronomy','exg','operations','vendor','faq','_archive'], index=0)\n\nst.file_uploader("Arquivos (.md, .txt, .pdf)", type=["md","txt","pdf"], accept_multiple_files=True)
        if uploads and st.button("Enviar para a IA"):
            ok, fail = 0, 0
            for f in uploads:
                try:
                    files = {"file": (f.name, f.getvalue(), f"type")}
                    r = requests.post(f"{API_URL}/upload_doc", files=files, timeout=120)
                    ok += 1 if r.ok else 0
                    fail += 0 if r.ok else 1
                except Exception:
                    fail += 1
            if ok and not fail:
                st.success(f"{ok} arquivo(s) enviado(s) com sucesso.")
            else:
                st.warning(f"Uploads concluídos. Sucesso: {ok}  Falhas: {fail}")

    c1, c2 = st.columns([2,1])
    with c1:
        custom_glob = st.text_input("Padrão de documentos (opcional)", value="", placeholder="Ex.: data/docs/TerraSynapse_OPS_*/**/*.md")
    with c2:
        top_k = st.slider("Top K fontes", 1, 10, 4)

    # histórico
    for m in st.session_state['chat_messages']:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Digite sua pergunta e pressione Enter")
    if prompt:
        st.session_state['chat_messages'].append({"role":"user","content":prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            payload = {
                "messages": st.session_state['chat_messages'],
                "doc_paths": [custom_glob] if custom_glob.strip() else None,
                "top_k": int(top_k),
            }
            r = requests.post(f"{API_URL}/chat", json=payload, timeout=120)
            if r.ok:
                data = r.json()
                assistant = data.get("assistant","(sem resposta)")
                sources = data.get("sources",[]) or []
                st.session_state['chat_messages'].append({"role":"assistant","content":assistant})
                with st.chat_message("assistant"):
                    st.markdown(assistant)
                    if sources:
                        with st.expander("Fontes utilizadas"):
                            for s in sources:
                                st.markdown(f"- `{s}`")
            else:
                err = r.text
                st.session_state['chat_messages'].append({"role":"assistant","content":f"Erro da API: {err}"})
                with st.chat_message("assistant"):
                    st.error(err)
        except Exception as e:
            st.session_state['chat_messages'].append({"role":"assistant","content":f"Erro: {e}"})
            with st.chat_message("assistant"):
                st.error(f"Erro: {e}")

    if st.button(" Resetar conversa"):
        st.session_state['chat_messages'] = []
        st.experimental_rerun()

# ===================== TAB 2: ExG =====================
with tabs[1]:
    st.subheader("Índice de Vegetação ExG")
    img = library = st.selectbox('Biblioteca', ['_inbox (padrão)','manuals','agronomy','exg','operations','vendor','faq','_archive'], index=0)\n\nst.file_uploader("Imagem RGB", type=["jpg","jpeg","png"], key="exg_upl")
    if img and st.button("Calcular ExG"):
        try:
            files = {"file": (img.name, img.getvalue(), img.type)}
            r = requests.post(f"{API_URL}/exg", files=files, timeout=120)
            if r.ok:
                data = r.json()
                st.metric("ExG médio", f"{data.get('exg_mean', 0):.4f}")
                b64 = data.get("preview_png_base64", "")
                if b64:
                    st.image(BytesIO(base64.b64decode(b64)), caption="Preview ExG")
            else:
                st.error(r.text)
        except Exception as e:
            st.error(f"Erro ao processar imagem: {e}")

# ===================== TAB 3: Laudo PDF =====================
with tabs[2]:
    st.subheader("Gerar Laudo PDF")
    title = st.text_input("Título", "Laudo TerraSynapse")
    body = st.text_area("Conteúdo", "Resultados e observações... (cole aqui)")

    if st.button("Gerar PDF"):
        try:
            r = requests.post(f"{API_URL}/pdf", data={"title": title, "body": body}, timeout=120)
            if r.ok:
                data = r.json()
                b = base64.b64decode(data["pdf_base64"])
                st.download_button("Baixar PDF", b, file_name=data.get("filename", "laudo.pdf"),
                                   mime="application/pdf")
            else:
                st.error(r.text)
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")

# ===================== TAB 4: Clima (placeholder) =====================
with tabs[3]:
    st.info("Módulo de clima será integrado em breve (dados públicos + alertas).")


