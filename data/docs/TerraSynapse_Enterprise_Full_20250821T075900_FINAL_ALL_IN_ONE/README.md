# TerraSynapse Enterprise – Build FINAL

## Requisitos
- Python 3.10+
- `pip install -r requirements.txt`

## Inicialização
```bash
export TS_SECRETS_KEY=$(python - <<'PY'
from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())
PY)
uvicorn backend.app:app --reload --port 8000
# Interface multipáginas (execute qualquer uma)
streamlit run pages/04_Gerenciar_Usuarios.py
```

## Usuário Desenvolvedor (pré-criado)
- E-mail: `dev@terrasynapse.local`
- Senha: **Defina pelo painel** (crie o usuário com sua senha; a role já está `developer`).

Para dar acesso total a outro e-mail, use `pages/04_Gerenciar_Usuarios.py`.

## Endpoints úteis
- `/auth/password/create`, `/auth/password/login`, `/auth/role`
- `/ingest/gps/row` (POST), `/ingest/gps/bulk` (POST) – logs CSV em `data/gps/logs.csv`
- `/voice/tts` – gera `static/audio/tts.wav`
- `/weather/now` – clima (simulado se sem API key)
- ISOXML: `/isoxml/vendor/*` + páginas 26–28
- SSO OIDC/SAML2: páginas 06, 06b, 06c
- Agendador: `pages/44_Scheduler_Summaries.py`

## Heatmap GPS
- Envie pontos via `/ingest/gps/bulk` e abra `pages/21_GPS_Heatmap.py`.

## Voz Offline
- `pages/03_Config_Voz.py` (TTS ativado).

## Clima
- Configure `config/providers/clima.json` com sua chave. Sem chave → modo simulado.

Boa safra! 🌾