#!/usr/bin/env bash
#
# Instalador de Itzli.
#
# Qué hace: convierte un Arch Linux recién instalado (sin escritorio) en un
# sistema con Hyprland listo para usar y con el comando "perfil" para instalar
# herramientas de seguridad dentro de contenedores.
#
# Uso:
#   ./install.sh            instala de verdad
#   ./install.sh --simular  solo muestra lo que haría, sin tocar nada
#
# "set -euo pipefail" hace que el script se detenga al primer error en vez de
# seguir adelante con el sistema a medias. Es la red de seguridad de casi
# cualquier script de Bash serio.
set -euo pipefail

SIMULAR=false
[[ "${1:-}" == "--simular" ]] && SIMULAR=true

# Carpeta donde vive este script, para encontrar los archivos que lo acompañan
# sin importar desde dónde lo ejecutes.
ORIGEN="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"

# --- Funciones pequeñas de apoyo -------------------------------------------

paso() { printf '\n\033[1;36m==> %s\033[0m\n' "$1"; }
nota() { printf '    %s\n' "$1"; }

# Todo comando que cambia el sistema pasa por aquí. Así el modo --simular
# funciona con una sola condición en lugar de repetirla por todo el script.
ejecutar() {
    if $SIMULAR; then
        printf '    [simulación] %s\n' "$*"
    else
        "$@"
    fi
}

# --- Comprobaciones antes de empezar ---------------------------------------

# No se ejecuta como root porque la configuración va en TU carpeta personal.
# Para lo que sí necesita permisos se usa sudo, solo en esos comandos.
if [[ $EUID -eq 0 ]]; then
    echo "No ejecutes esto como root. Usa tu usuario normal (se pedirá sudo cuando haga falta)."
    exit 1
fi

if ! command -v pacman >/dev/null 2>&1 && ! $SIMULAR; then
    echo "No encuentro pacman. Este instalador es solo para Arch Linux."
    exit 1
fi

# --- Paquetes ---------------------------------------------------------------
# Están agrupados por función para que sepas qué quitar o cambiar.

ESCRITORIO=(
    hyprland                    # el compositor: dibuja y acomoda las ventanas
    xdg-desktop-portal-hyprland # permite compartir pantalla y abrir diálogos de archivos
    hyprpolkitagent             # la ventanita que pide tu contraseña cuando una app necesita permisos
    hyprlock                    # bloqueo de pantalla
    waybar                      # la barra superior (reloj, red, batería)
    fuzzel                      # el menú para buscar y abrir aplicaciones
    mako libnotify              # notificaciones (libnotify trae el comando notify-send)
    xdg-utils                   # trae xdg-open, que abre enlaces en el navegador
    sddm                        # pantalla gráfica de inicio de sesión
    qt5-wayland qt6-wayland     # para que las apps hechas con Qt se vean bien en Wayland
)

APLICACIONES=(
    kitty     # terminal
    thunar    # explorador de archivos
    firefox   # navegador
)

SISTEMA=(
    networkmanager network-manager-applet # wifi y red, con icono en la barra
    pipewire pipewire-pulse wireplumber   # sonido
    brightnessctl playerctl               # teclas de brillo y multimedia del portátil
    grim slurp wl-clipboard               # capturas de pantalla y portapapeles
    noto-fonts ttf-jetbrains-mono-nerd    # fuentes (la "nerd" trae los iconos de la barra)
)

CONTENEDORES=(
    podman    # el motor que ejecuta los contenedores, sin necesitar root
    distrobox # la capa que integra esos contenedores con tu escritorio
)

paso "1/6  Instalando paquetes"
nota "--needed evita reinstalar lo que ya tienes; -Syu actualiza todo primero,"
nota "porque en Arch instalar sin actualizar puede romper dependencias."
ejecutar sudo pacman -Syu --needed --noconfirm \
    "${ESCRITORIO[@]}" "${APLICACIONES[@]}" "${SISTEMA[@]}" "${CONTENEDORES[@]}"

# --- Teclado ----------------------------------------------------------------

paso "2/6  Distribución del teclado"
TECLADO="latam"
if ! $SIMULAR; then
    echo "    1) Latinoamérica (latam)   2) España (es)   3) Inglés EE. UU. (us)"
    read -r -p "    Elige [1]: " opcion
    case "${opcion:-1}" in
        2) TECLADO="es" ;;
        3) TECLADO="us" ;;
        *) TECLADO="latam" ;;
    esac
fi
nota "Teclado elegido: $TECLADO"

# --- Configuración del escritorio ------------------------------------------

