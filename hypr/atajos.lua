-- Atajos que Itzli añade al escritorio base.
--
-- Este archivo no toca los atajos del escritorio: solo usa combinaciones que
-- estaban libres. Recibe las funciones "bind" y "exec_cmd" del propio
-- escritorio, así que si este cambia por dentro, aquí no hay que tocar nada.
return function(bind, exec_cmd)
  bind("SUPER", "N", exec_cmd("otearia"),
    { description = "Itzli: noticias y vulnerabilidades (Otearia)" })
  bind("SUPER", "F1", exec_cmd("kitty --class itzli-ayuda less $HOME/.config/itzli/atajos.txt"),
    { description = "Itzli: ayuda y atajos propios" })
  bind("SUPER ALT", "A", exec_cmd("aprender"),
    { description = "Itzli: menú de aprendizaje y guías" })
  bind("SUPER ALT", "I", exec_cmd("perfil menu"),
    { description = "Itzli: entrar a un perfil de herramientas" })
end
