# TerraSynapse – Docker/Compose

## Subir tudo
```bash
cd ops/docker
cp .env.example .env   # edite TS_SECRETS_KEY
docker compose up --build -d
```
Back-end: http://localhost:8000  
Painéis: 8501..8504 (ou via Nginx em /admin/*).

## Volumes persistentes (opcional)
Adicione às services:
```yaml
    volumes:
      - ../../config:/app/config
      - ../../data:/app/data
```

## Atualizar
```bash
docker compose build backend st_usuarios st_isoxml_vendor st_isoxml_presets st_summaries
docker compose up -d
```