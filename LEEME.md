# Itzli

Arch Linux con Hyprland, pensado para aprender ciberseguridad. Las herramientas no se instalan en el sistema: van en contenedores, agrupadas por perfil.

Esta es la versión 0.1. Todavía no es una ISO propia; es un instalador que se ejecuta sobre un Arch recién instalado. Así se puede probar y corregir rápido antes de empaquetarlo como distro.

## Cómo probarlo (en una máquina virtual)

Pruébalo primero en una máquina virtual (VirtualBox, VMware o GNOME Boxes), no en tu equipo real. Activa la aceleración 3D en la máquina virtual: Hyprland la necesita para dibujar.

1. Descarga la ISO de Arch desde archlinux.org y arranca la máquina virtual con ella.
2. Escribe `archinstall`. Es el instalador guiado oficial: te pregunta disco, usuario y contraseña. En el tipo de instalación elige **Minimal** (sin escritorio, porque el nuestro lo pone el script) y en red elige **NetworkManager**. Crea tu usuario con permisos de administrador (sudo).
3. Reinicia, entra con tu usuario y lleva esta carpeta a la máquina. Lo más cómodo es subirla a un repositorio tuyo de GitHub y clonarla con `git clone`.
4. Dentro de la carpeta: `./install.sh` (o `./install.sh --simular` para ver qué haría sin tocar nada).
5. `sudo reboot` y en la pantalla de inicio elige la sesión Hyprland.

## Qué hay en la carpeta y para qué sirve cada cosa

| Archivo | Para qué |
|---|---|
| `install.sh` | Instala los paquetes, copia la configuración y activa los servicios. Cada bloque explica por qué existe. |
| `config/hypr/hyprland.lua` | Configuración del escritorio: apariencia, teclado y atajos. |
| `config/waybar/config.jsonc` | La barra superior. |
| `config/atajos.txt` | La chuleta que aparece con SUPER + F1. |
| `config/aprender.txt` | La lista del menú de aprendizaje (SUPER + A). Se edita como texto. |
| `perfil` | El comando que crea los contenedores e instala las herramientas. |
| `aprender` | El menú que abre guías locales, TryHackMe, Hack The Box, wikis, etc. |
| `laboratorio` | Prepara máquinas virtuales aisladas para análisis de malware. |
| `otearia/` | La app de noticias, con su propio `LEEME.md` e instalador. |
| `iconos/` | El logo de la distro y el icono de Otearia, en SVG. |
| `config/guias/*.md` | Guías para principiantes: primeros pasos, perfiles, malware y wifi. |
| `perfiles/*.perfil` | Un archivo por perfil, con su lista de herramientas. |

## Por qué está hecho así

**Arch como base.** Hyprland cambia muy rápido y Arch entrega siempre la versión reciente. En Ubuntu habría que compilarlo a mano.

**Configuración en Lua.** Desde Hyprland 0.55 la configuración es un archivo Lua y desde la 0.57 el formato antiguo `hyprland.conf` dejó de funcionar. Muchos tutoriales en internet siguen mostrando el formato viejo; no sirven aquí.

**Contenedores con distrobox.** Kali y BlackArch traen miles de herramientas con dependencias que chocan entre sí y con el sistema. Dentro de un contenedor pueden romperse sin afectar a tu Arch, y se borran con un comando. Distrobox se usa sobre Podman porque Podman funciona sin root.

**Cada perfil con su carpeta personal.** Vive en `~/.local/share/itzli/homes/<perfil>`, para que las herramientas no llenen tu carpeta de usuario de archivos ocultos.

**Paquetes instalados uno por uno.** Los nombres en Kali cambian con el tiempo. Si uno falla, el resto se instala y al final se te dice cuáles faltaron y cómo buscarlos.

## Los perfiles

`perfil listar` muestra los 19 (los 12 roles de Athena y 7 extra). Para crear uno propio, copia cualquier archivo de `~/.config/itzli/perfiles/`, cámbiale el nombre y edita sus cuatro líneas:

```
DESCRIPCION="Qué es"
IMAGEN="docker.io/kalilinux/kali-rolling:latest"
GESTOR="apt"            # apt para Kali, pacman para BlackArch
PAQUETES="nmap curl"
```

## Dos advertencias importantes

**Un contenedor de distrobox no es una caja fuerte.** Comparte tu red, tus dispositivos y puede llegar a tus archivos. Protege al sistema de paquetes rotos, no de programas maliciosos. Para ejecutar una muestra de malware real se usa una máquina virtual aislada y sin red, nunca el perfil `malware-analyst`, que es solo para análisis estático (mirar el archivo sin ejecutarlo).

**Las herramientas ofensivas solo se usan con permiso.** Contra tus propios equipos, laboratorios como TryHackMe o Hack The Box, o programas de bug bounty dentro de su alcance. Fuera de eso es delito en casi cualquier país.

## Qué no se ha probado

Los scripts pasaron revisión de sintaxis y pruebas de lógica con programas simulados. No se han ejecutado en un Arch real ni se ha arrancado Hyprland con esta configuración: esa prueba es la tuya en la máquina virtual. Los nombres de algunos paquetes de Kali pueden haber cambiado; el comando te avisará de cuáles.

## Siguientes pasos previstos

- ISO instalable propia.
- Exportar al menú de aplicaciones las herramientas gráficas de cada perfil (Burp Suite, Wireshark, Ghidra).
- Fondo de pantalla, tema y pantalla de bloqueo propios.
