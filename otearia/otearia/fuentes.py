"""Descarga noticias (RSS) y vulnerabilidades (NVD)."""
import html
import json
import os
import re
import urllib.parse
import urllib.request
from calendar import timegm
from datetime import datetime, timedelta, timezone

import feedparser

from . import db

# Algunos sitios (CISA entre ellos) rechazan peticiones sin identificación.
AGENTE = "Otearia/0.1 (lector de noticias)"
NVD = os.environ.get("OTEARIA_NVD_URL", "https://services.nvd.nist.gov/rest/json/cves/2.0")


def descargar(url, espera=25):
    peticion = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    with urllib.request.urlopen(peticion, timeout=espera) as respuesta:
        return respuesta.read()


def texto_limpio(texto, maximo=600):
    """Quita las etiquetas HTML que muchos RSS meten en el resumen."""
    texto = re.sub(r"<[^>]+>", " ", texto or "")
    texto = re.sub(r"\s+", " ", html.unescape(texto)).strip()
    return texto if len(texto) <= maximo else texto[:maximo].rsplit(" ", 1)[0] + "…"


def leer_fuente(fuente):
    """Devuelve las noticias de una fuente como lista de diccionarios."""
    datos = feedparser.parse(descargar(fuente["url"]))
    if datos.bozo and not datos.entries:
        raise ValueError("la respuesta no es un RSS válido")

    noticias = []
    for entrada in datos.entries:
        enlace, titulo = entrada.get("link"), texto_limpio(entrada.get("title"), 300)
        if not enlace or not titulo:
            continue
        # feedparser ya convierte la fecha a UTC; si la fuente no trae fecha
        # se usa el momento de la descarga.
        partes = entrada.get("published_parsed") or entrada.get("updated_parsed")
        fecha = datetime.fromtimestamp(timegm(partes), timezone.utc) if partes else db.ahora()
        noticias.append({
            "enlace": enlace,
            "titulo": titulo,
            "resumen": texto_limpio(entrada.get("summary")),
            "fecha": db.iso(min(fecha, db.ahora())),  # hay fuentes con fechas en el futuro
        })
    return noticias


def _gravedad(metricas):
    # Una CVE puede venir puntuada con varias versiones de CVSS. Se toma la
    # más moderna que exista.
    for version in ("cvssMetricV40", "cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        for metrica in metricas.get(version, []):
            datos = metrica.get("cvssData", {})
            gravedad = datos.get("baseSeverity") or metrica.get("baseSeverity")
            if gravedad:
                return gravedad.upper(), datos.get("baseScore")
    return "SIN EVALUAR", None


def leer_cves(dias):
    """Consulta las CVE publicadas en los últimos días en la base NVD."""
    url = NVD
    if url.startswith("http"):
        fin = db.ahora()
        formato = "%Y-%m-%dT%H:%M:%S.000"
        url += "?" + urllib.parse.urlencode({
            "pubStartDate": (fin - timedelta(days=dias)).strftime(formato),
            "pubEndDate": fin.strftime(formato),
        })
    respuesta = json.loads(descargar(url, espera=60))

    cves = []
    for elemento in respuesta.get("vulnerabilities", []):
        cve = elemento.get("cve", {})
        if not cve.get("id") or cve.get("vulnStatus") == "Rejected":
            continue
        descripcion = next((d["value"] for d in cve.get("descriptions", []) if d.get("lang") == "en"), "")
        gravedad, puntuacion = _gravedad(cve.get("metrics", {}))
        cves.append({
            "id": cve["id"],
            "fecha": cve.get("published", "")[:19] + "Z",
            "gravedad": gravedad,
            "puntuacion": puntuacion,
            "descripcion": texto_limpio(descripcion, 900),
            "enlace": "https://nvd.nist.gov/vuln/detail/" + cve["id"],
        })
    return cves
