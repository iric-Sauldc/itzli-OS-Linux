PRIMEROS PASOS                              (q para salir, flechas para moverte)

Este escritorio se llama Hyprland y funciona distinto a Windows: las ventanas
no se enciman, se acomodan solas en mosaico. Casi todo se hace con el teclado.
SUPER es la tecla con el logo de Windows.

Lo mínimo para moverte
  SUPER + Enter   abre una terminal
  SUPER + D       busca y abre una aplicación
  SUPER + Q       cierra la ventana
  SUPER + 1..0    cambia de espacio de trabajo (como escritorios virtuales)
  SUPER + H       la lista completa de atajos del escritorio
  SUPER + F1      la ayuda propia de Itzli
  SUPER + W       cambiar el fondo (los colores de todo se ajustan solos)
  CTRL + ALT + P  menú de apagar, reiniciar y cerrar sesión

La terminal, en cinco comandos
  pwd             dónde estoy
  ls              qué hay aquí
  cd carpeta      entrar a una carpeta  (cd .. para subir)
  man comando     el manual de cualquier comando (q para salir)
  sudo comando    ejecutar algo como administrador

Instalar programas en el sistema
  sudo pacman -S nombre      instalar
  sudo pacman -Syu           actualizar TODO (hazlo una vez por semana)
  pacman -Ss palabra         buscar

  En Arch nunca instales sin actualizar antes (nada de "pacman -Sy nombre"):
  mezclar paquetes nuevos con viejos es la forma más común de romperlo.

Las herramientas de seguridad NO se instalan con pacman
  Van en perfiles, dentro de contenedores, para no ensuciar el sistema.
  Lee la guía "cómo funcionan los perfiles" (SUPER + A).

Por dónde empezar a aprender
  1. perfil instalar enthusiast-student
  2. SUPER + A y abre TryHackMe. Empieza por las salas de Linux y de redes.
  3. OverTheWire (nivel Bandit) para soltarte con la terminal.
  Primero entiende cómo funcionan las redes y Linux. Las herramientas son lo
  de menos: sin la base, solo estarás copiando comandos.

Si algo se rompe
  Si la barra o los menús se ven raros: SUPER + ALT + R los recarga.
  Si la pantalla queda rara: CTRL + ALT + Supr cierra la sesión.
  Si Hyprland no arranca: en la pantalla de inicio pulsa CTRL + ALT + F3
  y entra con tu usuario. Tus ajustes están en ~/.config/hypr/UserConfigs
  y los de Itzli en ~/.config/itzli/hypr
