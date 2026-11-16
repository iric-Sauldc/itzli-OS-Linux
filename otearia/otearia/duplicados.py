"""Detecta cuándo dos medios publican la misma noticia."""
import re
import unicodedata

# Palabras que no distinguen una noticia de otra.
VACIAS = set("""
de la el en y a los las del un una por con para que se su al es lo como mas o
sus le ya este esta entre sin sobre tras nuevo nueva nuevos nuevas segun
the of and to in for on with by from at is are new how why after says
""".split())

PARECIDO_MINIMO = 0.6


def huella(titulo):
    """Reduce un título a su conjunto de palabras significativas."""
    sin_acentos = unicodedata.normalize("NFKD", titulo.lower()).encode("ascii", "ignore").decode()
    palabras = re.findall(r"[a-z0-9]+", sin_acentos)
    return frozenset(p for p in palabras if len(p) > 2 and p not in VACIAS)


def parecidas(a, b):
    """Compara dos huellas: palabras en común dividido entre palabras totales."""
    # Con títulos muy cortos cualquier coincidencia parecería un duplicado.
    if len(a) < 3 or len(b) < 3:
        return False
    return len(a & b) / len(a | b) >= PARECIDO_MINIMO
