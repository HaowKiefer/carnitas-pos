# Este programa fue desarrollado por Abelino Zuniga (haowkiefer) y Rodrigo Rubio
# El video de como se usa esta en yt con la liga: https://www.youtube.com/watch?v=7e117ckDJ1s

import ctypes
import glob
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import mariadb
import webview
from app import app, DB_CONFIG

HOST = "127.0.0.1"
PORT = 5000
URL = f"http://{HOST}:{PORT}"
ES_WINDOWS = os.name == "nt"


def obtener_ruta_recurso(relativa):
    """Obtiene recursos internos empaquetados (templates, static, iconos)."""
    base = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base, relativa)


def obtener_carpeta_ejecutable():
    """Obtiene la carpeta real donde está ubicado el ejecutable o script."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.abspath(os.path.dirname(__file__))


def es_administrador_windows():
    """Verifica si el proceso tiene privilegios de Administrador en Windows."""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def encontrar_cliente_mariadb_windows():
    """Localiza mariadb.exe o mysql.exe en PATH o en Program Files."""
    for cmd in ("mariadb.exe", "mysql.exe"):
        ruta = shutil.which(cmd)
        if ruta:
            return ruta

    patrones = [
        r"C:\Program Files\MariaDB*\bin\mariadb.exe",
        r"C:\Program Files\MariaDB*\bin\mysql.exe",
        r"C:\Program Files (x86)\MariaDB*\bin\mariadb.exe",
        r"C:\Program Files (x86)\MariaDB*\bin\mysql.exe",
        r"C:\xampp\mysql\bin\mysql.exe",
    ]
    for patron in patrones:
        coincidencias = sorted(glob.glob(patron), reverse=True)
        if coincidencias:
            return coincidencias[0]

    return None


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


def mostrar_error_y_salir(titulo, mensaje_html):
    """Muestra una ventana gráfica de error clara para el usuario final."""
    webview.create_window(title=titulo, html=mensaje_html, width=540, height=260)
    webview.start()
    sys.exit(1)


def instalar_en_windows(ruta_sql, ruta_icono_origen):
    """Configura MariaDB, importa carnitas.sql y crea accesos directos en Windows 11."""
    cliente_sql = encontrar_cliente_mariadb_windows()
    if not cliente_sql:
        mostrar_error_y_salir(
            "Falta MariaDB - Carnitas POS",
            "<h3>No se detectó MariaDB en esta computadora</h3>"
            "<p>Instala <b>MariaDB Server</b> para Windows (deja la contraseña de root vacía) y vuelve a abrir <b>CarnitasPOS.exe</b>.</p>",
        )

    usuario = DB_CONFIG["user"]
    password = DB_CONFIG["password"]
    nombre_db = DB_CONFIG["database"]
    puerto = str(DB_CONFIG["port"])

    # 1. Asegurar que el servicio de MariaDB esté encendido (elevando con UAC si hace falta)
    ps_servicio = (
        "$svc = Get-Service | Where-Object { $_.Name -match 'MariaDB|MySQL' } | Select-Object -First 1; "
        "if ($svc -and $svc.Status -ne 'Running') { "
        "Set-Service -Name $svc.Name -StartupType Automatic; "
        "Start-Service -Name $svc.Name "
        "}"
    )
    if es_administrador_windows():
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_servicio],
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    else:
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            "powershell.exe",
            f'-NoProfile -ExecutionPolicy Bypass -Command "{ps_servicio}"',
            None,
            0,
        )
        time.sleep(3)

    # 2. Crear usuario 'mesero' y base de datos 'carnitas' con root local
    sql_setup = (
        f"CREATE USER IF NOT EXISTS '{usuario}'@'127.0.0.1' IDENTIFIED BY '{password}';\n"
        f"CREATE USER IF NOT EXISTS '{usuario}'@'localhost' IDENTIFIED BY '{password}';\n"
        f"ALTER USER '{usuario}'@'127.0.0.1' IDENTIFIED BY '{password}';\n"
        f"ALTER USER '{usuario}'@'localhost' IDENTIFIED BY '{password}';\n"
        f"GRANT ALL PRIVILEGES ON `{nombre_db}`.* TO '{usuario}'@'127.0.0.1';\n"
        f"GRANT ALL PRIVILEGES ON `{nombre_db}`.* TO '{usuario}'@'localhost';\n"
        f"FLUSH PRIVILEGES;\n"
        f"CREATE DATABASE IF NOT EXISTS `{nombre_db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\n"
    )

    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as tmp:
        tmp.write(sql_setup)
        ruta_tmp_setup = tmp.name

    try:
        with open(ruta_tmp_setup, "r", encoding="utf-8") as f_setup:
            subprocess.run(
                [cliente_sql, "--protocol=TCP", "-h", "127.0.0.1", "-P", puerto, "-u", "root"],
                stdin=f_setup,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

        # 3. Importar carnitas.sql usando el usuario recién creado
        env = os.environ.copy()
        env["MYSQL_PWD"] = password
        with open(ruta_sql, "r", encoding="utf-8") as f_datos:
            subprocess.run(
                [cliente_sql, "--protocol=TCP", "-h", "127.0.0.1", "-P", puerto, "-u", usuario, nombre_db],
                stdin=f_datos,
                env=env,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
    except subprocess.CalledProcessError:
        mostrar_error_y_salir(
            "Error al Configurar Base de Datos",
            "<h3>No se pudo conectar como root a MariaDB</h3>"
            "<p>Verifica que el servicio <b>MariaDB</b> esté iniciado y que el usuario <code>root</code> no tenga una contraseña personalizada que bloquee la configuración inicial.</p>",
        )
    finally:
        if os.path.exists(ruta_tmp_setup):
            os.remove(ruta_tmp_setup)

    # 4. Copiar el .exe a AppData\Local\CarnitasPOS y crear accesos directos (.lnk)
    if getattr(sys, "frozen", False):
        dir_app = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "CarnitasPOS")
        os.makedirs(dir_app, exist_ok=True)
        destino_exe = os.path.join(dir_app, "CarnitasPOS.exe")
        destino_icono = os.path.join(dir_app, "logo.png")

        if os.path.abspath(sys.executable).lower() != destino_exe.lower():
            shutil.copy2(sys.executable, destino_exe)

        if os.path.exists(ruta_icono_origen):
            shutil.copy2(ruta_icono_origen, destino_icono)

        escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
        menu_inicio = os.path.join(
            os.environ.get("APPDATA", ""),
            "Microsoft",
            "Windows",
            "Start Menu",
            "Programs",
        )

        destinos_lnk = []
        if os.path.isdir(escritorio):
            destinos_lnk.append(os.path.join(escritorio, "Carnitas POS.lnk"))
        if os.path.isdir(menu_inicio):
            destinos_lnk.append(os.path.join(menu_inicio, "Carnitas POS.lnk"))

        for lnk in destinos_lnk:
            ps_lnk = (
                f"$ws = New-Object -ComObject WScript.Shell; "
                f"$s = $ws.CreateShortcut('{lnk}'); "
                f"$s.TargetPath = '{destino_exe}'; "
                f"$s.WorkingDirectory = '{dir_app}'; "
                f"$s.Description = 'Sistema de Gestión - Carnitas Estela'; "
                f"$s.Save()"
            )
            subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_lnk],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )


def instalar_en_linux(ruta_sql, ruta_icono_origen):
    """Configura MariaDB, importa carnitas.sql y crea lanzador .desktop en Arch Linux."""
    usuario = DB_CONFIG["user"]
    password = DB_CONFIG["password"]
    nombre_db = DB_CONFIG["database"]

    script_root = f"""#!/bin/bash
