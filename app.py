import os, re, shutil, tempfile
from flask import Flask, request, jsonify, Response, abort
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import yt_dlp

app = Flask(__name__, static_folder="static", static_url_path="")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
limiter = Limiter(get_remote_address, app=app, storage_uri="memory://")

# Acepta APP_KEYS (varias, separadas por comas) o, si no existe, APP_KEY (una sola)
_raw = os.environ.get("APP_KEYS") or os.environ.get("APP_KEY", "")
KEYS = {k.strip() for k in _raw.split(",") if k.strip()}

FB_RE = re.compile(r"https?://([\w-]+\.)*(facebook\.com|fb\.watch|fb\.com)/", re.I)


@app.get("/")
def home():
    return app.send_static_file("index.html")


@app.post("/api/download")
@limiter.limit("10 per hour")
def download():
    if KEYS and request.headers.get("X-Key") not in KEYS:
        abort(401)
    url = (request.get_json(silent=True) or {}).get("url", "")
    if not FB_RE.match(url):
        return jsonify(error="Ese enlace no parece de Facebook"), 400

    tmp = tempfile.mkdtemp()
    try:
        opts = {
            "outtmpl": f"{tmp}/video.%(ext)s",
            "format": "best[ext=mp4]/best",
            "noplaylist": True,
            "quiet": True,
            "max_filesize": 100 * 1024 * 1024,
            "match_filter": yt_dlp.utils.match_filter_func("duration < 600"),
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
        with open(path, "rb") as f:
            data = f.read()
    except Exception:
        return jsonify(error="No se pudo descargar (¿privado, muy largo o bloqueado?)"), 500
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return Response(data, mimetype="video/mp4",
                    headers={"Content-Disposition": "attachment; filename=video.mp4"})