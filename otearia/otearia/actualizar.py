"""Una pasada completa: descargar, traducir, quitar repetidas y avisar."""
import subprocess
from datetime import timedelta

from . import alertas, db, duplicados, fuentes
from .traducir import Traductor


def _guardar_noticias(con, cfg, errores):
    nuevas = 0
    for fuente in cfg["fuentes"]:
        try:
            for n in fuentes.leer_fuente(fuente):
                # Las fuentes en español no necesitan traducción: el título
                # "traducido" es el mismo original.
                en_espanol = fuente.get("idioma", "en") == "es"
                cursor = con.execute(
                    """INSERT OR IGNORE INTO noticias
                       (tema, fuente, idioma, enlace, fecha, titulo_original, resumen_original, titulo, resumen)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (fuente["tema"], fuente["nombre"], fuente.get("idioma", "en"), n["enlace"], n["fecha"],
                     n["titulo"], n["resumen"],
                     n["titulo"] if en_espanol else None, n["resumen"] if en_espanol else None),
                )
                nuevas += cursor.rowcount
        except Exception as error:
            # Una fuente caída no debe impedir leer las demás.
            errores.append(f"{fuente['nombre']}: {error}")
    return nuevas


def _guardar_cves(con, cfg, errores):
    nuevas = 0
    try:
        for c in fuentes.leer_cves(cfg["cve"]["dias"]):
            cursor = con.execute(
                """INSERT OR IGNORE INTO cves (id, fecha, gravedad, puntuacion, descripcion_original, enlace)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (c["id"], c["fecha"], c["gravedad"], c["puntuacion"], c["descripcion"], c["enlace"]),
            )
            nuevas += cursor.rowcount
            # NVD suele publicar la CVE primero y puntuarla días después.
            if not cursor.rowcount and c["puntuacion"] is not None:
                con.execute("UPDATE cves SET gravedad = ?, puntuacion = ? WHERE id = ? AND puntuacion IS NULL",
                            (c["gravedad"], c["puntuacion"], c["id"]))
    except Exception as error:
        errores.append(f"NVD: {error}")
    return nuevas


def _traducir_pendientes(con, traductor, tope):
    """Traduce primero las noticias más nuevas y luego las CVE más graves."""
    hechas = 0
    for n in con.execute("SELECT * FROM noticias WHERE titulo IS NULL ORDER BY fecha DESC LIMIT ?", (tope,)).fetchall():
        titulo = traductor.traducir(n["titulo_original"], n["idioma"])
        if titulo is None:
            break
        resumen = traductor.traducir(n["resumen_original"], n["idioma"]) or n["resumen_original"]
        con.execute("UPDATE noticias SET titulo = ?, resumen = ? WHERE id = ?", (titulo, resumen, n["id"]))
        hechas += 1

    restantes = tope - hechas
    if restantes > 0 and traductor.disponible:
        for c in con.execute(
            "SELECT * FROM cves WHERE descripcion IS NULL ORDER BY puntuacion DESC NULLS LAST, fecha DESC LIMIT ?",
            (restantes,),
        ).fetchall():
            descripcion = traductor.traducir(c["descripcion_original"], "en")
            if descripcion is None:
                break
            con.execute("UPDATE cves SET descripcion = ? WHERE id = ?", (descripcion, c["id"]))
            hechas += 1
    return hechas


def _marcar_repetidas(con):
    """Si varios medios cuentan lo mismo, queda visible solo la primera."""
    desde = db.iso(db.ahora() - timedelta(days=4))
    # Se comparan los títulos ya en español, para emparejar también una
    # noticia en inglés con la misma publicada por un medio en español.
    principales = [
        (n["id"], duplicados.huella(n["titulo"]))
        for n in con.execute(
            "SELECT id, titulo FROM noticias WHERE revisada = 1 AND duplicada_de IS NULL AND fecha >= ? ORDER BY fecha",
            (desde,))
    ]
    repetidas = 0
    por_revisar = con.execute(
        "SELECT id, titulo FROM noticias WHERE revisada = 0 AND titulo IS NOT NULL ORDER BY fecha").fetchall()
    for n in por_revisar:
        huella = duplicados.huella(n["titulo"])
        original = next((pid for pid, h in principales if duplicados.parecidas(huella, h)), None)
        if original:
            con.execute("UPDATE noticias SET duplicada_de = ?, revisada = 1 WHERE id = ?", (original, n["id"]))
            repetidas += 1
        else:
            con.execute("UPDATE noticias SET revisada = 1 WHERE id = ?", (n["id"],))
            principales.append((n["id"], huella))
    return repetidas


def actualizar(cfg, traductor=None, avisar=alertas.notificar):
    con = db.conectar()
    errores = []
    # En la primera ejecución todo es "nuevo": avisar de todo sería una
    # avalancha de notificaciones, así que esa vez no se avisa.
    primera_vez = con.execute("SELECT COUNT(*) FROM noticias").fetchone()[0] == 0

    noticias_nuevas = _guardar_noticias(con, cfg, errores)
    cves_nuevas = _guardar_cves(con, cfg, errores)
    con.commit()  # se guarda ya: si la traducción tarda o falla, lo descargado no se pierde

    traducidas = _traducir_pendientes(con, traductor or Traductor(), cfg["general"]["max_traducciones"])
    repetidas = _marcar_repetidas(con)

    avisos = alertas.pendientes(con, cfg)
    if not primera_vez:
        alertas.enviar(avisos, avisar)

    db.limpiar_antiguas(con, cfg["general"]["dias_guardados"])
    db.guardar_estado(con, "ultima_actualizacion", db.iso(db.ahora()))
    db.guardar_estado(con, "errores", " | ".join(errores))
    con.commit()
    con.close()

    # Le pide a la barra que se redibuje ya, sin esperar a su siguiente turno.
    subprocess.run(["pkill", "-RTMIN+8", "waybar"], check=False, capture_output=True)
    return {"noticias": noticias_nuevas, "cves": cves_nuevas, "traducidas": traducidas,
            "repetidas": repetidas, "avisos": len(avisos), "errores": errores}
