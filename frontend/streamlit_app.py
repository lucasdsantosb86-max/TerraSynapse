import os
import base64
from io import BytesIO
from pathlib import Path

import requests
import streamlit as st
from PIL import Image

# ---------- Config ----------
API_URL = os.environ.get("API_URL", "http://localhost:8000")

LOGO_PATH = Path(__file__).parent / "assets" / "logo.png"

# Ícone da aba
PAGE_ICON = "🌱"
if LOGO_PATH.exists():
    try:
        PAGE_ICON = Image.open(LOGO_PATH)
    except Exception:
        PAGE_ICON = "🌱"

st.set_page_config(
    page_title="TerraSynapse",
    page_icon=PAGE_ICON,
    layout="wide",
)

# ---------- CSS global (tema + polimentos) ----------
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

/* Esconde header/toolbar nativos do Streamlit (evita deslocamento e corte) */
header[data-testid="stHeader"] { display:none !important; }
div[data-testid="stToolbar"] { display:none !important; }
#MainMenu, footer { visibility:hidden; height:0; }

/* Espaço geral do conteúdo */
.block-container { padding-top: 1.2rem !important; padding-bottom: 1.0rem; }

/* Header brand (logo + textos) */
.ts-brand {
  display:flex; align-items:center; gap:.8rem;
  margin: .10rem 0 .15rem 0;
}
.ts-logo { width:46px; height:46px; object-fit:contain; border-radius:8px; display:block; }
.ts-title { font-weight:800; font-size:1.30rem; line-height:1.1; margin:0; padding:0; }
.ts-tagline { color:var(--ts-ink-soft); margin-top:.10rem; font-size:.96rem; }
.ts-rule { height:1px; background: var(--ts-line); opacity:.35; margin:.55rem 0 1.05rem 0; }

/* Inputs / Botões */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea { border-radius:.75rem; }
.stButton>button {
  padding:.55rem 1.05rem; border-radius:.8rem; font-weight:700;
  background:var(--ts-accent); color:#1b1b1b; border:0;
}
.stButton>button:hover{ filter:brightness(0.96); }

/* Uploader */
.css-1gulkj5 { border-radius:.8rem; }

/* Tabs com contraste melhor */
.stTabs [data-baseweb="tab-list"] { gap:.5rem; }
.stTabs [data-baseweb="tab"]{
  background:var(--ts-bg-2); color:var(--ts-ink);
  border-radius:.75rem; padding:.35rem .9rem;
}
.stTabs [aria-selected="true"]{
  background:var(--ts-line); color:var(--ts-accent); font-weight:800;
}

/* Slider */
.stSlider [data-baseweb="slider"] div[role="slider"] { box-shadow:none; }

/* Links das fontes */
.ts-source {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size:.9rem; color:var(--ts-ink); opacity:.9;
}

/* Responsivo */
@media (max-width: 640px){
  .ts-logo { width:40px; height:40px; }
  .ts-title { font-size:1.18rem; }
}
</style>
""", unsafe_allow_html=True)

# ---------- Header (HTML flex robusto, sem depender do layout do Streamlit) ----------
def render_brand():
    logo_html = ""
    if LOGO_PATH.exists():
        try:
            b64 = base64.b64encode(open(LOGO_PATH, "rb").read()).decode("utf-8")
            logo_html = f'<img class="ts-logo" src="data:image/png;base64,{b64}" alt="TerraSynapse logo" />'
        except Exception:
            logo_html = '<span class="ts-logo">🌱</span>'
    else:
        logo_html = '<span class="ts-logo">🌱</span>'

    st.markdown(
        f"""
        <div class="ts-brand">
          {logo_html}
          <div>
            <div class="ts-title">TerraSynapse</div>
            <div class="ts-tagline">Plataforma de IA para o agronegócio — QA por documento, ExG e Laudo PDF.</div>
          </div>
        </div>
        <div class="ts-rule"></div>
        """,
        unsafe_allow_html=True
    )

render_brand()

# ---------- Abas ----------
tabs = st.tabs(["🔎 Buscar respostas", "🌿 ExG", "📝 Laudo PDF", "🌤️ Clima (em breve)"])

# ======================================================
# TAB 1 — QA por documento
# ======================================================
with tabs[0]:
    st.subheader("Buscar respostas por documento")

    st.write("Envie arquivos de conhecimento **(.md, .txt, .pdf)** e faça perguntas. "
             "Enquanto o banco cresce, o app usa os docs enviados + exemplos.")

    with st.expander("➕ Enviar documentos", expanded=False):
        uploads = st.file_uploader("Arquivos (.md, .txt, .pdf)", type=["md","txt","pdf"], accept_multiple_files=True)
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
                st.warning(f"Uploads concluídos. Sucesso: {ok} • Falhas: {fail}")

    ask = st.text_input("Sua pergunta", placeholder="Ex.: Como ajustar manejo em período de seca?")
    st.caption("Fontes padrão: docs enviados (`data/docs`) + exemplos internos. "
               "Pode informar um padrão de busca abaixo, se quiser.")
    custom_glob = st.text_input("Padrão de documentos (opcional)", value="", placeholder="Deixe vazio para usar padrão automático")
    top_k = st.slider("Quantas fontes considerar (Top K)", 1, 10, 5)

    if st.button("Buscar resposta"):
        payload = {"question": ask, "doc_paths": [custom_glob] if custom_glob.strip() else None, "top_k": top_k}
        try:
            r = requests.post(f"{API_URL}/qa", json=payload, timeout=120)
            if r.ok:
                data = r.json()
                st.success("✅ Resposta encontrada:")
                st.write(data.get("answer", ""))

                sources = data.get("sources", []) or []
                if sources:
                    st.markdown("**Fontes utilizadas:**")
                    for s in sources:
                        st.markdown(f'<div class="ts-source">• {s}</div>', unsafe_allow_html=True)
                else:
                    st.caption("Nenhuma fonte retornada.")
            else:
                st.error(r.text)
        except Exception as e:
            st.error(f"Erro ao consultar a API: {e}")

# ======================================================
# TAB 2 — Índice ExG
# ======================================================
with tabs[1]:
    st.subheader("Índice de Vegetação ExG")
    img = st.file_uploader("Imagem RGB", type=["jpg","jpeg","png"], key="exg_upl")
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

# ======================================================
# TAB 3 — Laudo PDF
# ======================================================
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

# ======================================================
# TAB 4 — Clima (placeholder)
# ======================================================
with tabs[3]:
    st.info("Módulo de clima será integrado em breve (dados públicos + alertas).")
