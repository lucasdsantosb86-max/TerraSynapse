
# TerraSynapse IA — Roteiro de Vídeo de Demonstração
Data: 2025-08-21 12:51 UTC

## Cena 1 — Login e Configurações
1. Abra `streamlit run pages/00_Login.py`
2. Login com **dev_terrasynapse / TS!Dev2025** (depois altere).
3. Mostre a engrenagem ⚙ e confirme idioma/PT-BR.

## Cena 2 — Curadoria Premium
1. Abra `streamlit run pages/03_Admin_Curadoria.py`
2. Clique **Ingerir todos os lotes agora**.
3. Mostre a confirmação de `Indexados: N`.

## Cena 3 — Planejamento de Talhão
1. Abra `streamlit run pages/14_Planejamento_de_Talhao.py`
2. Carregue um GeoTIFF (ou imagem RGB de teste).
3. Mostre **área útil (ha)**, **insumos** e **Economia (R$)**.
4. Clique em **Exportar laudo** (gera JSON de laudo).

## Cena 4 — Upload fácil de novos snippets
1. Abra `streamlit run pages/04_Admin_Upload_Snippets.py`
2. Faça upload de um `.jsonl` novo e clique **Ingerir todos agora**.

## Cena 5 — GPS Heatmap (métricas)
1. Envie um JSONL real via `POST /ingest/gps`.
2. Abra `GET /gps/metrics?date=YYYY-MM-DD` e mostre km/dia.

**Dica de gravação**: use OBS Studio (perfil 1920x1080@30fps). Captura de janela do navegador + microfone.
