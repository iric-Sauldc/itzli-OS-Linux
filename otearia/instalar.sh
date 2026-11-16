#!/usr/bin/env bash
#
# Instala Otearia para tu usuario. Lo llama el instalador de la distro,
# pero también puedes ejecutarlo solo para reinstalar o actualizar la app.
set -euo pipefail

ORIGEN="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATOS="${XDG_DATA_HOME:-$HOME/.local/share}/otearia"

echo "==> Dependencias del sistema"
# python-gobject y gtk4: la ventana. python-feedparser: leer RSS.
# libnotify: el comando notify-send para las alertas.
sudo pacman -S --needed --noconfirm python python-gobject gtk4 python-feedparser libnotify

echo "==> Entorno de Python propio"
# La librería de traducción no está en los repositorios de Arch, y Arch no
# deja usar pip sobre el Python del sistema (podría romper otros programas).
# La solución estándar es un "entorno virtual": una carpeta con sus propias
# librerías. --system-site-packages le deja ver además las de pacman (GTK).
python -m venv --system-site-packages "$DATOS/venv"
"$DATOS/venv/bin/pip" install --quiet --upgrade deep-translator

echo "==> Copiando la aplicación"
rm -rf "$DATOS/app"
mkdir -p "$DATOS/app"
cp -r "$ORIGEN/otearia" "$DATOS/app/"

# El lanzador es lo que hace que exista el comando "otearia".
lanzador="$(mktemp)"
cat > "$lanzador" <<'LANZADOR'
#!/bin/sh
DATOS="${XDG_DATA_HOME:-$HOME/.local/share}/otearia"
PYTHONPATH="$DATOS/app" exec "$DATOS/venv/bin/python" -m otearia "$@"
LANZADOR
sudo install -m 755 "$lanzador" /usr/local/bin/otearia
rm -f "$lanzador"

echo "==> Icono y entrada en el menú de aplicaciones"
# El archivo .desktop es lo que hace que Otearia aparezca en el menú (SUPER + D).
# Se llama igual que el identificador de la ventana para que el sistema sepa
# qué icono mostrarle.
ICONOS="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/scalable/apps"
MENU="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
mkdir -p "$ICONOS" "$MENU"
cp "$ORIGEN/../iconos/otearia.svg" "$ICONOS/org.otearia.Ventana.svg"
cat > "$MENU/org.otearia.Ventana.desktop" <<'ENTRADA'
[Desktop Entry]
Type=Application
Name=Otearia
Comment=Noticias de tecnología y vulnerabilidades en español
Exec=otearia
Icon=org.otearia.Ventana
Categories=Network;News;
ENTRADA

echo "==> Actualización automática"
otearia programar || echo "    No se pudo activar ahora; tras reiniciar ejecuta: otearia programar"

echo "Otearia instalado. Ábrelo con SUPER + N o escribiendo: otearia"
