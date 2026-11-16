AUDITORÍA WIFI                              (q para salir, flechas para moverte)

Antes de nada
  Audita solo tu propia red o una para la que tengas permiso por escrito.
  Capturar o interferir tráfico de redes ajenas es delito.

Por qué este perfil es distinto
  Normalmente una tarjeta wifi solo escucha lo que va dirigido a ella. Para
  auditar hace falta el "modo monitor", en el que escucha todo lo que hay en
  el aire. Cambiar ese modo exige ser root de verdad, así que el perfil wifi
  usa un contenedor con root real (los demás no). Consecuencias:
    - pide tu contraseña al instalarlo y al entrar;
    - tiene menos aislamiento: lo que hagas dentro afecta a la red del equipo.

El hardware importa más que el software
  Muchas tarjetas internas de portátil no soportan modo monitor. Lo habitual
  es usar un adaptador wifi USB cuyo chip sí lo soporte. Antes de comprar
  uno, busca el modelo exacto junto a "monitor mode linux".

  Para ver si tu tarjeta lo soporta, en una terminal normal:
      iw list
  Busca el bloque "Supported interface modes". Si aparece "monitor", sirve.

En una máquina virtual
  La máquina virtual no ve la tarjeta interna como wifi. Necesitas un
  adaptador USB y "pasarlo" a la máquina desde el menú de dispositivos USB.

Primeros pasos
  perfil instalar wifi
  perfil entrar wifi
  iw dev                    muestra tus interfaces wifi (suele ser wlan0)

  Al poner la tarjeta en modo monitor pierdes la conexión wifi normal hasta
  que la devuelvas a su modo habitual o reinicies NetworkManager:
      sudo systemctl restart NetworkManager

Qué practicar y dónde
  Usa tu propio router. Un buen primer ejercicio es defensivo: mira qué
  seguridad anuncia tu red (WPA2 o WPA3), si tiene WPS activado y qué
  dispositivos hay conectados, y corrige lo que encuentres débil.
  Para la teoría, las salas de redes inalámbricas de TryHackMe y la
  documentación de aircrack-ng explican cada herramienta paso a paso.

Si no detecta la tarjeta dentro del perfil
  Comprueba primero fuera del perfil con "iw dev". Si ahí tampoco aparece, es
  un problema de controlador (driver) del adaptador, no del perfil.
