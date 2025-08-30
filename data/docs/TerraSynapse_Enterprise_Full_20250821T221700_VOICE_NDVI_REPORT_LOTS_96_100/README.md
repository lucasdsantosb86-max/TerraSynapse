# TerraSynapse IA – Entrega de Módulos (NDVI, Segmentação, GPS Heatmap, Alertas, Voz Offline)

## Como rodar
1) Backend (FastAPI)
```bash
uvicorn backend.app:app --reload --port 8000
```
2) Frontend (Streamlit) – abra as páginas desejadas
```bash
streamlit run pages/05_Home.py
# em outra janela
streamlit run pages/14_Planejamento_de_Talhao.py
streamlit run pages/06_GPS_Heatmap.py
```

## Testes rápidos
- GPS: envie `data/examples/gps_logs.jsonl` via aba *Heatmap* ou:
```bash
curl -F file=@data/examples/gps_logs.jsonl http://localhost:8000/ingest/gps
curl 'http://localhost:8000/gps/metrics'
```
- Alertas (umidade/geada/vento):
```bash
curl -X POST -F 'payload=@data/examples/weather_sample.json' http://localhost:8000/alerts/apply
```
- GeoTIFF (NDVI): envie um GeoTIFF com bandas [NIR, RED, (opcional) RE] pela *Planejamento de Talhão*.

## Observações
- GeoTIFF precisa de `rasterio`/GDAL, `shapely`/GEOS e `PROJ`. Instale conforme seu SO.
- Para NDVI real, use sensores com banda NIR (ex.: Sentinel‑2 B8 + B4; NDRE usa B5/6/7). Com RGB, usamos proxy (heurística).

## Fontes técnicas citadas
- NDVI: USGS/NASA (fórmula) e NASA Earth Observatory (conceito).
- Sentinel‑2: bandas B8 (NIR), B4 (Red), B5‑B7 (Red Edge) – ESA User Guide.
- GPS/NMEA: especificações RMC (gpsd).
- John Deere APIs: JDLink / Connected Support (developer portal).
- Vosk ASR offline (reconhecimento de voz) e pyttsx3 (TTS offline).
- Alertas de geada/tempo severo: INMET e OpenWeather (API One Call).
Gerado em 2025-08-21T12:00:40.268490Z.
