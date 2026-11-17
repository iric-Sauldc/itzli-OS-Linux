-- Programas que Itzli lanza al iniciar la sesión.
return function(exec_once)
  -- Abre el panel de noticias solo si en la configuración de Otearia
  -- elegiste forma = "panel" o "ambas".
  exec_once("otearia inicio")
end
