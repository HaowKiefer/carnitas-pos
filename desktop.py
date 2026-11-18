# Este programa fue desarrollado por Abelino Zuniga (haowkiefer) y Rodrigo Rubio
# El video de como se usa esta en yt con la liga: https://www.youtube.com/watch?v=7e117ckDJ1s

import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
import webview
from app import app

HOST = "127.0.0.1"
PORT = 5000
URL = f"http://{HOST}:{PORT}"
ES_WINDOWS = os.name == "nt"


def crear_acceso_directo_windows():
    """Crea acceso directo en Escritorio la primera vez que se ejecuta en Windows."""
    if not getattr(sys, "frozen", False) or not ES_WINDOWS:
        return

    dir_app = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "CarnitasPOS")
    os.makedirs(dir_app, exist_ok=True)
    destino_exe = os.path.join(dir_app, "CarnitasPOS.exe")

    if os.path.abspath(sys.executable).lower() != destino_exe.lower():
        shutil.copy2(sys.executable, destino_exe)
        carpeta_origen = os.path.dirname(os.path.abspath(sys.executable))
        sql_origen = os.path.join(carpeta_origen, "carnitas.sql")
        if os.path.exists(sql_origen):
            shutil.copy2(sql_origen, os.path.join(dir_app, "carnitas.sql"))

    escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
    lnk_escritorio = os.path.join(escritorio, "Carnitas POS.lnk")
    if os.path.isdir(escritorio) and not os.path.exists(lnk_escritorio):
        ps_lnk = (
            f"$ws = New-Object -ComObject WScript.Shell; "
            f"$s = $ws.CreateShortcut('{lnk_escritorio}'); "
            f"$s.TargetPath = '{destino_exe}'; "
            f"$s.WorkingDirectory = '{dir_app}'; "
            f"$s.Description = 'Sistema de Gestión - Carnitas Estela'; "
            f"$s.Save()"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_lnk],
            creationflags=subprocess.CREATE_NO_WINDOW,
        )


def iniciar_servidor():
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)


def esperar_servidor():
    for _ in range(40):
        try:
            urllib.request.urlopen(URL)
            return True
        except Exception:
            time.sleep(0.2)
    return False


if __name__ == "__main__":
    crear_acceso_directo_windows()

    hilo_flask = threading.Thread(target=iniciar_servidor, daemon=True)
    hilo_flask.start()

    if esperar_servidor():
        webview.create_window(
            title="Sistema de Gestión - Carnitas Estela",
            url=URL,
            width=1280,
            height=800,
            resizable=True,
        )
        webview.start()
