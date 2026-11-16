"""Traducción al español con un traductor web gratuito (deep-translator)."""
import time


class Traductor:
    """Traduce textos sueltos y se rinde pronto si el servicio no responde."""

    MAX_FALLOS = 3

    def __init__(self):
        self._por_idioma = {}
        self.fallos_seguidos = 0

    @property
    def disponible(self):
        # Tras varios fallos seguidos lo normal es que no haya internet o que
        # el servicio nos esté limitando. Insistir solo lo empeora: se deja
        # el texto original y se reintenta en la próxima actualización.
        return self.fallos_seguidos < self.MAX_FALLOS

    def traducir(self, texto, idioma):
        if not texto or not self.disponible:
            return None
        try:
            if idioma not in self._por_idioma:
                from deep_translator import GoogleTranslator
                self._por_idioma[idioma] = GoogleTranslator(source=idioma, target="es")
            resultado = self._por_idioma[idioma].translate(texto[:4500])
            self.fallos_seguidos = 0
            time.sleep(0.3)  # pausa corta para no parecer un robot abusivo
            return resultado or None
        except Exception:
            self.fallos_seguidos += 1
            return None