set -e
systemctl enable --now mariadb
mariadb -u root <<'SQL'
CREATE USER IF NOT EXISTS '{usuario}'@'127.0.0.1' IDENTIFIED BY '{password}';
CREATE USER IF NOT EXISTS '{usuario}'@'localhost' IDENTIFIED BY '{password}';
ALTER USER '{usuario}'@'127.0.0.1' IDENTIFIED BY '{password}';
ALTER USER '{usuario}'@'localhost' IDENTIFIED BY '{password}';
GRANT ALL PRIVILEGES ON `{nombre_db}`.* TO '{usuario}'@'127.0.0.1';
GRANT ALL PRIVILEGES ON `{nombre_db}`.* TO '{usuario}'@'localhost';
FLUSH PRIVILEGES;
CREATE DATABASE IF NOT EXISTS `{nombre_db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SQL
"""
    with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False, encoding="utf-8") as tmp:
        tmp.write(script_root)
        ruta_script = tmp.name

    try:
        os.chmod(ruta_script, 0o755)
        subprocess.run(["pkexec", "bash", ruta_script], check=True)
    except subprocess.CalledProcessError:
        mostrar_error_y_salir(
            "Instalación Cancelada - Carnitas POS",
            "<h3>Se canceló la autenticación o falló MariaDB</h3>"
            "<p>Asegúrate de tener instalado <code>mariadb</code>, haber inicializado la base de datos y aceptar la contraseña de administrador.</p>",
        )
    finally:
        if os.path.exists(ruta_script):
            os.remove(ruta_script)

    env = os.environ.copy()
    env["MYSQL_PWD"] = password
    with open(ruta_sql, "r", encoding="utf-8") as f_datos:
        subprocess.run(
            ["mariadb", "--protocol=TCP", "-h", "127.0.0.1", "-u", usuario, nombre_db],
            stdin=f_datos,
            env=env,
            check=True,
        )

    if getattr(sys, "frozen", False):
        dir_bin = os.path.expanduser("~/.local/bin")
        dir_icon = os.path.expanduser("~/.local/share/icons/hicolor/256x256/apps")
        dir_apps = os.path.expanduser("~/.local/share/applications")
        os.makedirs(dir_bin, exist_ok=True)
        os.makedirs(dir_icon, exist_ok=True)
        os.makedirs(dir_apps, exist_ok=True)

        destino_bin = os.path.join(dir_bin, "CarnitasPOS")
        destino_icon = os.path.join(dir_icon, "carnitas-pos.png")
        destino_desktop = os.path.join(dir_apps, "carnitas-pos.desktop")

        if os.path.abspath(sys.executable) != destino_bin:
            shutil.copy2(sys.executable, destino_bin)
            os.chmod(destino_bin, 0o755)

        if os.path.exists(ruta_icono_origen):
            shutil.copy2(ruta_icono_origen, destino_icon)

        contenido_desktop = (
            "[Desktop Entry]\n"
            "Version=1.0\n"
            "Type=Application\n"
            "Name=Carnitas POS\n"
            "Comment=Sistema de Gestión - Carnitas Estela\n"
            f"Exec={destino_bin}\n"
            f"Icon={destino_icon}\n"
            "Terminal=false\n"
            "Categories=Office;Finance;\n"
        )
        with open(destino_desktop, "w", encoding="utf-8") as f_desk:
            f_desk.write(contenido_desktop)
        os.chmod(destino_desktop, 0o755)


def instalar_todo_un_clic():
    """Orquesta la instalación automática según el sistema operativo."""
    carpeta_actual = obtener_carpeta_ejecutable()
    ruta_sql = os.path.join(carpeta_actual, "carnitas.sql")
    ruta_icono_origen = obtener_ruta_recurso(os.path.join("static", "img", "logo.png"))

    if not os.path.exists(ruta_sql):
        ejecutable = "CarnitasPOS.exe" if ES_WINDOWS else "CarnitasPOS"
        mostrar_error_y_salir(
            "Error de Instalación - Carnitas POS",
            f"<h3>No se encontró carnitas.sql</h3>"
            f"<p>Asegúrate de descomprimir todo el archivo ZIP y dejar <b>carnitas.sql</b> en la misma carpeta que <b>{ejecutable}</b>:<br>"
            f"<code>{carpeta_actual}</code></p>",
        )

    if ES_WINDOWS:
        instalar_en_windows(ruta_sql, ruta_icono_origen)
    else:
        instalar_en_linux(ruta_sql, ruta_icono_origen)


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