paso "3/6  Copiando la configuración de Hyprland y la barra"

# Si ya tenías una configuración, se guarda una copia con la fecha en vez de
# pisarla. Nunca borres la configuración de alguien sin dejarle vuelta atrás.
respaldar() {
    local carpeta="$1"
    if [[ -e "$carpeta" ]]; then
        local copia
        copia="$carpeta.respaldo-$(date +%Y%m%d-%H%M%S)"
        nota "Ya existía $carpeta, la guardo como $copia"
        ejecutar mv "$carpeta" "$copia"
    fi
}

respaldar "$CONFIG/hypr"
respaldar "$CONFIG/waybar"

ejecutar mkdir -p "$CONFIG/hypr" "$CONFIG/waybar" "$CONFIG/itzli/perfiles"
ejecutar cp "$ORIGEN/config/hypr/hyprland.lua" "$CONFIG/hypr/hyprland.lua"
ejecutar cp "$ORIGEN/config/waybar/config.jsonc" "$CONFIG/waybar/config.jsonc"
ejecutar cp "$ORIGEN/config/atajos.txt" "$CONFIG/itzli/atajos.txt"
# El logo queda en una ruta del sistema para usarlo luego en la pantalla de
# inicio de sesión y en la ISO.
ejecutar sudo install -Dm 644 "$ORIGEN/iconos/itzli.svg" /usr/share/pixmaps/itzli.svg
# La versión pequeña es para barras y menús; la de un solo color, para
# fondos, arranque o impresión.
ejecutar sudo install -Dm 644 "$ORIGEN/iconos/itzli-pequeno.svg" /usr/share/pixmaps/itzli-pequeno.svg
ejecutar sudo install -Dm 644 "$ORIGEN/iconos/itzli-mono.svg" /usr/share/pixmaps/itzli-mono.svg

# Sustituye la marca del teclado en la copia ya instalada, no en el original.
ejecutar sed -i "s/__TECLADO__/$TECLADO/" "$CONFIG/hypr/hyprland.lua"

# --- Perfiles ---------------------------------------------------------------

paso "4/6  Instalando el comando 'perfil' y los perfiles de herramientas"
nota "El comando va en /usr/local/bin porque esa carpeta ya está en el PATH,"
nota "o sea, podrás escribir 'perfil' desde cualquier terminal."
ejecutar sudo install -m 755 "$ORIGEN/perfil" /usr/local/bin/perfil
ejecutar sudo install -m 755 "$ORIGEN/aprender" /usr/local/bin/aprender
ejecutar sudo install -m 755 "$ORIGEN/laboratorio" /usr/local/bin/laboratorio
ejecutar mkdir -p "$CONFIG/itzli/guias"
ejecutar cp "$ORIGEN"/config/guias/*.md "$CONFIG/itzli/guias/"
# -n: si ya personalizaste tu lista de aprendizaje, no se sobrescribe.
ejecutar cp -n "$ORIGEN/config/aprender.txt" "$CONFIG/itzli/aprender.txt"
# -n: no sobrescribe perfiles que tú ya hayas modificado.
ejecutar cp -n "$ORIGEN"/perfiles/*.perfil "$CONFIG/itzli/perfiles/"

# --- Contenedores sin root --------------------------------------------------

paso "Otearia, el radar de noticias"
nota "Tiene su propio instalador para poder actualizarlo por separado."
ejecutar bash "$ORIGEN/otearia/instalar.sh"

paso "5/6  Preparando los contenedores sin root"
nota "Podman necesita un rango de 'sub-usuarios' para que root DENTRO del"
nota "contenedor sea un usuario sin poderes FUERA de él."
if $SIMULAR || ! grep -q "^$USER:" /etc/subuid 2>/dev/null; then
    ejecutar sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 "$USER"
else
    nota "Ya estaba configurado."
fi

# --- Servicios --------------------------------------------------------------

paso "6/6  Activando servicios"
nota "'enable' los arranca en cada inicio. SDDM no se inicia ahora mismo para"
nota "no cortarte la sesión a mitad de la instalación."
ejecutar sudo systemctl enable NetworkManager.service
ejecutar sudo systemctl enable sddm.service

cat <<'FIN'

Listo. Reinicia con:  sudo reboot

Al volver verás la pantalla de inicio de sesión. Elige la sesión "Hyprland".
Dentro del escritorio:
  SUPER + F1      muestra todos los atajos de teclado
  SUPER + Enter   abre una terminal
  perfil listar   muestra los perfiles de herramientas disponibles
FIN
