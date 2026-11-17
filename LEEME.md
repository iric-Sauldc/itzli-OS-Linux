# Itzli

Arch Linux con Hyprland para aprender ciberseguridad. "Itzli" es obsidiana en náhuatl.

Las herramientas de seguridad no se instalan en el sistema: van en contenedores, agrupadas por rol (estudiante, bug bounty, analista de malware...).

Esta versión todavía no es una ISO. Es un instalador que se ejecuta sobre un Arch recién instalado.

## Cómo está armada

Itzli tiene dos capas.

**El escritorio base** es el proyecto de KooL, mantenido hoy por LinuxBeginnings. Instala Hyprland ya configurado: barra, menús, notificaciones, bloqueo, temas y pantalla de inicio. Se descarga al instalar, así que siempre llega su versión más reciente. Esto importa porque Hyprland cambia seguido y ese proyecto se encarga de seguirle el paso.

**La capa de Itzli** va encima: los roles, Otearia, el laboratorio de malware, las guías, el logo, el fondo y los colores.

Las dos capas no se mezclan. El escritorio reserva la carpeta `~/.config/hypr/UserConfigs` para ajustes del usuario y no la pisa al actualizarse. Itzli añade ahí un bloque pequeño que carga sus propios archivos desde `~/.config/itzli/hypr`. Si un archivo de Itzli fallara, el escritorio arranca igual.

## Instalar (pruébalo primero en una máquina virtual)

1. Crea la máquina virtual: 4 GB de RAM, 40 GB de disco, aceleración 3D activada.
2. Instala Arch con `archinstall`: tipo **Minimal**, red **NetworkManager**, un usuario con sudo y el paquete adicional `git`.
3. Lleva esta carpeta a la máquina (por ejemplo, con `git clone` desde un repositorio tuyo).
4. Dentro de la carpeta:

```
./install.sh --simular    # solo muestra lo que hará
./install.sh
sudo reboot
```

El instalador del escritorio base es interactivo y está en inglés. Antes de abrirlo, Itzli te muestra qué contestar. Lo más importante: cuando al final pregunte si quieres reiniciar, contesta **n**, porque falta la parte de Itzli.

Si algo se corta a la mitad, vuelve a ejecutar `./install.sh`. Detecta lo que ya está hecho y no lo repite.

## Qué hay en la carpeta

| Archivo | Para qué |
|---|---|
| `install.sh` | Instala las dos capas. Cada paso explica por qué existe. |
| `base/preset.conf` | Qué opciones del escritorio base quedan marcadas (la instalación "recortada"). |
| `hypr/*.lua` | Atajos, arranque y reglas de ventanas que Itzli añade al escritorio. |
| `sddm/theme.conf.user` | Fondo, colores y textos en español para la pantalla de inicio. |
| `fondos/` | El fondo de escritorio y el de la pantalla de inicio. |
| `iconos/` | El logo de Itzli (completo, pequeño y de un color) y el icono de Otearia. |
| `perfil`, `perfiles/` | El comando que crea los contenedores, y un archivo por rol. |
| `aprender`, `config/aprender.txt` | El menú de aprendizaje y su lista editable. |
| `laboratorio` | Prepara máquinas virtuales aisladas para análisis de malware. |
| `itzli-menu` | El menú común que usan los comandos anteriores. |
| `otearia/` | La app de noticias, con su propio `LEEME.md`. |
| `config/guias/` | Guías para principiantes. |
| `CREDITOS.md` | De dónde viene el escritorio base y qué implican sus licencias. |

## Decisiones y sus porqués

**Los colores salen del fondo.** El escritorio base genera la paleta de toda la interfaz a partir del fondo de pantalla. Itzli deja su fondo azul como fondo inicial y con eso todo sale en azules, sin tocar ningún tema. Si cambias de fondo con SUPER + W, los colores cambian con él.

**El contador de Otearia vive en un diseño de barra propio.** El instalador copia el diseño de barra en uso, le añade el módulo y activa la copia (termina en `-Itzli`). El diseño original queda intacto. Si eliges otro diseño con SUPER + ALT + B, el contador desaparece de la barra, pero las alertas y SUPER + N siguen funcionando.

**La pantalla de inicio usa `theme.conf.user`.** SDDM lee ese archivo después del `theme.conf` del tema, así que los valores de Itzli ganan sin modificar el tema original.

**Contenedores con distrobox sobre Podman.** Kali y BlackArch traen miles de herramientas que chocan entre sí. En un contenedor pueden romperse sin afectar al sistema, y Podman funciona sin root.

**Atajos en combinaciones libres.** Itzli no cambia ningún atajo del escritorio. Usa SUPER + N, SUPER + F1, SUPER + ALT + A y SUPER + ALT + I, que estaban sin usar.

## Dos advertencias importantes

**Un contenedor de distrobox no es una caja fuerte.** Comparte tu red y puede llegar a tus archivos. Protege al sistema de paquetes rotos, no de programas maliciosos. Para ejecutar una muestra de malware real usa el laboratorio (`laboratorio preparar`), nunca el rol `malware-analyst`, que es solo para análisis estático.

**Las herramientas ofensivas solo se usan con permiso.** Contra tus propios equipos, laboratorios como TryHackMe o Hack The Box, o programas de bug bounty dentro de su alcance.

## Qué se ha probado y qué no

Probado contra una copia real de la configuración del escritorio base: los archivos del escritorio cargan los atajos, reglas y arranque de Itzli; el diseño de barra generado es válido; el instalador se puede repetir sin duplicar nada.

Sin probar: la instalación completa en un Arch real con las dos capas, el aspecto final de la pantalla de inicio y de la barra, y que los colores salgan en azul. Esa prueba es en tu máquina virtual.

## Siguientes pasos previstos

- Exportar al menú de aplicaciones las herramientas gráficas de cada rol (Burp Suite, Wireshark, Ghidra).
- Pantalla de bienvenida para elegir rol con un clic.
- ISO instalable.
