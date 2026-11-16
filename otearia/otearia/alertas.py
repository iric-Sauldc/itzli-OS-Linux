"""Notificaciones de escritorio para lo urgente."""
import shutil
import subprocess

MAX_AVISOS = 5  # más de esto en una tanda es ruido, no información


def notificar(titulo, cuerpo, urgente=False):
    if not shutil.which("notify-send"):
        print(f"[aviso] {titulo}: {cuerpo}")
        return
    subprocess.run(
        ["notify-send", "--app-name=Otearia", f"--urgency={'critical' if urgente else 'normal'}",
         titulo, cuerpo],
        check=False,
    )


def pendientes(con, cfg):
    """Devuelve los avisos por enviar y marca todo como ya notificado."""
    avisos = []
    palabras = [p.lower() for p in cfg["alertas"]["palabras"] if p.strip()]

    for n in con.execute("SELECT * FROM noticias WHERE notificada = 0 AND duplicada_de IS NULL"):
        texto = " ".join(filter(None, [n["titulo_original"], n["titulo"], n["resumen_original"]])).lower()
        encontrada = next((p for p in palabras if p in texto), None)
        if encontrada:
            avisos.append((f"Mención de «{encontrada}»", n["titulo"] or n["titulo_original"], False))

    if cfg["alertas"]["cve_criticas"]:
        minimo = cfg["alertas"]["puntuacion_minima"]
        for c in con.execute(
            "SELECT * FROM cves WHERE notificada = 0 AND puntuacion >= ? ORDER BY puntuacion DESC", (minimo,)
        ):
            descripcion = c["descripcion"] or c["descripcion_original"]
            avisos.append((f"Vulnerabilidad crítica {c['id']} ({c['puntuacion']})", descripcion[:200], True))

    con.execute("UPDATE noticias SET notificada = 1 WHERE notificada = 0")
    con.execute("UPDATE cves SET notificada = 1 WHERE notificada = 0")
    return avisos


def enviar(avisos, avisar=notificar):
    for titulo, cuerpo, urgente in avisos[:MAX_AVISOS]:
        avisar(titulo, cuerpo, urgente)
    if len(avisos) > MAX_AVISOS:
        avisar("Otearia", f"Y {len(avisos) - MAX_AVISOS} alertas más. Abre la app para verlas.", False)
