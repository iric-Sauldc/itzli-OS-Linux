"""Base de datos local (SQLite).

Todo se guarda en un solo archivo. Por eso la app funciona sin internet:
la ventana nunca lee de la red, solo de aquí.
"""
import sqlite3
from datetime import datetime, timedelta, timezone

from . import config

ESQUEMA = """
CREATE TABLE IF NOT EXISTS noticias (
    id              INTEGER PRIMARY KEY,
    tema            TEXT NOT NULL,
    fuente          TEXT NOT NULL,
    idioma          TEXT NOT NULL,
    enlace          TEXT NOT NULL UNIQUE,   -- UNIQUE impide guardar dos veces la misma
    fecha           TEXT NOT NULL,          -- en UTC, formato ISO: se ordena como texto
    titulo_original TEXT NOT NULL,
    resumen_original TEXT NOT NULL DEFAULT '',
    titulo          TEXT,                   -- en español; vacío = pendiente de traducir
    resumen         TEXT,
    duplicada_de    INTEGER,                -- id de la noticia principal si otro medio ya la publicó
    revisada        INTEGER NOT NULL DEFAULT 0,  -- ya pasó por el detector de repetidas
    favorita        INTEGER NOT NULL DEFAULT 0,
    leida           INTEGER NOT NULL DEFAULT 0,
    notificada      INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS cves (
    id              TEXT PRIMARY KEY,       -- por ejemplo CVE-2026-12345
    fecha           TEXT NOT NULL,
    gravedad        TEXT NOT NULL,          -- CRITICAL, HIGH, MEDIUM, LOW o SIN EVALUAR
    puntuacion      REAL,
    descripcion_original TEXT NOT NULL,
    descripcion     TEXT,
    enlace          TEXT NOT NULL,
    leida           INTEGER NOT NULL DEFAULT 0,
    notificada      INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS estado (clave TEXT PRIMARY KEY, valor TEXT);
CREATE INDEX IF NOT EXISTS noticias_fecha ON noticias(fecha);
"""


def conectar():
    config.DIR_DATOS.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(config.DIR_DATOS / "otearia.db", timeout=30)
    con.row_factory = sqlite3.Row  # permite leer columnas por nombre: fila["titulo"]
    con.executescript(ESQUEMA)
    # Columnas añadidas en versiones posteriores. Una base creada antes no las
    # tiene, y CREATE TABLE IF NOT EXISTS no modifica tablas que ya existen.
    try:
        con.execute("ALTER TABLE noticias ADD COLUMN resumen_ia TEXT")
    except sqlite3.OperationalError:
        pass  # ya existía
    return con


def ahora():
    return datetime.now(timezone.utc)


def iso(momento):
    return momento.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def guardar_estado(con, clave, valor):
    con.execute("INSERT OR REPLACE INTO estado VALUES (?, ?)", (clave, str(valor)))


def leer_estado(con, clave, defecto=""):
    fila = con.execute("SELECT valor FROM estado WHERE clave = ?", (clave,)).fetchone()
    return fila["valor"] if fila else defecto


def noticias(con, tema=None, solo_favoritas=False, limite=150):
    """Noticias principales (sin las repetidas), de la más nueva a la más antigua."""
    filtros, valores = ["duplicada_de IS NULL"], []
    if tema:
        filtros.append("tema = ?")
        valores.append(tema)
    if solo_favoritas:
        filtros.append("favorita = 1")
    sql = f"SELECT * FROM noticias WHERE {' AND '.join(filtros)} ORDER BY fecha DESC LIMIT ?"
    return con.execute(sql, (*valores, limite)).fetchall()


def otros_medios(con, noticia_id):
    return con.execute(
        "SELECT fuente, enlace FROM noticias WHERE duplicada_de = ? ORDER BY fecha", (noticia_id,)
    ).fetchall()


def cves(con, limite=200):
    return con.execute("SELECT * FROM cves ORDER BY fecha DESC LIMIT ?", (limite,)).fetchall()


def limpiar_antiguas(con, dias):
    limite = iso(ahora() - timedelta(days=dias))
    con.execute("DELETE FROM noticias WHERE fecha < ? AND favorita = 0", (limite,))
    con.execute("DELETE FROM cves WHERE fecha < ?", (limite,))
