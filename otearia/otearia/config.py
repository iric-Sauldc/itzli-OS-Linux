"""Lee la configuración del usuario."""
import os
import shutil
import tomllib
from pathlib import Path

DIR_CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "otearia"
DIR_DATOS = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "otearia"
ARCHIVO = DIR_CONFIG / "config.toml"
EJEMPLO = Path(__file__).parent / "config.ejemplo.toml"

TEMAS = {"ciberseguridad": "Ciberseguridad", "ia": "Inteligencia artificial", "innovacion": "Innovación en TI"}


def cargar():
    # La primera vez se copia el ejemplo, así el usuario tiene un archivo
    # comentado que editar en lugar de empezar de cero.
    if not ARCHIVO.exists():
        DIR_CONFIG.mkdir(parents=True, exist_ok=True)
        shutil.copy(EJEMPLO, ARCHIVO)
    with open(ARCHIVO, "rb") as f:
        cfg = tomllib.load(f)

    # Valores por defecto: si el usuario borra una línea, la app no se cae.
    cfg.setdefault("general", {})
    cfg["general"].setdefault("intervalo_minutos", 30)
    cfg["general"].setdefault("forma", "barra")
    cfg["general"].setdefault("dias_guardados", 30)
    cfg["general"].setdefault("max_traducciones", 60)
    cfg.setdefault("alertas", {})
    cfg["alertas"].setdefault("palabras", [])
    cfg["alertas"].setdefault("cve_criticas", True)
    cfg["alertas"].setdefault("puntuacion_minima", 9.0)
    cfg.setdefault("cve", {}).setdefault("dias", 3)
    cfg.setdefault("resumen_ia", {})
    cfg.setdefault("fuentes", [])
    return cfg
