-- Configuración de Hyprland para Itzli.
--
-- Desde la versión 0.55 Hyprland se configura con Lua (un lenguaje de
-- programación sencillo) y desde la 0.57 el formato antiguo hyprland.conf ya
-- no funciona. Si copias trozos de tutoriales viejos con líneas tipo
-- "bind = SUPER, Q, ..." no van a servir aquí.
--
-- Este archivo parte del ejemplo oficial y solo usa funciones que aparecen
-- en él. Referencia: https://wiki.hypr.land/configuring/
--
-- Tras cambiar algo, guarda el archivo: Hyprland lo recarga solo. Si hay un
-- error de sintaxis te avisa en pantalla y mantiene la configuración anterior.


---- MONITOR ----
-- "preferred" y "auto" dejan que Hyprland elija la resolución nativa de la
-- pantalla. Así funciona igual en un portátil que en una máquina virtual.
hl.monitor({
    output   = "",
    mode     = "preferred",
    position = "auto",
    scale    = "auto",
})


---- PROGRAMAS ----
-- Definidos una sola vez aquí arriba: si mañana cambias de terminal, tocas
-- una línea y todos los atajos siguen funcionando.
local terminal  = "kitty"
local archivos  = "thunar"
local navegador = "firefox"
local menu      = "fuzzel"
local ayuda     = "kitty --class ayuda less " .. os.getenv("HOME") .. "/.config/itzli/atajos.txt"
local captura   = "grim -g \"$(slurp)\" - | wl-copy"


---- ARRANQUE ----
-- Hyprland por sí solo es una pantalla vacía: no trae barra, ni
-- notificaciones, ni icono de wifi. Cada pieza es un programa aparte que hay
-- que lanzar al iniciar la sesión.
hl.on("hyprland.start", function()
    hl.exec_cmd("waybar")
    hl.exec_cmd("mako")
    hl.exec_cmd("nm-applet")
    hl.exec_cmd("systemctl --user start hyprpolkitagent")
    hl.exec_cmd("otearia inicio") -- abre el panel de noticias si así lo configuraste
end)


---- VARIABLES DE ENTORNO ----
hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")


---- APARIENCIA ----
-- Valores sobrios a propósito: poco desenfoque y animaciones cortas para que
-- vaya ligero en equipos modestos y en máquinas virtuales.
hl.config({
    general = {
        gaps_in     = 4,
        gaps_out    = 8,
        border_size = 2,

        col = {
            active_border   = "rgba(33ccffee)",
            inactive_border = "rgba(595959aa)",
        },

        -- Permite cambiar el tamaño de una ventana arrastrando su borde con
        -- el ratón, como en cualquier escritorio tradicional.
        resize_on_border = true,

        layout = "dwindle",
    },

    decoration = {
        rounding = 6,

        shadow = { enabled = false },

        blur = {
            enabled = true,
            size    = 3,
            passes  = 1,
        },
    },

    animations = {
        enabled = true,
    },

    dwindle = {
        preserve_split = true,
    },

    misc = {
        -- 0 quita los fondos de mascota anime que trae Hyprland por defecto.
        force_default_wallpaper = 0,
        disable_hyprland_logo   = true,
    },
})


---- TECLADO Y RATÓN ----
hl.config({
    input = {
        -- El instalador sustituye esta marca por latam, es o us.
        kb_layout = "__TECLADO__",

        follow_mouse = 1,

        touchpad = {
            natural_scroll = true,
        },
    },
})

-- Tres dedos a los lados en el touchpad para cambiar de espacio de trabajo.
hl.gesture({
    fingers   = 3,
    direction = "horizontal",
    action    = "workspace",
})


---- ATAJOS DE TECLADO ----
-- SUPER es la tecla con el logo de Windows. Si cambias algo aquí, actualiza
-- también ~/.config/itzli/atajos.txt, que es la chuleta de SUPER + F1.
local mod = "SUPER"

