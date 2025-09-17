import sqlite3
from datetime import datetime
import os
import re

# -----------------------------
# CONFIGURACIÓN DE ARCHIVO DB
# -----------------------------
DB_FILE = os.path.join(
    "c:/Users/hecto/OneDrive/Documentos/Juanda/1101/PROFU/App",
    "datos.db"
)

def conectar():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")  # 🔑 Activar llaves foráneas
    return conn

# -----------------------------
# CREACIÓN DE TABLAS
# -----------------------------
def crear_tabla_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            padre TEXT,
            estudiante TEXT,
            curso TEXT,
            promocion TEXT,
            correo TEXT UNIQUE,
            contrasena TEXT,
            tipo_usuario TEXT DEFAULT 'user'
        )
    """)
    conn.commit()
    conn.close()

def crear_tabla_metas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            curso TEXT,
            nombre TEXT,
            fecha TEXT,
            costo REAL
        )
    """)
    conn.commit()
    conn.close()

def crear_tabla_ahorros():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ahorros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meta_id INTEGER,
            usuario_id INTEGER,
            cantidad REAL,
            fecha TEXT,
            FOREIGN KEY (meta_id) REFERENCES metas(id) ON DELETE CASCADE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def crear_tabla_salidas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS salidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meta_id INTEGER,
            usuario_id INTEGER,
            cantidad REAL,
            fecha TEXT,
            FOREIGN KEY (meta_id) REFERENCES metas(id) ON DELETE CASCADE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def crear_tabla_aportes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aportes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            curso TEXT,
            cantidad REAL,
            fecha TEXT,
            hora TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def crear_tabla_ascensos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ascensos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            curso_anterior TEXT,
            curso_nuevo TEXT,
            fecha TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def crear_admin_por_defecto():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO usuarios (padre, estudiante, curso, promocion, correo, contrasena, tipo_usuario)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("-", "-", "-", "-", "juan.david.pereira.leon@gmail.com", "7719", "admin"))
    conn.commit()
    conn.close()

def crear_tablas():
    crear_tabla_usuarios()
    crear_tabla_metas()
    crear_tabla_ahorros()
    crear_tabla_salidas()
    crear_tabla_aportes()
    crear_tabla_ascensos()
    crear_admin_por_defecto()

crear_tabla = crear_tablas  # compatibilidad con código anterior

# -----------------------------
# FUNCIONES DE USUARIOS
# -----------------------------
def registrar_usuario(padre, estudiante, curso, promocion, correo, contrasena):
    try:
        patron = r"^[a-zA-Z0-9._%+-]+@(gmail\.com|hotmail\.com|outlook\.com|yahoo\.com|ngc\.edu\.co)$"
        if not re.match(patron, correo):
            print("❌ Correo inválido o dominio no permitido.")
            return False
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usuarios (padre, estudiante, curso, promocion, correo, contrasena, tipo_usuario)
            VALUES (?, ?, ?, ?, ?, ?, 'user')
        """, (padre, estudiante, curso, promocion, correo, contrasena))
        conn.commit()
        return True
    except Exception as e:
        print("❌ Error registrando usuario:", e)
        return False
    finally:
        conn.close()

def validar_login(correo, contrasena):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE correo = ? AND contrasena = ?", (correo, contrasena))
    user = cursor.fetchone()
    conn.close()
    return user

def obtener_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    data = cursor.fetchall()
    conn.close()
    return data
def obtener_usuario_por_correo(correo):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE correo = ?", (correo,))

    usuario = cursor.fetchone()
    conn.close()
    return usuario

# -----------------------------
# FUNCIONES DE METAS
# -----------------------------
def agregar_meta(curso, nombre, fecha, costo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO metas (curso, nombre, fecha, costo) VALUES (?, ?, ?, ?)",
                   (curso, nombre, fecha, costo))
    conn.commit()
    conn.close()

def obtener_metas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM metas")
    data = cursor.fetchall()
    conn.close()
    return data
def obtener_metas_por_curso(curso, usuario_id=None):
    """
    Devuelve las metas de un curso específico.
    Si se pasa usuario_id, se pueden filtrar solo las metas en las que ese usuario tiene ahorros o salidas.
    """
    conn = conectar()
    cursor = conn.cursor()
    if usuario_id is None:
        cursor.execute("SELECT * FROM metas WHERE curso = ?", (curso,))
    else:
        cursor.execute("""
            SELECT DISTINCT m.*
            FROM metas m
            LEFT JOIN ahorros a ON a.meta_id = m.id AND a.usuario_id = ?
            LEFT JOIN salidas s ON s.meta_id = m.id AND s.usuario_id = ?
            WHERE m.curso = ?
        """, (usuario_id, usuario_id, curso))
    data = cursor.fetchall()
    conn.close()
    return data

# -----------------------------
# AHORROS Y SALIDAS
# -----------------------------
def registrar_ahorro(meta_id, usuario_id, cantidad):
    conn = conectar()
    cursor = conn.cursor()
    fecha = datetime.now().strftime("%d/%m/%Y")
    cursor.execute("INSERT INTO ahorros (meta_id, usuario_id, cantidad, fecha) VALUES (?, ?, ?, ?)", (meta_id, usuario_id, cantidad, fecha))
    conn.commit()
    conn.close()

def registrar_salida(meta_id, usuario_id, cantidad):
    conn = conectar()
    cursor = conn.cursor()
    fecha = datetime.now().strftime("%d/%m/%Y")
    cursor.execute("INSERT INTO salidas (meta_id, usuario_id, cantidad, fecha) VALUES (?, ?, ?, ?)", (meta_id, usuario_id, cantidad, fecha))
    conn.commit()
    conn.close()
def obtener_total_ahorrado(meta_id, usuario_id=None):
    """
    Devuelve el total ahorrado para una meta específica.
    Si se pasa usuario_id, solo suma lo del usuario; si no, suma todos los usuarios.
    """
    conn = conectar()
    cursor = conn.cursor()
    if usuario_id is None:
        cursor.execute("SELECT SUM(cantidad) FROM ahorros WHERE meta_id = ?", (meta_id,))
    else:
        cursor.execute("SELECT SUM(cantidad) FROM ahorros WHERE meta_id = ? AND usuario_id = ?", (meta_id, usuario_id))
    resultado = cursor.fetchone()[0]
    conn.close()
    return resultado if resultado else 0.0

# -----------------------------
# FUNCIONES DE APORTES (CORREGIDAS)
# -----------------------------
def registrar_aporte(usuario_id, curso, cantidad):
    conn = conectar()
    cursor = conn.cursor()
    ahora = datetime.now()
    fecha = ahora.strftime("%d/%m/%Y")
    hora = ahora.strftime("%H:%M:%S")
    cursor.execute("INSERT INTO aportes (usuario_id, curso, cantidad, fecha, hora) VALUES (?, ?, ?, ?, ?)", (usuario_id, curso, cantidad, fecha, hora))
    conn.commit()
    conn.close()

def obtener_aportes_por_curso():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT curso, COUNT(DISTINCT usuario_id) as num_usuarios, SUM(cantidad) as total
        FROM aportes
        GROUP BY curso
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def obtener_aportes_detalle_por_curso(curso):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.estudiante, a.cantidad, a.curso, a.fecha, a.hora
        FROM aportes a
        JOIN usuarios u ON u.id = a.usuario_id
        WHERE a.curso = ?
    """, (curso,))
    data = cursor.fetchall()
    conn.close()
    return data

