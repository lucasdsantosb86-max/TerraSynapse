# Checklist de Produção – TerraSynapse Enterprise

## 1) Sistema e OS
- [ ] Ubuntu 22.04/24.04 LTS atualizado (`unattended-upgrades`).
- [ ] Usuário de serviço `terrasynapse` (sem sudo).
- [ ] Firewall: permitir 80/443; backend interno em 127.0.0.1:8000; Streamlit 127.0.0.1:8501..
- [ ] Relógio NTP sincronizado.

## 2) Python/Runtime
- [ ] Python 3.10+; `virtualenv` em `/opt/terrasynapse/.venv`.
- [ ] `pip install -r requirements.txt` sem warnings críticos.
- [ ] `TS_SECRETS_KEY` configurada (**obrigatório**).

## 3) Secrets/Config
- [ ] `config/providers/clima.json` com chaves (ClimaTempo/OWM) se usar clima real.
- [ ] `config/branding.json` com cores/logos por domínio.
- [ ] SMTP configurado (envio PDF/CSV + alertas).
- [ ] SSO (OIDC/SAML2) configurado e testado; `auth_role_mapping.json` revisado.

## 4) Web/Proxy (Nginx)
- [ ] Proxy reverso para backend (`/api/ → 127.0.0.1:8000`).
- [ ] Subpaths para painéis Streamlit (ou subdomínios), com `proxy_set_header` corretos.
- [ ] TLS (Let's Encrypt) e `HSTS` habilitado.

## 5) Systemd/Serviços
- [ ] `terrasynapse-backend.service` ativo (Restart=always).
- [ ] Unidades Streamlit ativas (conforme sua escolha).
- [ ] `journalctl -u ...` sem erros; logrotate configurado.

## 6) Banco/Arquivos
- [ ] Backups diários de `config/` e `data/` (retention ≥ 30 dias).
- [ ] Permissões mínimas (UMASK 027).

## 7) Segurança (LGPD/LGPD-like)
- [ ] Força de senha (mínimo 12 chars + complexidade).
- [ ] Expiração de senha (90d) se aplicável.
- [ ] Rate-limit e proteção CSRF no proxy.
- [ ] CORS restrito ao seu domínio.

## 8) Observabilidade
- [ ] Health-check no Nginx (`/api/health`).
- [ ] Alertas de cron (se `summaries_tick` falhar).
- [ ] Métricas básicas (latência, 5xx).

## 9) DR/Incidentes
- [ ] Script de restauração testado.
- [ ] Procedimento de rotação de chaves (TS_SECRETS_KEY, SMTP, APIs).
- [ ] Registro de incidentes e contatos.

---

## Anexos (exemplos prontos em `ops/`)
- `nginx.conf` – Proxy + TLS
- `terrasynapse-backend.service` – Uvicorn
- `streamlit-*.service` – painéis
- `logrotate-terrasynapse` – rotação de logs
