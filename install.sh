#!/usr/bin/env bash
#
# Instalador de Itzli.
#
# Itzli se arma en dos capas:
#   1. El escritorio base: el proyecto de KooL / LinuxBeginnings, que instala y
#      mantiene Hyprland con su barra, menús, temas y pantalla de inicio.
#   2. Lo propio de Itzli, encima: los roles de seguridad, Otearia, el
#      laboratorio, las guías, el logo, el fondo y los colores.
#
# El escritorio base se descarga en el momento, no viene dentro de Itzli. Así
# siempre recibes su versión más reciente, que es la que sigue los cambios de
# Hyprland.
#
# Uso:
#   ./install.sh             instala todo
#   ./install.sh --simular   muestra lo que haría, sin tocar nada
#   ./install.sh --sin-base  solo la capa de Itzli (si el escritorio ya está)
#   ./install.sh --con-base  vuelve a pasar el instalador del escritorio base
set -euo pipefail

SIMULAR=false
BASE=auto
for opcion in "$@"; do
    case "$opcion" in
        --simular)  SIMULAR=true ;;
        --sin-base) BASE=no ;;
        --con-base) BASE=si ;;
        *) echo "Opción desconocida: $opcion"; exit 1 ;;
    esac
done

ORIGEN="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"
HYPR="$CONFIG/hypr"
ITZLI="$CONFIG/itzli"

BASE_REPO="${ITZLI_BASE_REPO:-https://github.com/LinuxBeginnings/Arch-Hyprland.git}"
BASE_DIR="${ITZLI_BASE_DIR:-$HOME/Arch-Hyprland}"

paso() { printf '\n\033[1;36m==> %s\033[0m\n' "$1"; }
nota() { printf '    %s\n' "$1"; }

# Todo comando que cambia el sistema pasa por aquí: así --simular funciona
# con una sola condición.
ejecutar() {
    if $SIMULAR; then
        printf '    [simulación] %s\n' "$*"
    else
        "$@"
    fi
}

if [[ $EUID -eq 0 ]]; then
    echo "No ejecutes esto como root. Usa tu usuario normal (se pedirá sudo cuando haga falta)."
    exit 1
fi
if ! command -v pacman >/dev/null 2>&1 && ! $SIMULAR; then
    echo "No encuentro pacman. Este instalador es solo para Arch Linux."
    exit 1
fi

# ---------------------------------------------------------------------------
paso "1/8  Escritorio base"

# La carpeta UserConfigs solo existe si el escritorio base ya se instaló.
if [[ "$BASE" == auto ]]; then
    if [[ -d "$HYPR/UserConfigs" ]]; then BASE=no; else BASE=si; fi
fi

if [[ "$BASE" == si ]]; then
    ejecutar sudo pacman -Syu --needed --noconfirm git base-devel

    if [[ -d "$BASE_DIR/.git" ]]; then
        nota "Actualizando el instalador del escritorio base en $BASE_DIR"
        ejecutar git -C "$BASE_DIR" pull --ff-only
    else
        nota "Descargando el instalador del escritorio base"
        ejecutar git clone --depth=1 "$BASE_REPO" "$BASE_DIR"
    fi

    cat <<'AVISO'

    Ahora se abre el instalador del escritorio base. Es interactivo y está en
    inglés. Qué contestar:

      - Ayudante de AUR: marca "yay" con la barra espaciadora y pulsa Enter.
      - Lista de opciones: ya vienen marcadas las de Itzli. Solo pulsa Enter.
        (Si tu equipo tiene tarjeta NVIDIA, marca también "nvidia".)
      - "Are you happy with these choices?": Yes.
      - Preguntas de la configuración (teclado, resolución, hora): elige lo
        tuyo. Para el teclado latinoamericano escribe: latam
      - Si ofrece descargar más fondos de pantalla (1 GB): n
      - "Would you like to reboot now?":  n   <- importante, falta la parte de Itzli

AVISO
    if ! $SIMULAR; then
        read -r -p "    Pulsa Enter para empezar... " _
    fi
    # Se entra a su carpeta porque su instalador busca sus archivos con rutas
    # relativas. El paréntesis hace que el "cd" no afecte al resto del script.
    if $SIMULAR; then
        nota "[simulación] (cd $BASE_DIR && ./install.sh --preset $ORIGEN/base/preset.conf)"
    else
        (cd "$BASE_DIR" && ./install.sh --preset "$ORIGEN/base/preset.conf")
    fi

    if ! $SIMULAR && [[ ! -d "$HYPR/UserConfigs" ]]; then
        echo
        echo "El escritorio base no terminó de instalarse (falta $HYPR/UserConfigs)."
        echo "Revisa los mensajes de arriba y los registros en $BASE_DIR/Install-Logs,"
        echo "y vuelve a ejecutar ./install.sh cuando esté resuelto."
        exit 1
    fi
