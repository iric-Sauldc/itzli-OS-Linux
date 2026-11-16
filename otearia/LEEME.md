# Otearia

Radar de noticias de tecnología en español: ciberseguridad, inteligencia artificial e innovación en TI, más una pestaña de vulnerabilidades (CVE) tomadas de la base NVD.

## Uso

| Orden | Qué hace |
|---|---|
| `otearia` | Abre la ventana (también con SUPER + N o clic en la barra) |
| `otearia panel` | Abre el panel fijo |
| `otearia actualizar` | Descarga y traduce ahora |
| `otearia fuentes` | Comprueba qué fuentes responden |
| `otearia listar` / `otearia cves` | Lo mismo que la ventana, en la terminal |
| `otearia programar` | Aplica el intervalo de actualización de tu configuración |

## Configuración

Todo está en `~/.config/otearia/config.toml`, con comentarios en cada opción: intervalo (15, 30 o 60 minutos), forma del widget (`barra`, `panel` o `ambas`), palabras que disparan una alerta y la lista de fuentes.

## Cómo está hecho y por qué

La app está partida en archivos pequeños, cada uno con una sola tarea:

| Archivo | Tarea |
|---|---|
| `fuentes.py` | Descargar RSS y consultar NVD |
| `traducir.py` | Traducir al español |
| `duplicados.py` | Reconocer la misma noticia en varios medios |
| `alertas.py` | Decidir qué merece notificación |
| `actualizar.py` | Encadenar todo lo anterior en una pasada |
| `db.py` | Guardar y leer de la base de datos |
| `resumen.py` | Pedir a una IA los puntos clave (opcional) |
| `ventana.py` | La interfaz gráfica |
| `barra.py` | El texto del módulo de la barra |
| `programar.py` | El temporizador de actualización automática |

**La ventana nunca toca internet.** Solo lee la base de datos local (SQLite). Por eso funciona sin conexión y abre al instante: descargar es trabajo de `otearia actualizar`, que corre aparte.

**Se actualiza con un temporizador de systemd**, no con un programa siempre abierto. Así funciona con la ventana cerrada y no gasta memoria entre actualizaciones.

**Traducción con tope.** El traductor gratuito puede bloquear a quien pide demasiado. Cada pasada traduce como máximo `max_traducciones` textos, empezando por las noticias más nuevas y las CVE más graves. Lo que no alcanza queda en su idioma original, marcado como pendiente, y se traduce en la siguiente pasada. Cada texto se traduce una sola vez.

**Repetidas.** Dos noticias se consideran la misma si sus títulos comparten al menos el 60 % de sus palabras significativas. Queda visible la primera y las demás aparecen como "también en".

**Alertas.** La primera actualización no avisa de nada, porque todo sería nuevo. Después avisa de CVE con puntuación igual o mayor a la que configures y de noticias que mencionen tus palabras, con un máximo de cinco avisos por pasada.

**Resúmenes con IA, opcionales.** Si rellenas `url` y `modelo` en la sección `[resumen_ia]` de la configuración, cada noticia muestra un botón "Resumir" que devuelve de 3 a 5 puntos clave. Funciona con cualquier servicio compatible con el formato de OpenAI, incluidos modelos locales como Ollama (sin clave). Cada noticia se resume una sola vez y el resultado se guarda. Ten en cuenta que el texto de la noticia se envía al servicio que configures, y que tu clave queda escrita en el archivo de configuración: no lo compartas ni lo subas a un repositorio.

## Pendiente

- Buscador y filtro por gravedad en la pestaña de CVE.