hl.bind(mod .. " + F1",     hl.dsp.exec_cmd(ayuda))
hl.bind(mod .. " + Return", hl.dsp.exec_cmd(terminal))
hl.bind(mod .. " + D",      hl.dsp.exec_cmd(menu))
hl.bind(mod .. " + E",      hl.dsp.exec_cmd(archivos))
hl.bind(mod .. " + B",      hl.dsp.exec_cmd(navegador))
hl.bind(mod .. " + A",      hl.dsp.exec_cmd("aprender"))    -- plataformas de práctica y documentación
hl.bind(mod .. " + P",      hl.dsp.exec_cmd("perfil menu")) -- entrar a un perfil instalado
hl.bind(mod .. " + N",      hl.dsp.exec_cmd("otearia"))   -- noticias (Otearia)
hl.bind(mod .. " + L",      hl.dsp.exec_cmd("hyprlock"))
hl.bind(mod .. " + Q",      hl.dsp.window.close())
hl.bind(mod .. " + V",      hl.dsp.window.float({ action = "toggle" }))
hl.bind(mod .. " + J",      hl.dsp.layout("togglesplit"))
hl.bind(mod .. " + SHIFT + S", hl.dsp.exec_cmd(captura))
hl.bind(mod .. " + SHIFT + M", hl.dsp.exec_cmd("hyprctl dispatch 'hl.dsp.exit()'"))

-- Mover el foco entre ventanas con las flechas.
hl.bind(mod .. " + left",  hl.dsp.focus({ direction = "left" }))
hl.bind(mod .. " + right", hl.dsp.focus({ direction = "right" }))
hl.bind(mod .. " + up",    hl.dsp.focus({ direction = "up" }))
hl.bind(mod .. " + down",  hl.dsp.focus({ direction = "down" }))

-- Espacios de trabajo del 1 al 10 (la tecla 0 es el 10).
for i = 1, 10 do
    local tecla = i % 10
    hl.bind(mod .. " + " .. tecla,         hl.dsp.focus({ workspace = i }))
    hl.bind(mod .. " + SHIFT + " .. tecla, hl.dsp.window.move({ workspace = i }))
end

-- Mover y redimensionar ventanas con SUPER + botones del ratón.
hl.bind(mod .. " + mouse:272", hl.dsp.window.drag(),   { mouse = true })
hl.bind(mod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- Teclas de volumen, brillo y multimedia del portátil.
-- "locked" hace que funcionen también con la pantalla bloqueada.
hl.bind("XF86AudioRaiseVolume",  hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+"), { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume",  hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"),      { locked = true, repeating = true })
hl.bind("XF86AudioMute",         hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),     { locked = true })
hl.bind("XF86MonBrightnessUp",   hl.dsp.exec_cmd("brightnessctl set 5%+"),                          { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("brightnessctl set 5%-"),                          { locked = true, repeating = true })
hl.bind("XF86AudioPlay",         hl.dsp.exec_cmd("playerctl play-pause"),                           { locked = true })
hl.bind("XF86AudioNext",         hl.dsp.exec_cmd("playerctl next"),                                 { locked = true })
hl.bind("XF86AudioPrev",         hl.dsp.exec_cmd("playerctl previous"),                             { locked = true })


---- REGLAS DE VENTANAS ----
-- Sin esta regla, una app que pide "maximizarse" rompe el mosaico.
hl.window_rule({
    name  = "ignorar-maximizar",
    match = { class = ".*" },

    suppress_event = "maximize",
})

-- La ventana de ayuda (SUPER + F1) sale flotando en vez de ocupar un hueco.
hl.window_rule({
    name  = "ayuda-flotante",
    match = { class = "ayuda" },

    float = true,
})

-- Otearia como ventana: flotante, para leer y cerrar sin desordenar el mosaico.
hl.window_rule({
    name  = "otearia-ventana",
    match = { class = "org.otearia.Ventana" },

    float = true,
})

-- Otearia como panel: flotante y pegado al borde derecho de la pantalla.
hl.window_rule({
    name  = "otearia-panel",
    match = { class = "org.otearia.Panel" },

    float = true,
    move  = "monitor_w-440 50",
})
