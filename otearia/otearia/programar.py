"""Actualización automática con un temporizador de systemd.

Se usa systemd y no un bucle dentro de la app porque así se actualiza
aunque la ventana esté cerrada, y sin dejar un programa propio en memoria.
"""
import shutil
import subprocess
from pathlib import Path

SERVICIO = """[Unit]
Description=Otearia: descarga de noticias

[Service]
Type=oneshot
ExecStart={ejecutable} actualizar
"""

TEMPORIZADOR = """[Unit]
Description=Otearia: actualización cada {minutos} minutos

[Timer]
OnBootSec=2min
OnUnitActiveSec={minutos}min

[Install]
WantedBy=timers.target
"""


def programar(minutos):
    if minutos not in (15, 30, 60):
        raise SystemExit("intervalo_minutos debe ser 15, 30 o 60")
    carpeta = Path.home() / ".config/systemd/user"
    carpeta.mkdir(parents=True, exist_ok=True)
    ejecutable = shutil.which("otearia") or "/usr/local/bin/otearia"
    (carpeta / "otearia.service").write_text(SERVICIO.format(ejecutable=ejecutable))
    (carpeta / "otearia.timer").write_text(TEMPORIZADOR.format(minutos=minutos))
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    subprocess.run(["systemctl", "--user", "enable", "--now", "otearia.timer"], check=False)
    print(f"Otearia se actualizará sola cada {minutos} minutos.")
