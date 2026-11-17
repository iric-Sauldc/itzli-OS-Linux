-- Cómo se colocan las ventanas propias de Itzli.
return function(apply_window_rule)
  apply_window_rule({
    name = "itzli-otearia-ventana",
    match = { class = "org.otearia.Ventana" },
    float = true,
    center = true,
    size = "900 680",
  })
  -- El panel va pegado al borde derecho.
  apply_window_rule({
    name = "itzli-otearia-panel",
    match = { class = "org.otearia.Panel" },
    float = true,
    size = "420 860",
    move = "72% 7%",
  })
  apply_window_rule({
    name = "itzli-ayuda",
    match = { class = "itzli-ayuda" },
    float = true,
    center = true,
    size = "820 640",
  })
end
