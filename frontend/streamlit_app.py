import os, requests, streamlit as st
from io import BytesIO
import base64

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="TerraSynapse",
    page_icon="🌱",
    layout="wide"
)

# ======= CSS simples para dar acabamento =======
st.markdown("""
<style>
/* centraliza e dá respiro */
.block-container {padding-top: 1.5rem; padding-bottom: 1.5rem;}
/* cards mais suaves */
div[data-testid="stMetricValue"] {font-weight:700;}
/* botões maiores */
.stButton>button {padding: 0.5rem 1rem; border-radius: 0.75rem;}
/* caixas */
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
  border-radius: 0.75rem;
}
</style>
""", unsafe_allow_html=True)

# ======= Header =======
col1, col2 = st.columns([1,3])
with col1:
    st.markdown("### 🌱 TerraSynapse")
with col2:
    st.caption("Plataforma de IA para o agronegócio — QA por documento, ExG e Laudo PDF.")

# ======= Navegação =======
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
                    if r.ok:
                        ok_cnt += 1
                    else:
                        fail_cnt += 1
                except Exception:
                    fail_cnt += 1
            st.success(f"Uploads concluídos. Sucesso: {ok_cnt} • Falhas: {fail_cnt}")

    q = st.text_input("Sua pergunta", placeholder="Ex.: Como ajustar manejo em período de seca?")
    st.caption("Fontes padrão: docs enviados (data/docs) + exemplos internos. Pode informar um padrão de busca avançado abaixo, se quiser.")
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
