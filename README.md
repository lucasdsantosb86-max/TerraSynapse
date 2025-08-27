# TerraSynapse Enterprise (MVP Online)
Backend: FastAPI (/health, /qa, /exg, /pdf)
Frontend: Streamlit (QA por documento, ExG, PDF)
Deploy: Render (2 serviços) + domínios (GoDaddy) + Wix no www/raiz

## Rodar local (dev)
python -m venv .venv && .\.venv\Scripts\activate
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
# terminal 1 (API)
uvicorn backend.app.main:app --reload
# terminal 2 (APP)
$env:API_URL="http://localhost:8000"; streamlit run frontend/streamlit_app.py

## Deploy Render
- Use render.yaml como Blueprint e crie os 2 serviços.
- Depois aponte api. e app. no GoDaddy (CNAME) e use Wix no www/raiz.
