# Este programa fue desarrollado por Abelino Zuniga (haowkiefer) y Rodrigo Rubio
# El video de como se usa esta en yt con la liga https://www.youtube.com/watch?v=7e117ckDJ1s

import json
import os
import sys
from flask import Flask, render_template, request, redirect, session, url_for
import mariadb
from datetime import datetime, timedelta

# Detectar si corre como ejecutable empaquetado (PyInstaller) o como script normal
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(base_dir, 'templates'),
    static_folder=os.path.join(base_dir, 'static')
)
app.secret_key = "clave_simple"  # En producción, usa una clave aleatoria y segura


def obtener_ruta_config_db():
    """Guarda la configuración en AppData (Windows) o ~/.config/CarnitasPOS (Linux)."""
    if os.name == "nt":
        carpeta = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "CarnitasPOS")
    else:
        carpeta = os.path.join(os.path.expanduser("~"), ".config", "CarnitasPOS")
    os.makedirs(carpeta, exist_ok=True)
    return os.path.join(carpeta, "db_config.json")


DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "mesero",
    "password": "mesero123",
    "database": "carnitas",
    "port": 3306
}


def cargar_db_config():
    ruta = obtener_ruta_config_db()
    if os.path.exists(ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
                DB_CONFIG.update(datos)
        except Exception:
            pass


def guardar_db_config(nuevo_config):
    DB_CONFIG.update(nuevo_config)
    ruta = obtener_ruta_config_db()
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(DB_CONFIG, f, indent=2)


def probar_conexion_y_tablas():
    """Verifica si se puede conectar y si la tabla 'empleados' existe."""
    try:
        con = mariadb.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            port=int(DB_CONFIG["port"]),
        )
        cur = con.cursor()
        cur.execute("SHOW TABLES LIKE 'empleados'")
        existe = cur.fetchone() is not None
        con.close()
        return existe
    except Exception:
        return False


def inicializar_sql_con_credenciales(host, port, user, password, database, ruta_sql):
    """Conecta con las credenciales dadas, crea la BD si falta e importa carnitas.sql."""
    con = mariadb.connect(host=host, port=int(port), user=user, password=password)
    cur = con.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    cur.execute(f"USE `{database}`;")

    with open(ruta_sql, "r", encoding="utf-8") as f:
        contenido_sql = f.read()

    # Limpiar comentarios de línea y dividir sentencias SQL de forma segura
    lineas_limpias = []
    for linea in contenido_sql.splitlines():
        strip_l = linea.strip()
        if not strip_l or strip_l.startswith("--") or strip_l.startswith("#"):
            continue
        lineas_limpias.append(linea)

    sql_unido = "\n".join(lineas_limpias)
    for sentencia in sql_unido.split(";"):
        limpia = sentencia.strip()
        if limpia and not (limpia.startswith("/*") and limpia.endswith("*/")):
            cur.execute(limpia)

    con.commit()
    con.close()


cargar_db_config()
mesa_global = None


def get_conexion_db():
    return mariadb.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        port=int(DB_CONFIG["port"])
    )


@app.before_request
def verificar_configuracion_db():
    """Si aún no hay conexión válida o faltan tablas, redirige al formulario de conexión."""
    if request.endpoint in ("configurar_db", "static"):
        return None
    if not probar_conexion_y_tablas():
        return redirect(url_for("configurar_db"))


