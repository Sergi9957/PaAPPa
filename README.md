# Descargador de videos

Mini web (PWA) para descargar videos de Facebook a partir de su enlace.
Hecha con Flask y yt-dlp.

## Uso local
pip install -r requirements.txt
$env:APP_KEY="laclave"; python app.py

## Despliegue
Comando de arranque: gunicorn app:app
Variable de entorno: APP_KEY
