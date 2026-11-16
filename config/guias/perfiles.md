CÓMO FUNCIONAN LOS PERFILES                 (q para salir, flechas para moverte)

La idea
  Un perfil es un contenedor: una mini distro (Kali o BlackArch) que corre
  dentro de la tuya. Las herramientas se instalan ahí dentro. Si se rompen o
  ya no las quieres, borras el perfil y tu sistema queda intacto.

  La pieza que lo hace posible se llama distrobox. Tú solo usas el comando
  "perfil", que la maneja por ti.

Uso diario
  perfil listar                 qué perfiles hay y cuáles tienes instalados
  perfil ver web-pentester      qué herramientas trae uno
  perfil instalar web-pentester lo crea (la primera vez tarda: descarga Kali)
  perfil entrar web-pentester   abre una terminal dentro
  perfil actualizar web-pentester
  perfil borrar web-pentester
  SUPER + P                     menú para entrar a uno instalado

Cómo sé que estoy dentro
  El texto antes del cursor cambia y muestra el nombre del contenedor, algo
  como  usuario@perfil-web-pentester. Para salir escribe: exit

Qué se comparte y qué no
  Dentro del perfil tienes otra carpeta personal, separada de la tuya. Así las
  herramientas no llenan tu sistema de archivos de configuración.
  Tu carpeta real sigue accesible desde dentro, en su ruta de siempre
  (/home/tu-usuario). La red es la misma que la de tu equipo.

  Importante: un contenedor NO es una barrera de seguridad. Te protege de
  paquetes rotos, no de programas maliciosos. Para eso está el laboratorio.

Instalar algo más dentro de un perfil
  Entra y usa el gestor de esa distro:
    Kali:       sudo apt install nombre      (buscar: apt-cache search palabra)
    BlackArch:  sudo pacman -S nombre        (buscar: pacman -Ss palabra)

Crear tu propio perfil
  Los perfiles son archivos de texto en ~/.config/itzli/perfiles/
  Copia uno, cámbiale el nombre (solo minúsculas, números y guiones) y edita:

    DESCRIPCION="Mi perfil"
    IMAGEN="docker.io/kalilinux/kali-rolling:latest"
    GESTOR="apt"
    PAQUETES="nmap curl"

  Para BlackArch: IMAGEN="docker.io/blackarchlinux/blackarch:latest" y
  GESTOR="pacman".

Si un paquete no se instaló
  Al terminar, "perfil instalar" lista los que fallaron. Casi siempre es que
  cambió de nombre: búscalo desde dentro y corrige el archivo del perfil.