@app.route("/configurar_db", methods=["GET", "POST"])
def configurar_db():
    error = None
    if request.method == "POST":
        host = request.form.get("host", "127.0.0.1").strip()
        port = int(request.form.get("port", 3306))
        user = request.form.get("user", "root").strip()
        password = request.form.get("password", "")
        database = request.form.get("database", "carnitas").strip()

        try:
            # 1. Probar conexión básica al servidor MariaDB/MySQL
            con = mariadb.connect(host=host, port=port, user=user, password=password)
            cur = con.cursor()
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            cur.execute(f"USE `{database}`;")
            cur.execute("SHOW TABLES LIKE 'empleados'")
            tiene_tablas = cur.fetchone() is not None
            con.close()

            # 2. Si la BD está vacía, buscar carnitas.sql e importarlo
            if not tiene_tablas:
                posibles_rutas = []
                if getattr(sys, "frozen", False):
                    posibles_rutas.append(os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "carnitas.sql"))
                posibles_rutas.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), "carnitas.sql"))
                posibles_rutas.append(os.path.join(os.getcwd(), "carnitas.sql"))

                ruta_sql = next((r for r in posibles_rutas if os.path.exists(r)), None)
                if not ruta_sql:
                    raise FileNotFoundError(f"No se encontró carnitas.sql en: {posibles_rutas[0]}")

                inicializar_sql_con_credenciales(host, port, user, password, database, ruta_sql)

            # 3. Guardar credenciales en disco y entrar al login
            guardar_db_config({
                "host": host,
                "port": port,
                "user": user,
                "password": password,
                "database": database
            })
            return redirect(url_for("login"))

        except Exception as e:
            error = f"No se pudo conectar o importar la base de datos: {e}"

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Configurar Base de Datos - Carnitas POS</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #18181b; color: #f4f4f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .card {{ background: #27272a; padding: 30px; border-radius: 12px; width: 420px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
            h2 {{ margin-top: 0; color: #f59e0b; }}
            label {{ display: block; margin-top: 12px; font-size: 14px; color: #d4d4d8; }}
            input {{ width: 100%; padding: 10px; margin-top: 5px; border-radius: 6px; border: 1px solid #3f3f46; background: #18181b; color: white; box-sizing: border-box; }}
            button {{ width: 100%; padding: 12px; margin-top: 20px; background: #f59e0b; color: #18181b; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; font-size: 15px; }}
            button:hover {{ background: #d97706; }}
            .error {{ background: #7f1d1d; color: #fecaca; padding: 10px; border-radius: 6px; margin-top: 15px; font-size: 13px; }}
            .hint {{ font-size: 12px; color: #a1a1aa; margin-top: 8px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Conexión a MariaDB / MySQL</h2>
            <p class="hint">Ingresa las credenciales de tu servidor local. Si la base de datos aún no existe, se creará e importará automáticamente.</p>
            {f'<div class="error">{error}</div>' if error else ''}
            <form method="POST">
                <label>Servidor (Host)</label>
                <input type="text" name="host" value="{DB_CONFIG['host']}" required>
                <label>Puerto</label>
                <input type="number" name="port" value="{DB_CONFIG['port']}" required>
                <label>Usuario de MySQL / MariaDB (ej. root)</label>
                <input type="text" name="user" value="root" required>
                <label>Contraseña de MySQL / MariaDB</label>
                <input type="password" name="password" placeholder="Déjalo vacío si no tiene contraseña">
                <label>Nombre de la Base de Datos</label>
                <input type="text" name="database" value="{DB_CONFIG['database']}" required>
                <button type="submit">Conectar e Instalar Base de Datos</button>
            </form>
        </div>
    </body>
    </html>
    """


# --- VALIDACIÓN DE LOGIN CON BLOQUEO TEMPORAL (RF-06) ---
def probar_login(usuario, password, rol):
    try:
        con = get_conexion_db()
        cur = con.cursor()

        cur.execute("""
            SELECT numero_empleado, password, activo, intentos_fallidos, bloqueado_hasta
            FROM empleados
            WHERE usuario = %s AND rol = %s
        """, (usuario, rol))

        emp = cur.fetchone()

        if not emp:
            con.close()
            return False, "Usuario o rol incorrectos."

        num_emp, pass_correcta, activo, intentos, bloqueado_hasta = emp

        if not activo:
            con.close()
            return False, "Usuario dado de baja en el sistema."

        ahora = datetime.now()
        if bloqueado_hasta and ahora < bloqueado_hasta:
            minutos_restantes = int((bloqueado_hasta - ahora).total_seconds() // 60) + 1
            con.close()
            return False, f"Cuenta bloqueada temporalmente por seguridad. Intenta de nuevo en {minutos_restantes} minuto(s)."

        if password == pass_correcta:
            cur.execute("""
                UPDATE empleados
                SET intentos_fallidos = 0, bloqueado_hasta = NULL
                WHERE numero_empleado = %s
            """, (num_emp,))
            con.commit()
            con.close()
            return True, "Ok"
        else:
            nuevos_intentos = (intentos or 0) + 1
            nuevo_bloqueo = None

            if nuevos_intentos >= 3:
                nuevo_bloqueo = ahora + timedelta(minutes=15)
                msg = "Has superado los 3 intentos fallidos consecutivos. Tu cuenta se ha bloqueado temporalmente por 15 minutos."
            else:
                intentos_restantes = 3 - nuevos_intentos
                msg = f"Contraseña incorrecta. Te quedan {intentos_restantes} intento(s) antes del bloqueo temporal."

            cur.execute("""
                UPDATE empleados
                SET intentos_fallidos = %s, bloqueado_hasta = %s
                WHERE numero_empleado = %s
            """, (nuevos_intentos, nuevo_bloqueo, num_emp))

            con.commit()
            con.close()
            return False, msg

    except Exception as e:
        print(f"Error al validar login: {e}")
        return False, f"Error en el sistema: {e}"


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"].strip()
        password = request.form["password"].strip()
        rol = request.form.get("rol")

        es_valido, mensaje = probar_login(usuario, password, rol)

        if es_valido:
            session.clear()
            session["usuario"] = usuario
            session["rol"] = rol

            if rol == "admin":
                return redirect(url_for("administrador_inicio"))
            else:
                return redirect(url_for("usuario_inicio"))
        else:
            return render_template("login.html", error=mensaje)

    return render_template("login.html")


@app.route("/inicio", methods=["GET", "POST"])
def administrador_inicio():
    if "usuario" not in session or session.get("rol") != "admin":
        return redirect("/")

    if request.method == "POST":
        accion = request.form.get("accion")
        if accion == "ver_bebidas":
            return redirect(url_for("bebida"))
        elif accion == "ver_comida":
            return redirect(url_for("comida"))
        elif accion == "ver_extras":
            return redirect(url_for("extras"))
        elif accion == "ver_empleados":
            return redirect(url_for("empleados"))
        elif accion == "ver_nomina":
            return redirect(url_for("nomina"))
        elif accion == "ver_inventario":
            return redirect(url_for("inventario"))
        elif accion == "ver_historial":
            return redirect(url_for("historial_ventas"))
        elif accion == "ver_gastos":
            return redirect(url_for("gastos"))
        elif accion == "agregar_producto":
            return redirect(url_for("agregar_producto"))
        elif accion == "eliminar_producto":
            return redirect(url_for("eliminar_producto"))
        elif accion == "ver_recetas":
            return redirect(url_for("recetas"))

    return render_template("administrador_inicio.html", usuario=session["usuario"], mesa=mesa_global)


@app.route("/empleados", methods=["GET", "POST"])
def empleados():
    if "usuario" not in session or session.get("rol") != "admin":
        return redirect("/")

    mensaje = None
    admin_actual = session.get("usuario")

    if request.method == "POST":
        accion = request.form.get("accion")

        if accion == "agregar":
            nombre = request.form.get("nombre", "").strip()
            apellido = request.form.get("apellido", "").strip()
            usuario = request.form.get("usuario", "").strip()
            password = request.form.get("password", "").strip()
            rol = request.form.get("rol", "mesero")
            direccion = request.form.get("direccion", "").strip()
            telefono = request.form.get("telefono", "").strip()

            if nombre and apellido and usuario and password:
                try:
                    con = get_conexion_db()
                    cur = con.cursor()

                    cur.execute("""
                        INSERT INTO empleados (nombre, apellido, usuario, password, rol, direccion, telefono, activo, en_turno)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, 1, 0)
                    """, (nombre, apellido, usuario, password, rol, direccion, telefono))

                    id_nuevo_empleado = cur.lastrowid

                    cur.execute("""
                        INSERT INTO historial_cambios_usuarios (id_admin, empleado_afectado, accion, detalles)
                        VALUES (%s, %s, %s, %s)
                    """, (admin_actual, id_nuevo_empleado, "CREACION", f"Se creó el usuario '{usuario}' con rol '{rol}'."))

                    con.commit()
                    con.close()
                    mensaje = "Empleado registrado correctamente."
                except mariadb.IntegrityError:
                    mensaje = "El nombre de usuario ya está registrado."
                except Exception as e:
                    mensaje = f"Error al agregar empleado: {e}"
            else:
                mensaje = "Nombre, apellido, usuario y contraseña son obligatorios."

        elif accion == "cambiar_rol":
            numero_empleado = request.form.get("numero_empleado")
            nuevo_rol = request.form.get("nuevo_rol")

            try:
                con = get_conexion_db()
                cur = con.cursor()

                cur.execute("SELECT usuario, rol FROM empleados WHERE numero_empleado = %s", (numero_empleado,))
                res = cur.fetchone()

                if res:
                    usuario_target, rol_anterior = res[0], res[1]

                    if rol_anterior != nuevo_rol:
                        cur.execute("UPDATE empleados SET rol = %s WHERE numero_empleado = %s", (nuevo_rol, numero_empleado))

                        cur.execute("""
                            INSERT INTO historial_cambios_usuarios (id_admin, empleado_afectado, accion, detalles)
                            VALUES (%s, %s, %s, %s)
                        """, (admin_actual, numero_empleado, "CAMBIO_ROL", f"Rol de '{usuario_target}' actualizado de '{rol_anterior}' a '{nuevo_rol}'."))

                        con.commit()
                        mensaje = f"Rol de {usuario_target} actualizado a {nuevo_rol}."
                    else:
                        mensaje = "El empleado ya posee ese rol."
                con.close()
            except Exception as e:
                mensaje = f"Error al cambiar el rol: {e}"

        elif accion == "baja_logica":
            numero_empleado = request.form.get("numero_empleado")
            try:
                con = get_conexion_db()
                cur = con.cursor()

                cur.execute("SELECT usuario FROM empleados WHERE numero_empleado = %s", (numero_empleado,))
                res = cur.fetchone()
                usuario_target = res[0] if res else str(numero_empleado)

                cur.execute("UPDATE empleados SET activo = 0, en_turno = 0 WHERE numero_empleado = %s", (numero_empleado,))

                cur.execute("""
                    INSERT INTO historial_cambios_usuarios (id_admin, empleado_afectado, accion, detalles)
                    VALUES (%s, %s, %s, %s)
                """, (admin_actual, numero_empleado, "BAJA_LOGICA", f"Acceso desactivado para el usuario '{usuario_target}'."))

                con.commit()
                con.close()
                mensaje = "Empleado dado de baja lógicamente."
            except Exception as e:
                mensaje = f"Error al dar de baja al empleado: {e}"

    try:
        con = get_conexion_db()
        cur = con.cursor()

        cur.execute("""
            SELECT numero_empleado, nombre, apellido, usuario, rol, telefono, activo, en_turno
            FROM empleados
            WHERE activo = 1
            ORDER BY numero_empleado DESC
        """)
        datos = cur.fetchall()
        columnas = ["N° Emp.", "Nombre", "Usuario", "Rol / Cambiar", "Teléfono", "Estado Acceso", "Estado Turno", "Acciones"]

        cur.execute("""
            SELECT h.id, h.id_admin, CONCAT(e.nombre, ' ', e.apellido, ' (', e.usuario, ')') AS empleado, h.accion, h.detalles, h.fecha
            FROM historial_cambios_usuarios h
            JOIN empleados e ON h.empleado_afectado = e.numero_empleado
            ORDER BY h.id DESC
        """)
        historial_cambios = cur.fetchall()

        cur.execute("""
            SELECT a.id, CONCAT(e.nombre, ' ', e.apellido) AS empleado, e.usuario, a.tipo, a.fecha_hora
            FROM asistencias a
            JOIN empleados e ON a.numero_empleado = e.numero_empleado
            ORDER BY a.fecha_hora DESC
        """)
        historial_asistencias = cur.fetchall()

        con.close()
    except Exception as e:
        return f"Error al cargar los datos: {e}"

    return render_template(
        "empleados.html",
        datos=datos,
        columnas=columnas,
        historial_cambios=historial_cambios,
        historial_asistencias=historial_asistencias,
        usuario=session.get("usuario"),
        mensaje=mensaje
    )


@app.route("/fichar_asistencia", methods=["POST"])
def fichar_asistencia():
    if "usuario" not in session or session.get("rol") != "admin":
        return redirect("/")

    numero_empleado = request.form.get("numero_empleado")
    tipo_evento = request.form.get("tipo")
    TARIFA_HORA = 37.80

    try:
        con = get_conexion_db()
        cur = con.cursor()

        cur.execute("SELECT activo, en_turno FROM empleados WHERE numero_empleado = %s", (numero_empleado,))
        res = cur.fetchone()

        if not res:
            con.close()
            return "Empleado no encontrado", 404

        activo, en_turno = res[0], res[1]

        if not activo:
            con.close()
            return redirect(url_for("empleados"))

        if tipo_evento == "entrada":
            if en_turno == 1:
                con.close()
                return redirect(url_for("empleados"))

            cur.execute("INSERT INTO asistencias (numero_empleado, tipo) VALUES (%s, 'entrada')", (numero_empleado,))
            cur.execute("UPDATE empleados SET en_turno = 1 WHERE numero_empleado = %s", (numero_empleado,))

        elif tipo_evento == "salida":
            if en_turno == 0:
                con.close()
                return redirect(url_for("empleados"))

            cur.execute("""
                SELECT fecha_hora
                FROM asistencias
                WHERE numero_empleado = %s AND tipo = 'entrada'
                ORDER BY id DESC LIMIT 1
            """, (numero_empleado,))
            ultima_entrada = cur.fetchone()

            cur.execute("INSERT INTO asistencias (numero_empleado, tipo) VALUES (%s, 'salida')", (numero_empleado,))
            cur.execute("UPDATE empleados SET en_turno = 0 WHERE numero_empleado = %s", (numero_empleado,))

            if ultima_entrada and ultima_entrada[0]:
                hora_entrada = ultima_entrada[0]
                hora_salida = datetime.now()
                diferencia_segundos = (hora_salida - hora_entrada).total_seconds()

                horas_trabajadas = round(max(0.01, diferencia_segundos / 3600.0), 2)
                total_pagar = round(horas_trabajadas * TARIFA_HORA, 2)

                cur.execute("""
                    INSERT INTO nomina (numero_empleado, horas_trabajadas, pago_por_hora, total_pagar, pagado)
                    VALUES (%s, %s, %s, %s, 0)
                """, (numero_empleado, horas_trabajadas, TARIFA_HORA, total_pagar))

        con.commit()
        con.close()
    except Exception as e:
        return f"Error al registrar asistencia y calcular nómina: {e}"

    return redirect(url_for("empleados"))


# --- NÓMINA Y CALCULADORA DE SUELDOS ($37.80 / HORA) ---
@app.route("/nomina", methods=["GET", "POST"])
def nomina():
    if "usuario" not in session or session.get("rol") != "admin":
        return redirect("/")

    mensaje = None
    TARIFA_HORA = 37.80

    if request.method == "POST":
        accion = request.form.get("accion")

        if accion == "registrar_nomina":
            numero_empleado = request.form.get("numero_empleado")
            try:
                horas = float(request.form.get("horas_trabajadas", 0))
            except ValueError:
                horas = 0.0

            if numero_empleado and horas > 0:
                total_pagar = round(horas * TARIFA_HORA, 2)
                try:
                    con = get_conexion_db()
                    cur = con.cursor()
                    cur.execute("""
                        INSERT INTO nomina (numero_empleado, horas_trabajadas, pago_por_hora, total_pagar, pagado)
                        VALUES (%s, %s, %s, %s, 0)
                    """, (numero_empleado, horas, TARIFA_HORA, total_pagar))
                    con.commit()
                    con.close()
                    mensaje = f"Cálculo de nómina guardado (${total_pagar:.2f} MXN)."
                except Exception as e:
                    mensaje = f"Error al guardar la nómina: {e}"
            else:
                mensaje = "Selecciona un empleado e ingresa una cantidad válida de horas."

        elif accion == "marcar_pagado":
            id_nomina = request.form.get("id_nomina")
            try:
                con = get_conexion_db()
                cur = con.cursor()
                cur.execute("""
                    UPDATE nomina
                    SET pagado = 1, fecha_pago = NOW()
                    WHERE id = %s
                """, (id_nomina,))
                con.commit()
                con.close()
                mensaje = "Estado actualizado: Nómina marcada como PAGADA."
            except Exception as e:
                mensaje = f"Error al actualizar estado de pago: {e}"

        elif accion == "pagar_todo_empleado":
            numero_empleado = request.form.get("numero_empleado")
            try:
                con = get_conexion_db()
                cur = con.cursor()
                cur.execute("""
                    UPDATE nomina
                    SET pagado = 1, fecha_pago = NOW()
                    WHERE numero_empleado = %s AND pagado = 0
                """, (numero_empleado,))
                con.commit()
                con.close()
                mensaje = "Se liquidaron todas las horas pendientes del empleado."
            except Exception as e:
                mensaje = f"Error al liquidar nómina: {e}"

        elif accion == "eliminar":
            id_nomina = request.form.get("id_nomina")
            try:
                con = get_conexion_db()
                cur = con.cursor()
                cur.execute("DELETE FROM nomina WHERE id = %s", (id_nomina,))
                con.commit()
                con.close()
                mensaje = "Registro de nómina eliminado."
            except Exception as e:
                mensaje = f"Error al eliminar registro: {e}"

    try:
        con = get_conexion_db()
        cur = con.cursor()

        cur.execute("""
            SELECT numero_empleado, CONCAT(nombre, ' ', apellido, ' (', rol, ')')
            FROM empleados
            WHERE activo = 1
            ORDER BY nombre ASC
        """)
        empleados_activos = cur.fetchall()

        cur.execute("""
            SELECT e.numero_empleado, CONCAT(e.nombre, ' ', e.apellido) AS empleado, e.rol,
                   COALESCE(SUM(n.horas_trabajadas), 0) AS total_horas,
                   COALESCE(SUM(n.total_pagar), 0) AS total_dinero
            FROM empleados e
            JOIN nomina n ON e.numero_empleado = n.numero_empleado
            WHERE n.pagado = 0
            GROUP BY e.numero_empleado, e.nombre, e.apellido, e.rol
            ORDER BY total_dinero DESC
        """)
        resumen_pendiente = cur.fetchall()

        cur.execute("""
            SELECT n.id, CONCAT(e.nombre, ' ', e.apellido) AS empleado, e.rol,
                   n.horas_trabajadas, n.pago_por_hora, n.total_pagar,
                   n.pagado, n.fecha_registro, n.fecha_pago
            FROM nomina n
            JOIN empleados e ON n.numero_empleado = e.numero_empleado
            ORDER BY n.pagado ASC, n.id DESC
        """)
        registros_nomina = cur.fetchall()

        con.close()
    except Exception as e:
        return f"Error al cargar nómina: {e}"

    return render_template(
        "nomina.html",
        empleados=empleados_activos,
        resumen_pendiente=resumen_pendiente,
        registros=registros_nomina,
        tarifa=TARIFA_HORA,
        mensaje=mensaje,
        usuario=session.get("usuario")
    )


@app.route("/inventario", methods=["GET", "POST"])
def inventario():
    if "usuario" not in session or session.get("rol") != "admin":
        return redirect("/")

    mensaje = None

    if request.method == "POST":
        id_item = request.form.get("id_item")
        nueva_cantidad = request.form.get("nueva_cantidad")

        try:
            con = get_conexion_db()
            cur = con.cursor()
            cur.execute("""
                UPDATE inventario
                SET cantidad = %s
                WHERE id = %s
            """, (nueva_cantidad, id_item))
            con.commit()
            con.close()
            mensaje = "Stock actualizado correctamente."
        except Exception as e:
            mensaje = f"Error al actualizar stock: {e}"

    try:
        con = get_conexion_db()
        cur = con.cursor()
        cur.execute("SELECT id, producto, cantidad, unidad_medida FROM inventario ORDER BY producto ASC")
        datos = cur.fetchall()
        columnas = ["Producto", "Cantidad", "Unidad", "Acción"]
        con.close()
    except Exception as e:
        return f"Error al cargar el inventario: {e}"

    return render_template(
        "inventario.html",
        datos=datos,
        columnas=columnas,
        mensaje=mensaje,
        usuario=session.get("usuario")
    )


@app.route("/usuario_inicio", methods=["GET", "POST"])
def usuario_inicio():
    global mesa_global

    if request.method == "POST":
        mesa = request.form.get("mesa")
        if not mesa:
            return render_template("usuario_inicio.html", error="Selecciona una mesa")

        mesa_global = mesa
        session["rol"] = "cliente"
        return redirect(url_for("menu_mesa"))

    mesas_ocupadas = []
    try:
        con = get_conexion_db()
        cur = con.cursor()
        cur.execute("SELECT DISTINCT mesa FROM ordenes")
        registros = cur.fetchall()
        mesas_ocupadas = [str(r[0]) for r in registros]
        con.close()
    except Exception as e:
        print(f"Error al consultar mesas ocupadas: {e}")

    return render_template("usuario_inicio.html", mesa=mesa_global, mesas_ocupadas=mesas_ocupadas)


@app.route("/menu", methods=["GET", "POST"])
def menu_mesa():
    global mesa_global

    if not mesa_global:
        return redirect(url_for("usuario_inicio"))

    if request.method == "POST":
        accion = request.form.get("accion")

        if accion == "ver_bebidas":
            return redirect(url_for("bebida"))
        elif accion == "ver_comida":
            return redirect(url_for("comida"))
        elif accion == "ver_extras":
            return redirect(url_for("extras"))
        elif accion == "ver_cuenta":
            return redirect(url_for("cuenta"))
        else:
            return render_template("menu_mesa.html", error="Acción no válida", usuario="Cliente", mesa=mesa_global)

    return render_template("menu_mesa.html", usuario="Cliente", mesa=mesa_global)


@app.route("/agregar_orden", methods=["POST"])
def agregar_orden():
    global mesa_global

    if not mesa_global:
        return redirect(url_for("usuario_inicio"))

    producto = request.form.get("producto")
    precio = request.form.get("precio")

    try:
        cantidad = int(request.form.get("cantidad", 1))
        if cantidad < 1:
            cantidad = 1
    except ValueError:
        cantidad = 1

    tipo = request.form.get("tipo")

    cebolla = 1 if request.form.get("cebolla") else 0
    cilantro = 1 if request.form.get("cilantro") else 0
    nopales = 1 if request.form.get("nopales") else 0

    try:
        con = get_conexion_db()
        cur = con.cursor()
        cur.execute("""
            INSERT INTO ordenes (mesa, producto, precio, cantidad, cebolla, cilantro, nopales)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (mesa_global, producto, precio, cantidad, cebolla, cilantro, nopales))
        con.commit()
        con.close()
    except Exception as e:
        return f"Error al agregar orden: {e}"

    if tipo == "comida":
        return redirect(url_for("comida"))
    elif tipo == "bebida":
        return redirect(url_for("bebida"))
    elif tipo == "extras":
        return redirect(url_for("extras"))
    else:
        return redirect(url_for("menu_mesa"))


@app.route("/ordenes")
def ordenes_mesa():
    global mesa_global

    try:
        con = get_conexion_db()
        cur = con.cursor()
        cur.execute("""
            SELECT producto, precio, cantidad, cebolla, cilantro, nopales,
                   (precio * cantidad) AS subtotal, fecha
            FROM ordenes
            WHERE mesa = %s
        """, (mesa_global,))
        datos = cur.fetchall()
        con.close()
    except Exception as e:
        return f"Error: {e}"

    return render_template("ordenes.html", datos=datos, mesa=mesa_global)


@app.route("/historial_ventas")
def historial_ventas():
    if "usuario" not in session or session.get("rol") != "admin":
        return redirect("/")

    ver_todo = request.args.get("ver_todo", "0") == "1"

    try:
        con = get_conexion_db()
        cur = con.cursor()

        if ver_todo:
            cur.execute("""
                SELECT id_venta, mesa, producto, precio, cantidad, subtotal, fecha
                FROM ventas
                ORDER BY id_venta DESC, fecha DESC
            """)
        else:
            cur.execute("""
                SELECT id_venta, mesa, producto, precio, cantidad, subtotal, fecha
                FROM ventas
                WHERE DATE(fecha) = CURRENT_DATE
                ORDER BY id_venta DESC, fecha DESC
            """)
        datos = cur.fetchall()

        cur.execute("""
            SELECT COALESCE(SUM(subtotal), 0)
            FROM ventas
            WHERE DATE(fecha) = CURRENT_DATE
        """)
        total_dia = cur.fetchone()[0]

        cur.execute("""
            SELECT COALESCE(SUM(subtotal), 0)
            FROM ventas
            WHERE fecha >= DATE_SUB(CURRENT_DATE, INTERVAL WEEKDAY(CURRENT_DATE) DAY)
        """)
        total_semanal = cur.fetchone()[0]

        cur.execute("""
            SELECT COALESCE(SUM(subtotal), 0)
            FROM ventas
            WHERE YEAR(fecha) = YEAR(CURRENT_DATE)
        """)
        total_anual = cur.fetchone()[0]

        con.close()
    except Exception as e:
        return f"Error al cargar el historial: {e}"

    return render_template(
        "historial_ventas.html",
        datos=datos,
        total_dia=total_dia,
        total_semanal=total_semanal,
        total_anual=total_anual,
        ver_todo=ver_todo,
        usuario=session.get("usuario")
    )


@app.route("/gastos", methods=["GET", "POST"])
def gastos():
    if "usuario" not in session or session.get("rol") != "admin":
        return redirect("/")

    mensaje = None

    if request.method == "POST":
        concepto = request.form.get("concepto", "").strip()
        monto = request.form.get("monto")
        try:
            cantidad = float(request.form.get("cantidad", 1))
        except ValueError:
            cantidad = 1.0
        unidad_medida = request.form.get("unidad_medida", "pza")

        if concepto and monto:
            try:
                con = get_conexion_db()
                cur = con.cursor()

                cur.execute("""
                    INSERT INTO gastos (concepto, monto, cantidad, unidad_medida)
                    VALUES (%s, %s, %s, %s)
                """, (concepto, monto, cantidad, unidad_medida))

                cur.execute("SELECT id, cantidad FROM inventario WHERE LOWER(producto) = LOWER(%s)", (concepto,))
                item_inv = cur.fetchone()

                if item_inv:
                    id_inv, stock_actual = item_inv[0], item_inv[1]
                    nuevo_stock = float(stock_actual) + cantidad
                    cur.execute("""
                        UPDATE inventario
                        SET cantidad = %s, unidad_medida = %s
                        WHERE id = %s
                    """, (nuevo_stock, unidad_medida, id_inv))
                else:
                    cur.execute("""
                        INSERT INTO inventario (producto, cantidad, unidad_medida)
                        VALUES (%s, %s, %s)
                    """, (concepto, cantidad, unidad_medida))

                con.commit()
                con.close()
                mensaje = f"Gasto registrado e inventario actualizado (+{cantidad} {unidad_medida} a '{concepto}')."
            except Exception as e:
                mensaje = f"Error al registrar gasto e inventario: {e}"
        else:
            mensaje = "El concepto y el monto son obligatorios."

    filtro = request.args.get("filtro", "todos")

    try:
        con = get_conexion_db()
        cur = con.cursor()

        if filtro == "semanal":
            query = """
                SELECT id, concepto, cantidad, unidad_medida, monto, fecha
                FROM gastos
                WHERE fecha >= DATE_SUB(CURRENT_DATE, INTERVAL WEEKDAY(CURRENT_DATE) DAY)
                ORDER BY fecha DESC
            """
        elif filtro == "mensual":
            query = """
                SELECT id, concepto, cantidad, unidad_medida, monto, fecha
                FROM gastos
                WHERE YEAR(fecha) = YEAR(CURRENT_DATE) AND MONTH(fecha) = MONTH(CURRENT_DATE)
                ORDER BY fecha DESC
            """
        elif filtro == "anual":
            query = """
                SELECT id, concepto, cantidad, unidad_medida, monto, fecha
                FROM gastos
                WHERE YEAR(fecha) = YEAR(CURRENT_DATE)
                ORDER BY fecha DESC
            """
        else:
            query = "SELECT id, concepto, cantidad, unidad_medida, monto, fecha FROM gastos ORDER BY fecha DESC"

        cur.execute(query)
        datos = cur.fetchall()
        total_gastos = sum(fila[4] for fila in datos)

        cur.execute("SELECT producto, unidad_medida FROM inventario ORDER BY producto ASC")
        insumos_inventario = cur.fetchall()

        con.close()
    except Exception as e:
        return f"Error al cargar gastos: {e}"

    return render_template(
        "gastos.html",
        datos=datos,
        total=total_gastos,
        insumos_inventario=insumos_inventario,
        filtro_activo=filtro,
        mensaje=mensaje,
        usuario=session.get("usuario")
    )


@app.route("/limpiar_mesa")
def limpiar_mesa():
    global mesa_global
    mesa_global = None
    return redirect(url_for("usuario_inicio"))


@app.route("/agregar_producto", methods=["GET", "POST"])
def agregar_producto():
    if "usuario" not in session or session.get("rol") != "admin":
        return redirect("/")
    mensaje = None

    if request.method == "POST":
        tipo = request.form.get("tipo")
        nombre = request.form.get("nombre").strip()
        precio = request.form.get("precio")

        TABLAS_PERMITIDAS = {"bebida": "bebida", "comida": "comida", "extras": "extras"}
        if tipo not in TABLAS_PERMITIDAS:
            return "Tipo de producto no válido", 400

        tabla = TABLAS_PERMITIDAS[tipo]

        try:
            con = get_conexion_db()
            cur = con.cursor()
            cur.execute(f"INSERT INTO {tabla} (nombre, precio) VALUES (%s, %s)", (nombre, precio))
            con.commit()
            con.close()
            mensaje = "Producto agregado correctamente"
        except Exception as e:
            mensaje = f"Error: {e}"

    return render_template("agregar_producto.html", mensaje=mensaje, mesa=mesa_global)


@app.route("/eliminar_producto", methods=["GET", "POST"])
def eliminar_producto():
    if "usuario" not in session or session.get("rol") != "admin":
        return redirect("/")
    mensaje = None

    if request.method == "POST":
        tipo = request.form.get("tipo")
        nombre = request.form.get("nombre").strip()

        TABLAS_PERMITIDAS = {"bebida": "bebida", "comida": "comida", "extras": "extras"}
        if tipo not in TABLAS_PERMITIDAS:
            return "Tipo de producto no válido", 400

        tabla = TABLAS_PERMITIDAS[tipo]

        try:
            con = get_conexion_db()
            cur = con.cursor()
            cur.execute(f"DELETE FROM {tabla} WHERE nombre = %s", (nombre,))
            con.commit()
            con.close()
            mensaje = "Producto eliminado correctamente"
        except Exception as e:
            mensaje = f"Error: {e}"

    return render_template("eliminar_producto.html", mensaje=mensaje, mesa=mesa_global)


@app.route("/recetas", methods=["GET", "POST"])
def recetas():
    if "usuario" not in session or session.get("rol") != "admin":
        return redirect("/")

    mensaje = None

    if request.method == "POST":
        accion = request.form.get("accion")

        if accion == "guardar":
            producto_venta = request.form.get("producto_venta")
            id_inventario = request.form.get("id_inventario")
            try:
                cantidad_descontar = float(request.form.get("cantidad_descontar", 0))
            except ValueError:
                cantidad_descontar = 0.0

            if producto_venta and id_inventario and cantidad_descontar > 0:
                try:
                    con = get_conexion_db()
                    cur = con.cursor()
                    cur.execute("""
                        SELECT id FROM recetas
                        WHERE LOWER(producto_venta) = LOWER(%s) AND id_inventario = %s
                    """, (producto_venta, id_inventario))
                    existe = cur.fetchone()

                    if existe:
                        cur.execute("""
                            UPDATE recetas SET cantidad_descontar = %s WHERE id = %s
                        """, (cantidad_descontar, existe[0]))
                    else:
                        cur.execute("""
                            INSERT INTO recetas (producto_venta, id_inventario, cantidad_descontar)
                            VALUES (%s, %s, %s)
                        """, (producto_venta, id_inventario, cantidad_descontar))

                    con.commit()
                    con.close()
                    mensaje = "Regla de inventario guardada correctamente."
                except Exception as e:
                    mensaje = f"Error al guardar regla: {e}"
            else:
                mensaje = "Selecciona un producto, un insumo y una cantidad válida."

        elif accion == "eliminar":
            id_receta = request.form.get("id_receta")
            try:
                con = get_conexion_db()
                cur = con.cursor()
                cur.execute("DELETE FROM recetas WHERE id = %s", (id_receta,))
                con.commit()
                con.close()
                mensaje = "Regla eliminada."
            except Exception as e:
                mensaje = f"Error al eliminar regla: {e}"

    try:
        con = get_conexion_db()
        cur = con.cursor()

        cur.execute("""
            SELECT nombre FROM comida
            UNION
            SELECT nombre FROM bebida
            UNION
            SELECT nombre FROM extras
            ORDER BY nombre ASC
        """)
        productos_menu = [r[0] for r in cur.fetchall()]

        cur.execute("SELECT id, producto, unidad_medida FROM inventario ORDER BY producto ASC")
        insumos = cur.fetchall()

        cur.execute("""
            SELECT r.id, r.producto_venta, i.producto, r.cantidad_descontar, i.unidad_medida
            FROM recetas r
            JOIN inventario i ON r.id_inventario = i.id
            ORDER BY r.producto_venta ASC
        """)
        reglas = cur.fetchall()
        con.close()
    except Exception as e:
        return f"Error al cargar recetas: {e}"

    return render_template(
        "recetas.html",
        productos_menu=productos_menu,
        insumos=insumos,
        reglas=reglas,
        mensaje=mensaje,
        usuario=session.get("usuario")
    )


@app.route("/bebida")
def bebida():
    try:
        con = get_conexion_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM bebida")
        datos = cur.fetchall()
        columnas = [desc[0] for desc in cur.description]
        con.close()
    except Exception as e:
        return f"Error al cargar los datos: {e}"

    return render_template(
        "bebida.html",
        datos=datos,
        columnas=columnas,
        usuario=session.get("usuario", "Cliente"),
        mesa=mesa_global
    )


@app.route("/comida")
def comida():
    try:
        con = get_conexion_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM comida")
        datos = cur.fetchall()
        columnas = [desc[0] for desc in cur.description]
        con.close()
    except Exception as e:
        return f"Error al cargar los datos: {e}"

    return render_template(
        "comida.html",
        datos=datos,
        columnas=columnas,
        usuario=session.get("usuario", "Cliente"),
        mesa=mesa_global
    )


@app.route("/extras")
def extras():
    try:
        con = get_conexion_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM extras")
        datos = cur.fetchall()
        columnas = [desc[0] for desc in cur.description]
        con.close()
    except Exception as e:
        return f"Error al cargar los datos: {e}"

    return render_template(
        "extras.html",
        datos=datos,
        columnas=columnas,
        usuario=session.get("usuario", "Cliente"),
        mesa=mesa_global
    )


@app.route("/cuenta", methods=["GET", "POST"])
def cuenta():
    global mesa_global

    if not mesa_global:
        return redirect(url_for("usuario_inicio"))

    con = get_conexion_db()
    cur = con.cursor()

    if request.method == "POST":
        accion = request.form.get("accion")

        if accion == "eliminar":
            id_orden = request.form.get("id_orden")
            cur.execute("DELETE FROM ordenes WHERE id = %s", (id_orden,))
            con.commit()

        elif accion == "pagar":
            cur.execute("""
                SELECT producto, precio, cantidad, cebolla, cilantro, nopales
                FROM ordenes
                WHERE mesa = %s
            """, (mesa_global,))
            ordenes = cur.fetchall()

            cur.execute("SELECT COALESCE(MAX(id_venta), 0) + 1 FROM ventas")
            nuevo_id_venta = cur.fetchone()[0]

            for o in ordenes:
                producto_nombre = o[0]
                precio_unitario = o[1]
                cantidad_vendida = o[2]
                subtotal = precio_unitario * cantidad_vendida

                cur.execute("""
                    INSERT INTO ventas (id_venta, mesa, producto, precio, cantidad, subtotal)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (nuevo_id_venta, mesa_global, producto_nombre, precio_unitario, cantidad_vendida, subtotal))

                cur.execute("""
                    SELECT id_inventario, cantidad_descontar
                    FROM recetas
                    WHERE LOWER(producto_venta) = LOWER(%s)
                """, (producto_nombre,))
                ingredientes = cur.fetchall()

                for ing in ingredientes:
                    id_inv, cant_desc = ing[0], float(ing[1])
                    total_descontar = cant_desc * cantidad_vendida
                    cur.execute("""
                        UPDATE inventario
                        SET cantidad = GREATEST(0, cantidad - %s)
                        WHERE id = %s
                    """, (total_descontar, id_inv))

            cur.execute("DELETE FROM ordenes WHERE mesa = %s", (mesa_global,))
            con.commit()
            con.close()

            mesa_global = None
            return redirect(url_for("usuario_inicio"))

    cur.execute("""
        SELECT id, producto, precio, cantidad, cebolla, cilantro, nopales,
               (precio * cantidad) AS subtotal
        FROM ordenes
        WHERE mesa = %s
    """, (mesa_global,))
    datos = cur.fetchall()

    total = sum(d[7] for d in datos)
    con.close()

    return render_template("cuenta.html", datos=datos, total=total, mesa=mesa_global)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