else
    nota "El escritorio base ya está instalado; se omite. (Fuérzalo con --con-base.)"
fi

# ---------------------------------------------------------------------------
paso "2/8  Paquetes propios de Itzli"
PAQUETES=(
    podman      # el motor que ejecuta los contenedores, sin necesitar root
    distrobox   # la capa que integra esos contenedores con tu escritorio
    xdg-utils   # trae xdg-open, que abre enlaces en el navegador
    libnotify   # trae notify-send, para las notificaciones
    kitty       # la terminal donde se abren la ayuda y los perfiles
    firefox     # navegador, para el menú de aprendizaje
)
ejecutar sudo pacman -S --needed --noconfirm "${PAQUETES[@]}"

# ---------------------------------------------------------------------------
paso "3/8  Comandos, perfiles y guías"
nota "Los comandos van en /usr/local/bin, que ya está en el PATH."
for comando in perfil aprender laboratorio itzli-menu; do
    ejecutar sudo install -m 755 "$ORIGEN/$comando" "/usr/local/bin/$comando"
done
ejecutar mkdir -p "$ITZLI/perfiles" "$ITZLI/guias" "$ITZLI/hypr"
# --update=none: no pisa perfiles ni listas que tú ya hayas modificado.
ejecutar cp --update=none "$ORIGEN"/perfiles/*.perfil "$ITZLI/perfiles/"
ejecutar cp --update=none "$ORIGEN/config/aprender.txt" "$ITZLI/aprender.txt"
ejecutar cp "$ORIGEN"/config/guias/*.md "$ITZLI/guias/"
ejecutar cp "$ORIGEN/config/atajos.txt" "$ITZLI/atajos.txt"

# ---------------------------------------------------------------------------
paso "4/8  Otearia, el radar de noticias"
ejecutar bash "$ORIGEN/otearia/instalar.sh"

# ---------------------------------------------------------------------------
paso "5/8  Integración con el escritorio"
nota "El escritorio base reserva la carpeta UserConfigs para ajustes del usuario"
nota "y no la pisa al actualizarse. Itzli añade ahí tres líneas que cargan sus"
nota "propios archivos, en vez de modificar los del escritorio."
ejecutar cp "$ORIGEN"/hypr/*.lua "$ITZLI/hypr/"

# Añade al final de un archivo del escritorio un bloque que carga un archivo
# de Itzli. Va envuelto en pcall: si un día el archivo de Itzli falla, el
# escritorio arranca igual, solo sin ese añadido.
enganchar() {
    local destino="$HYPR/UserConfigs/$1" fragmento="$2" argumentos="$3"
    if $SIMULAR; then
        nota "[simulación] añadir a $1 la carga de $fragmento"
        return
    fi
    if [[ ! -f "$destino" ]]; then
        nota "No encuentro $1; se omite esa integración."
        return
    fi
    if grep -q '>>> Itzli' "$destino"; then
        nota "$1 ya cargaba lo de Itzli."
        return
    fi
    cat >> "$destino" <<EOF

-- >>> Itzli (no borres este bloque: carga los ajustes de ~/.config/itzli/hypr)
do
  local ruta = (os.getenv("HOME") or "") .. "/.config/itzli/hypr/$fragmento"
  local ok, extra = pcall(dofile, ruta)
  if ok and type(extra) == "function" then
    pcall(extra, $argumentos)
  end
end
-- <<< Itzli
EOF
    nota "$1 ahora carga $fragmento"
}
enganchar user_keybinds.lua     atajos.lua   "bind, exec_cmd"
enganchar user_startup.lua      arranque.lua "exec_once"
enganchar user_window_rules.lua ventanas.lua "apply_window_rule"

# ---------------------------------------------------------------------------
paso "6/8  Otearia en la barra"
BARRA="$HYPR/waybar"
if $SIMULAR; then
    nota "[simulación] crear un diseño de barra con el módulo de Otearia"
elif [[ ! -e "$BARRA/config" || ! -f "$BARRA/UserModules" ]]; then
    nota "No encuentro la barra del escritorio base; se omite."
else
    # El módulo se define en UserModules, el archivo que el escritorio reserva
    # para módulos del usuario.
    if ! grep -q '"custom/otearia"' "$BARRA/UserModules"; then
        sed -i '0,/^{[[:space:]]*$/s//{\n"custom\/otearia": {\n\t"exec": "otearia barra",\n\t"return-type": "json",\n\t"interval": 120,\n\t"signal": 8,\n\t"on-click": "otearia ventana"\n},/' "$BARRA/UserModules"
    fi
    # Definirlo no basta: hay que nombrarlo en un diseño. Se copia el diseño
    # que esté en uso con el módulo añadido a la derecha, y se activa la copia.
    # El original queda intacto.
    actual="$(readlink -f "$BARRA/config")"
    if grep -q '"custom/otearia"' "$actual"; then
        nota "El diseño de barra en uso ya incluye Otearia."
    else
        nuevo="$BARRA/configs/$(basename "$actual")-Itzli"
        sed '0,/"modules-right": \[/s//"modules-right": [\n\t"custom\/otearia",\n\t"custom\/separator#dot-line",/' "$actual" > "$nuevo"
        ln -sf "$nuevo" "$BARRA/config"
        nota "Diseño de barra activo: $(basename "$nuevo")"
    fi
fi

# ---------------------------------------------------------------------------
paso "7/8  Fondo, colores y pantalla de inicio"
IMAGENES="$(xdg-user-dir PICTURES 2>/dev/null || echo "$HOME/Pictures")"
ejecutar mkdir -p "$IMAGENES/wallpapers"
ejecutar cp "$ORIGEN/fondos/itzli.jpg" "$IMAGENES/wallpapers/itzli.jpg"

# El escritorio base saca los colores de toda la interfaz a partir del fondo
# de pantalla. Dejando el fondo de Itzli como "fondo actual" y pidiéndole que
# repita su arranque inicial, todo sale en azules sin tocar ningún tema.
# Solo se hace la primera vez, para no deshacer un fondo que elijas después.
if [[ ! -f "$ITZLI/.aspecto-aplicado" ]]; then
    ejecutar mkdir -p "$HYPR/wallpaper_effects"
    ejecutar cp "$ORIGEN/fondos/itzli.jpg" "$HYPR/wallpaper_effects/.wallpaper_current"
    ejecutar rm -f "$HYPR/.initial_startup_done"
    ejecutar touch "$ITZLI/.aspecto-aplicado"
else
    nota "El aspecto de Itzli ya se aplicó antes; se respeta tu fondo actual."
fi

TEMA_INICIO=/usr/share/sddm/themes/simple_sddm_2
if $SIMULAR || [[ -d "$TEMA_INICIO" ]]; then
    nota "theme.conf.user se lee después del theme.conf del tema: los valores"
    nota "de Itzli ganan y el tema original no se modifica."
    ejecutar sudo install -Dm 644 "$ORIGEN/fondos/itzli-inicio.jpg" "$TEMA_INICIO/Backgrounds/itzli.jpg"
    ejecutar sudo install -Dm 644 "$ORIGEN/sddm/theme.conf.user" "$TEMA_INICIO/theme.conf.user"
else
    nota "No está el tema de inicio del escritorio base; se omite."
fi

for logo in itzli itzli-pequeno itzli-mono; do
    ejecutar sudo install -Dm 644 "$ORIGEN/iconos/$logo.svg" "/usr/share/pixmaps/$logo.svg"
done

# ---------------------------------------------------------------------------
paso "8/8  Contenedores sin root"
nota "Podman necesita un rango de 'sub-usuarios' para que root DENTRO del"
nota "contenedor sea un usuario sin poderes FUERA de él."
if $SIMULAR || ! grep -q "^$USER:" /etc/subuid 2>/dev/null; then
    ejecutar sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 "$USER"
else
    nota "Ya estaba configurado."
fi

cat <<'FIN'

Listo. Reinicia con:  sudo reboot

Dentro del escritorio:
  SUPER + H        todos los atajos del escritorio
  SUPER + F1       ayuda y atajos propios de Itzli
  SUPER + N        noticias y vulnerabilidades (Otearia)
  SUPER + ALT + A  menú de aprendizaje y guías
  SUPER + ALT + I  entrar a un perfil de herramientas
  perfil listar    en una terminal, los roles disponibles
FIN