def obtener_aportes_por_usuario():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.estudiante, SUM(a.cantidad) as total, COUNT(a.id) as registros
        FROM usuarios u
        LEFT JOIN aportes a ON u.id = a.usuario_id
        GROUP BY u.id
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def obtener_aportes_detalle_por_usuario(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cantidad, curso, fecha, hora
        FROM aportes
        WHERE usuario_id = ?
    """, (usuario_id,))
    data = cursor.fetchall()
    conn.close()
    return data

# -----------------------------
# FUNCIONES DE ASCENSOS (CORREGIDAS)
# -----------------------------
def registrar_ascenso(usuario_id, curso_anterior, curso_nuevo):
    conn = conectar()
    cursor = conn.cursor()
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cursor.execute("INSERT INTO ascensos (usuario_id, curso_anterior, curso_nuevo, fecha) VALUES (?, ?, ?, ?)", (usuario_id, curso_anterior, curso_nuevo, fecha))
    cursor.execute("UPDATE usuarios SET curso = ? WHERE id = ?", (curso_nuevo, usuario_id))
    conn.commit()
    conn.close()

def obtener_ascensos_por_usuario(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ascensos WHERE usuario_id = ?", (usuario_id,))
    data = cursor.fetchall()
    conn.close()
    return data

# -----------------------------
# INIT
# -----------------------------
if __name__ == "__main__":
    crear_tablas()
    print("✅ Base de datos lista con todas las tablas y admin creado.")

    # ⚡ Datos de prueba
    conn = conectar()
    cur = conn.cursor()
    
    # Supongamos que hay un usuario y una meta
    cur.execute("SELECT id FROM usuarios WHERE correo='juan.david.pereira.leon@gmail.com'")
    usuario_id = cur.fetchone()[0]

    cur.execute("SELECT id FROM metas LIMIT 1")
    meta = cur.fetchone()
    if not meta:  # Si no hay meta, creamos una
        cur.execute("INSERT INTO metas (curso, nombre, fecha, costo) VALUES (?, ?, ?, ?)", ("11", "Viaje fin de curso", "31/12/2025", 1000.0))
        conn.commit()
        cur.execute("SELECT id FROM metas LIMIT 1")
        meta = cur.fetchone()
    meta_id = meta[0]

    # Registrar ahorro y salida de prueba
    registrar_ahorro(meta_id, usuario_id, 200.0)
    registrar_salida(meta_id, usuario_id, 50.0)
    print(f"Usuario {usuario_id} y meta {meta_id} con movimientos de prueba agregados")
    conn.close()

    crear_tablas()
    print("✅ Base de datos lista con todas las tablas y admin creado.")
    print("📂 Ubicación:", os.path.abspath(DB_FILE))
