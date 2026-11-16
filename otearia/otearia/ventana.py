"""La ventana de Otearia (GTK 4).

Sirve para las dos formas del widget: como ventana normal que se abre desde
la barra, o como panel angosto. Lo único que cambia es el tamaño y el
identificador, que es lo que Hyprland usa para colocarla en su sitio.
"""
import threading

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gio, GLib, Gtk  # noqa: E402

from . import config, db, resumen as ia  # noqa: E402

ESTILO = """
.titulo { font-weight: bold; font-size: 1.05em; }
.meta { opacity: 0.65; font-size: 0.9em; }
.fila { padding: 10px 12px; }
.puntos { padding: 6px 10px; border-left: 3px solid alpha(currentColor, 0.4); }
.CRITICAL { color: #ff5555; font-weight: bold; }
.HIGH { color: #ffb86c; font-weight: bold; }
.MEDIUM { color: #f1fa8c; }
"""

GRAVEDAD = {"CRITICAL": "CRÍTICA", "HIGH": "ALTA", "MEDIUM": "MEDIA", "LOW": "BAJA"}


def hace_cuanto(fecha_iso):
    """Convierte una fecha en 'hace 3 h', más fácil de leer que una hora exacta."""
    from datetime import datetime, timezone
    try:
        fecha = datetime.strptime(fecha_iso[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return ""
    minutos = int((db.ahora() - fecha).total_seconds() // 60)
    if minutos < 60:
        return f"hace {max(minutos, 1)} min"
    if minutos < 60 * 24:
        return f"hace {minutos // 60} h"
    return f"hace {minutos // (60 * 24)} d"


def etiqueta(texto, clase=None):
    e = Gtk.Label(label=texto, xalign=0, wrap=True)
    e.set_selectable(False)
    if clase:
        e.add_css_class(clase)
    return e


def abrir_enlace(enlace):
    Gio.AppInfo.launch_default_for_uri(enlace, None)


class Ventana(Gtk.ApplicationWindow):
    def __init__(self, app, cfg, panel):
        super().__init__(application=app, title="Otearia")
        self.cfg = cfg
        self.con = db.conectar()
        self.set_default_size(420 if panel else 900, 860 if panel else 680)

        cabecera = Gtk.HeaderBar()
        self.boton_actualizar = Gtk.Button(label="Actualizar")
        self.boton_actualizar.connect("clicked", self.al_actualizar)
        cabecera.pack_start(self.boton_actualizar)
        self.estado = Gtk.Label()
        self.estado.add_css_class("meta")
        cabecera.pack_end(self.estado)
        self.set_titlebar(cabecera)

        # Una pestaña por tema, más CVE y favoritos. Cada una es una lista
        # con desplazamiento.
        self.pestanas = Gtk.Notebook()
        self.listas = {}
        for clave, nombre in [*config.TEMAS.items(), ("cve", "Vulnerabilidades"), ("favoritas", "Favoritos")]:
            lista = Gtk.ListBox()
            lista.set_selection_mode(Gtk.SelectionMode.NONE)
            lista.set_show_separators(True)
            desplazable = Gtk.ScrolledWindow(vexpand=True)
            desplazable.set_child(lista)
            self.pestanas.append_page(desplazable, Gtk.Label(label=nombre))
            self.listas[clave] = lista
        self.set_child(self.pestanas)

        self.connect("close-request", self.al_cerrar)
        self.recargar()

    # --- Contenido ----------------------------------------------------------

    def recargar(self):
        for clave, lista in self.listas.items():
            while (hija := lista.get_first_child()) is not None:
                lista.remove(hija)
            if clave == "cve":
                filas = [self.fila_cve(c) for c in db.cves(self.con)]
            elif clave == "favoritas":
                filas = [self.fila_noticia(n) for n in db.noticias(self.con, solo_favoritas=True)]
            else:
                filas = [self.fila_noticia(n) for n in db.noticias(self.con, tema=clave)]
            for fila in filas:
                lista.append(fila)
            if not filas:
                lista.append(etiqueta("Nada por aquí todavía. Pulsa «Actualizar».", "fila"))

        ultima = db.leer_estado(self.con, "ultima_actualizacion")
        errores = db.leer_estado(self.con, "errores")
        texto = f"Actualizado {hace_cuanto(ultima)}" if ultima else "Sin actualizar"
        if errores:
            texto += f" · {errores.count('|') + 1} fuente(s) sin responder"
            self.estado.set_tooltip_text(errores.replace(" | ", "\n"))
        self.estado.set_label(texto)

    def fila_noticia(self, n):
        caja = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        caja.add_css_class("fila")

        traducida = bool(n["titulo"]) and n["idioma"] != "es"
        titulo = etiqueta(n["titulo"] or n["titulo_original"], "titulo")
        resumen = etiqueta(n["resumen"] or n["resumen_original"])

        meta = f"{n['fuente']} · {hace_cuanto(n['fecha'])}"
        otros = db.otros_medios(self.con, n["id"])
        if otros:
            meta += " · también en: " + ", ".join(sorted({o["fuente"] for o in otros}))
        if n["idioma"] != "es" and not n["titulo"]:
            meta += " · pendiente de traducir"

        botones = Gtk.Box(spacing=6)
        abrir = Gtk.Button(label="Abrir")
        abrir.connect("clicked", lambda _b: abrir_enlace(n["enlace"]))
        botones.append(abrir)

        favorita = Gtk.ToggleButton(label="★ Favorito", active=bool(n["favorita"]))
        favorita.connect("toggled", self.al_marcar_favorita, n["id"])
        botones.append(favorita)

        if traducida:
            # Permite comparar con el texto original cuando la traducción
            # automática deja algo raro, que con términos técnicos pasa.
            original = Gtk.ToggleButton(label="Ver original")

            def alternar(boton):
                ver_original = boton.get_active()
                titulo.set_label(n["titulo_original"] if ver_original else n["titulo"])
                resumen.set_label(n["resumen_original"] if ver_original else (n["resumen"] or n["resumen_original"]))
            original.connect("toggled", alternar)
            botones.append(original)

        # Los puntos clave de la IA. Se guardan en la base: pedirlos cuesta
        # tiempo (y quizá dinero), así que cada noticia se resume una sola vez.
        puntos = etiqueta(n["resumen_ia"] or "", "puntos")
        puntos.set_visible(bool(n["resumen_ia"]))
        if ia.activo(self.cfg) and not n["resumen_ia"]:
            resumir = Gtk.Button(label="Resumir")
            resumir.connect("clicked", self.al_resumir, n, puntos)
            botones.append(resumir)

        for pieza in (titulo, etiqueta(meta, "meta"), resumen, puntos, botones):
            caja.append(pieza)
        return caja

    def fila_cve(self, c):
        caja = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        caja.add_css_class("fila")

        puntuacion = f" {c['puntuacion']}" if c["puntuacion"] is not None else ""
        gravedad = etiqueta(f"{c['id']}  ·  {GRAVEDAD.get(c['gravedad'], 'SIN EVALUAR')}{puntuacion}", "titulo")
        gravedad.add_css_class(c["gravedad"].replace(" ", "-"))

        abrir = Gtk.Button(label="Ver en NVD", halign=Gtk.Align.START)
        abrir.connect("clicked", lambda _b: abrir_enlace(c["enlace"]))

        for pieza in (gravedad, etiqueta(hace_cuanto(c["fecha"]), "meta"),
                      etiqueta(c["descripcion"] or c["descripcion_original"]), abrir):
            caja.append(pieza)
        return caja

    # --- Acciones -----------------------------------------------------------

    def al_marcar_favorita(self, boton, noticia_id):
        self.con.execute("UPDATE noticias SET favorita = ? WHERE id = ?", (int(boton.get_active()), noticia_id))
        self.con.commit()

    def al_resumir(self, boton, n, puntos):
        boton.set_sensitive(False)
        boton.set_label("Resumiendo…")

        def trabajo():
            try:
                texto, fallo = ia.resumir(self.cfg, n["titulo_original"], n["enlace"], n["resumen_original"]), False
            except Exception as error:
                texto, fallo = f"No se pudo resumir: {error}", True
            GLib.idle_add(mostrar, texto, fallo)

        def mostrar(texto, fallo):
            puntos.set_label(texto)
            puntos.set_visible(True)
            if fallo:
                boton.set_label("Reintentar")
                boton.set_sensitive(True)
            else:
                boton.set_visible(False)
                self.con.execute("UPDATE noticias SET resumen_ia = ? WHERE id = ?", (texto, n["id"]))
                self.con.commit()
            return False

        threading.Thread(target=trabajo, daemon=True).start()

    def al_actualizar(self, _boton):
        self.boton_actualizar.set_sensitive(False)
        self.estado.set_label("Actualizando…")

        # La descarga tarda segundos. En un hilo aparte la ventana no se
        # congela; al terminar, GLib.idle_add devuelve el control al hilo de
        # la interfaz, que es el único que puede tocar los widgets.
        def trabajo():
            from .actualizar import actualizar
            try:
                actualizar(self.cfg)
            finally:
                GLib.idle_add(self.al_terminar)

        threading.Thread(target=trabajo, daemon=True).start()

    def al_terminar(self):
        self.boton_actualizar.set_sensitive(True)
        self.recargar()
        return False  # False = ejecutar una sola vez

    def al_cerrar(self, _ventana):
        # Cerrar la ventana cuenta como "ya lo vi": el contador de la barra
        # vuelve a cero.
        import subprocess
        self.con.execute("UPDATE noticias SET leida = 1 WHERE leida = 0")
        self.con.execute("UPDATE cves SET leida = 1 WHERE leida = 0")
        self.con.commit()
        self.con.close()
        subprocess.run(["pkill", "-RTMIN+8", "waybar"], check=False, capture_output=True)
        return False


def abrir(cfg, panel=False):
    # El identificador es lo que Hyprland ve como "class" de la ventana.
    # Uno distinto por forma permite una regla distinta para cada una.
    app = Gtk.Application(application_id="org.otearia.Panel" if panel else "org.otearia.Ventana")

    def al_activar(aplicacion):
        # Si ya había una ventana abierta, se trae al frente en vez de
        # abrir una segunda.
        existente = aplicacion.get_active_window()
        if existente:
            existente.present()
            return
        proveedor = Gtk.CssProvider()
        try:
            proveedor.load_from_string(ESTILO)
        except AttributeError:  # versiones de GTK anteriores a la 4.12
            proveedor.load_from_data(ESTILO.encode())
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), proveedor, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        Gtk.Window.set_default_icon_name("org.otearia.Ventana")
        Ventana(aplicacion, cfg, panel).present()

    app.connect("activate", al_activar)
    return app.run(None)
