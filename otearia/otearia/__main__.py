"""Punto de entrada: reparte cada orden a su módulo."""
import argparse
import subprocess
import sys

from . import config, db

AYUDA = """órdenes:
  ventana      abre la ventana de noticias
  panel        abre el panel fijo
  actualizar   descarga y traduce ahora
  listar       muestra las últimas noticias en la terminal
  cves         muestra las últimas vulnerabilidades en la terminal
  fuentes      comprueba qué fuentes responden
  programar    activa la actualización automática según tu configuración
  barra        (lo usa waybar) texto del módulo de la barra
  inicio       (lo usa Hyprland al arrancar) abre el panel si lo configuraste
"""


def main():
    analizador = argparse.ArgumentParser(prog="otearia", epilog=AYUDA,
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
    analizador.add_argument("orden", nargs="?", default="ventana")
    orden = analizador.parse_args().orden
    cfg = config.cargar()

    if orden in ("ventana", "panel"):
        # Se importa aquí y no arriba: así "actualizar" y "barra" funcionan
        # aunque no haya entorno gráfico (por ejemplo, desde systemd).
        from . import ventana
        sys.exit(ventana.abrir(cfg, panel=(orden == "panel")))

    elif orden == "actualizar":
        from .actualizar import actualizar
        r = actualizar(cfg)
        print(f"{r['noticias']} noticias nuevas, {r['cves']} CVE nuevas, "
              f"{r['traducidas']} traducciones, {r['repetidas']} repetidas agrupadas.")
        for error in r["errores"]:
            print("  no respondió →", error)

    elif orden == "listar":
        con = db.conectar()
        for n in db.noticias(con, limite=30):
            otros = ", ".join(o["fuente"] for o in db.otros_medios(con, n["id"]))
            print(f"{n['fecha'][:16].replace('T', ' ')}  [{n['fuente']}] {n['titulo'] or n['titulo_original']}"
                  + (f"  (también: {otros})" if otros else ""))

    elif orden == "cves":
        con = db.conectar()
        for c in db.cves(con, limite=30):
            puntuacion = c["puntuacion"] if c["puntuacion"] is not None else "-"
            print(f"{c['id']:18} {c['gravedad']:12} {puntuacion!s:5} {(c['descripcion'] or c['descripcion_original'])[:90]}")

    elif orden == "fuentes":
        from . import fuentes
        for fuente in cfg["fuentes"]:
            try:
                print(f"  bien   {fuente['nombre']}: {len(fuentes.leer_fuente(fuente))} noticias")
            except Exception as error:
                print(f"  FALLA  {fuente['nombre']}: {error}")

    elif orden == "programar":
        from .programar import programar
        programar(cfg["general"]["intervalo_minutos"])

    elif orden == "barra":
        from .barra import salida
        print(salida())

    elif orden == "inicio":
        if cfg["general"]["forma"] in ("panel", "ambas"):
            subprocess.Popen([sys.argv[0] if sys.argv[0].endswith("otearia") else "otearia", "panel"])

    else:
        analizador.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
