# Este programa fue desarrollado por Abelino Zuniga (haowkiefer) y Rodrigo Rubio
# El video de como se usa esta en yt con la liga: https://www.youtube.com/watch?v=7e117ckDJ1s

import os
import sys
import shutil
import subprocess
import threading
import time
import urllib.request
import mariadb
import webview
from app import app, DB_CONFIG

HOST = "127.0.0.1"
PORT = 5000
URL = f"http://{HOST}:{PORT}"


def obtener_ruta_recurso(relativa):
    """Obtiene la ruta real tanto en desarrollo como dentro del ejecutable PyInstaller."""
    base = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base, relativa)


def base_datos_lista():
    """Comprueba si el usuario mesero y la BD carnitas con sus tablas ya existen."""
    try:
        con = mariadb.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            port=DB_CONFIG["port"],
        )
        cur = con.cursor()
        cur.execute("SHOW TABLES LIKE 'empleados'")
        existe = cur.fetchone() is not None
        con.close()
        return existe
    except Exception:
        return False


def instalar_todo_un_clic():
    """Configura MariaDB, importa carnitas.sql y crea el acceso directo de escritorio."""
    ruta_sql = obtener_ruta_recurso("carnitas.sql")
    ruta_icono_origen = obtener_ruta_recurso(os.path.join("static", "img", "logo.png"))

    usuario = DB_CONFIG["user"]
    password = DB_CONFIG["password"]
    nombre_db = DB_CONFIG["database"]

    # Preparar script temporal de configuración del sistema
    script_setup = f"""#!/bin/bash
set -e
systemctl enable --now mariadb

mariadb -e "
CREATE USER IF NOT EXISTS '{usuario}'@'127.0.0.1' IDENTIFIED BY '{password}';
CREATE USER IF NOT EXISTS '{usuario}'@'localhost' IDENTIFIED BY '{password}';
ALTER USER '{usuario}'@'127.0.0.1' IDENTIFIED BY '{password}';
ALTER USER '{usuario}'@'localhost' IDENTIFIED BY '{password}';
GRANT ALL PRIVILEGES ON \\`{nombre_db}\\`.* TO '{usuario}'@'127.0.0.1';
GRANT ALL PRIVILEGES ON \\`{nombre_db}\\`.* TO '{usuario}'@'localhost';
FLUSH PRIVILEGES;
CREATE DATABASE IF NOT EXISTS \\`{nombre_db}\\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
"
mariadb {nombre_db} < "{ruta_sql}"
"""

    tmp_script = "/tmp/instalar_carnitas_setup.sh"
    with open(tmp_script, "w", encoding="utf-8") as f:
        f.write(script_setup)
    os.chmod(tmp_script, 0o755)

    # Pedir contraseña con ventana gráfica nativa de Linux (pkexec)
    subprocess.run(["pkexec", "bash", tmp_script], check=True)
    os.remove(tmp_script)

    # Instalar ejecutable en ~/.local/bin y crear acceso directo sin requerir root
    if getattr(sys, "frozen", False):
        dir_app = os.path.expanduser("~/.local/share/carnitas_pos")
        os.makedirs(dir_app, exist_ok=True)
        destino_bin = os.path.join(dir_app, "CarnitasPOS")
        destino_icono = os.path.join(dir_app, "logo.png")

        if os.path.abspath(sys.executable) != destino_bin:
            shutil.copy2(sys.executable, destino_bin)
            os.chmod(destino_bin, 0o755)

        if os.path.exists(ruta_icono_origen):
            shutil.copy2(ruta_icono_origen, destino_icono)

        desktop_entry = f"""[Desktop Entry]
Name=Carnitas POS
Comment=Sistema de Gestión de Restaurante - Carnitas Estela
Exec={destino_bin}
Icon={destino_icono}
Terminal=false
Type=Application
Categories=Office;Finance;
"""
        ruta_menu = os.path.expanduser("~/.local/share/applications/carnitas.desktop")
        os.makedirs(os.path.dirname(ruta_menu), exist_ok=True)
        with open(ruta_menu, "w", encoding="utf-8") as f:
            f.write(desktop_entry)

        for escritorio in ["Desktop", "Escritorio"]:
            ruta_esc = os.path.expanduser(f"~/{escritorio}")
            if os.path.isdir(ruta_esc):
                acceso = os.path.join(ruta_esc, "CarnitasPOS.desktop")
                with open(acceso, "w", encoding="utf-8") as f:
                    f.write(desktop_entry)
                os.chmod(acceso, 0o755)


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
    if not base_datos_lista():
        instalar_todo_un_clic()

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
