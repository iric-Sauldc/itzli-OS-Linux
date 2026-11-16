"""Texto para el módulo de la barra (waybar)."""
import json
from datetime import timedelta
from html import escape

from . import db


def salida():
    con = db.conectar()
    sin_leer = con.execute("SELECT COUNT(*) FROM noticias WHERE leida = 0 AND duplicada_de IS NULL").fetchone()[0]
    desde = db.iso(db.ahora() - timedelta(days=1))
    criticas = con.execute(
        "SELECT COUNT(*) FROM cves WHERE leida = 0 AND gravedad = 'CRITICAL' AND fecha >= ?", (desde,)).fetchone()[0]
    ultimas = db.noticias(con, limite=5)
    actualizado = db.leer_estado(con, "ultima_actualizacion", "nunca")
    con.close()

    texto = f"Noticias {sin_leer}"
    if criticas:
        texto += f" · CVE críticas {criticas}"
    lineas = [f"Última actualización: {actualizado}"] + ["• " + (n["titulo"] or n["titulo_original"]) for n in ultimas]
    # waybar interpreta el texto como marcado, así que se escapan < > &
    return json.dumps({
        "text": escape(texto),
        "tooltip": escape("\n".join(lineas)),
        "class": "critico" if criticas else ("nuevo" if sin_leer else "vacio"),
    }, ensure_ascii=False)
