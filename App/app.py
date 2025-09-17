# pylint: disable=no-member
from kivymd.app import MDApp
from kivy.core.window import Window
from utils import formato_pesos, parsear_monto
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.label import MDLabel
from datetime import datetime
from kivy.metrics import dp
from kivy.uix.popup import Popup   # 🔹 Import Popup
from utils import formato_pesos
import DB
from datetime import datetime as dt # 🔹 añadido para ascensos / fechas

# Crear todas las tablas y el admin por defecto
try:
    DB.crear_tablas()  # Esto ya hace todo: usuarios, metas, ahorros, salidas, aportes, ascensos y admin
    print("✅ Todas las tablas creadas correctamente.")
except Exception as e:
    print("⚠️ Error al crear las tablas:", e)



# -----------------------------
# Utilidades
# -----------------------------
def formato_pesos(valor):
    try:
        return "${:,.0f}".format(float(valor)).replace(",", ".")
    except:
        return str(valor)

def parsear_monto(texto):
    """Convierte entradas como '$3.500.000' o '3.500.000' a float 3500000.0"""
    limpio = texto.replace("$", "").replace(".", "").replace(",", "").strip()
    if not limpio:
        return 0.0
    return float(limpio)

def mostrar_popup(titulo, mensaje):
    popup = Popup(title=titulo,
                  content=Label(text=mensaje),
                  size_hint=(0.7, 0.4))
    popup.open()

def registrar_aporte(self, monto, fecha, hora=None):
    if hora is None:
        hora = datetime.now().strftime("%H:%M:%S")

# -----------------------------
# Pantalla de Inicio
# -----------------------------
class HomeScreen(Screen):
    def go_to_login(self, instance):
        login_screen = self.manager.get_screen("login")
        login_screen.desde_registro = False
        login_screen.limpiar_campos()
        self.manager.current = "login"

    def go_to_register(self, instance):
        self.manager.current = "register"


# -----------------------------
# Pantalla de Inicio de Sesión
# -----------------------------
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.desde_registro = False

    def limpiar_campos(self):
        self.ids.email.text = ""
        self.ids.password.text = ""

    def login(self, instance):
        correo = self.ids.email.text.strip()
        contrasena = self.ids.password.text

        # Admin fijo
        if correo == "juan.david.pereira.leon@gmail.com" and contrasena == "7719":
            mostrar_popup("Bienvenido", "✅ Sesión iniciada como administrador")
            self.manager.current = "admin_panel"
            return

        # Validación con BD
        user = DB.validar_login(correo, contrasena)
        if user:
            mostrar_popup("Bienvenido", f"✅ Hola {correo}")
            self.manager.get_screen("usuario_metas").set_usuario(correo)
            self.manager.current = "usuario_metas"
        else:
            mostrar_popup("Error", "❌ Correo o contraseña incorrectos")

    def go_to_home(self, instance):
        self.manager.current = "home"


# -----------------------------
# Pantalla de Registro
# -----------------------------
class RegisterScreen(Screen):
    def on_enter(self):
        # Menú de cursos
        cursos = ["Noveno", "Décimo", "Once"]
        menu_items_curso = [
            {"text": c, "viewclass": "OneLineListItem", "on_release": lambda x=c: self.set_curso(x)}
            for c in cursos
        ]
        self.menu_curso = MDDropdownMenu(
            caller=self.ids.curso,
            items=menu_items_curso,
            width_mult=4
        )

        # Menú de promociones
        promociones = ["2025-2026", "2026-2027", "2027-2028"]
        menu_items_prom = [
            {"text": p, "viewclass": "OneLineListItem", "on_release": lambda x=p: self.set_promocion(x)}
            for p in promociones
        ]
        self.menu_promocion = MDDropdownMenu(
            caller=self.ids.promocion,
            items=menu_items_prom,
            width_mult=4
        )

    def set_curso(self, value):
        self.ids.curso.text = value
        self.menu_curso.dismiss()

    def set_promocion(self, value):
        self.ids.promocion.text = value
        self.menu_promocion.dismiss()

    def register(self, instance):
        padre = self.ids.padre.text.strip()
        estudiante = self.ids.estudiante.text.strip()
        curso = self.ids.curso.text.strip()
        promocion = self.ids.promocion.text.strip()
        correo = self.ids.email.text.strip()
        contrasena = self.ids.password.text

        if curso == "Seleccionar curso" or promocion == "Seleccionar promoción":
            mostrar_popup("Aviso", "⚠️ Selecciona curso y promoción")
            return

        if DB.registrar_usuario(padre, estudiante, curso, promocion, correo, contrasena):
            mostrar_popup("Éxito", "✅ Usuario registrado con éxito")
            self.manager.current = "login"
        else:
            mostrar_popup("Error", "❌ No se pudo registrar el usuario. Verifica el correo.")

    def go_to_home(self, instance):
        self.manager.current = "home"


# -----------------------------
# Pantalla Panel de Administrador
# -----------------------------
class AdminPanelScreen(Screen):
    def go_to_metas(self, instance):
        metas_screen = self.manager.get_screen("metas")
        metas_screen.actualizar_lista()
        self.manager.current = "metas"

    def go_to_aportes(self, instance):
        try:
            self.manager.current = "aportes"
        except Exception as e:
            print("⚠️ Pantalla 'aportes' no encontrada:", e)

    def go_to_ascenso(self, instance):
        try:
            scr = self.manager.get_screen("ascenso")
            scr.cargar_lista()
            self.manager.current = "ascenso"
        except Exception as e:
            print("⚠️ Pantalla 'ascenso' no encontrada:", e)

    def logout(self, instance):  # <- CAMBIO para que coincida con .kv
        self.manager.current = "home"


# -----------------------------
# Pantalla de Metas (Admin)
# -----------------------------
# -----------------------------
# Pantalla Metas (Vista Admin)
# -----------------------------
class MetasScreen(Screen):
    def on_pre_enter(self, *args):
        self.actualizar_lista()
        return super().on_pre_enter(*args)

    def actualizar_lista(self):
        if not hasattr(self.ids, 'lista_layout'):
            return
        self.ids.lista_layout.clear_widgets()
        metas = DB.obtener_metas()
        if not metas:
            self.ids.lista_layout.add_widget(
                MDLabel(
                    text="No hay metas registradas",
                    size_hint_y=None,
                    height=40
                )
            )
            return
        for meta in metas:
            try:
                llave, curso, nombre, fecha, costo = meta
                fila = MetaItem(
                    meta_id=str(llave),
                    curso=curso,
                    nombre=nombre,
                    fecha=fecha,
                    costo=formato_pesos(costo)
                )
                self.ids.lista_layout.add_widget(fila)
            except Exception as e:
                print("Error creando MetaItem:", e)

    def editar_meta(self, meta):
        agregar_meta_screen = self.manager.get_screen("agregar_meta")
        agregar_meta_screen.cargar_meta(meta)
        self.manager.current = "agregar_meta"

    def eliminar_meta(self, meta_id):
        DB.eliminar_meta(meta_id)
        self.actualizar_lista()

    def agregar_meta(self, instance):
        agregar_meta_screen = self.manager.get_screen("agregar_meta")
        agregar_meta_screen.limpiar_campos()
        self.manager.current = "agregar_meta"

    def go_back(self, instance):
        self.manager.current = "admin_panel"


# -----------------------------
# Widget individual de Meta
# -----------------------------
class MetaItem(MDBoxLayout):
    meta_id = StringProperty()
    curso = StringProperty()
    nombre = StringProperty()
    fecha = StringProperty()
    costo = StringProperty()

    def editar(self):
        app = App.get_running_app()
        metas_screen = app.root.get_screen("metas")
        meta = (
            self.meta_id,
            self.curso,
            self.nombre,
            self.fecha,
            self.costo.replace("$", "").replace(".", "")
        )
        metas_screen.editar_meta(meta)

    def eliminar(self):
        app = App.get_running_app()
        metas_screen = app.root.get_screen("metas")
        metas_screen.eliminar_meta(self.meta_id)


# -----------------------------
# Pantalla Agregar/Editar Meta
# -----------------------------
class AgregarMetaScreen(Screen):
    meta_id = StringProperty(None)
    menu_curso = None

    def on_kv_post(self, base_widget):
        cursos = ["Noveno", "Décimo", "Once"]
        menu_items = [
            {"text": c, "viewclass": "OneLineListItem", "on_release": lambda x=c: self.set_curso(x)}
            for c in cursos
        ]
        if not self.menu_curso:
            self.menu_curso = MDDropdownMenu(
                caller=self.ids.curso_btn,
                items=menu_items,
                width_mult=4
            )

    def set_curso(self, curso):
        self.ids.curso_btn.text = curso
        if self.menu_curso:
            self.menu_curso.dismiss()

    def limpiar_campos(self):
        self.meta_id = None
        self.ids.curso_btn.text = "Seleccionar curso"
        self.ids.nombre.text = ""
        self.ids.fecha.text = ""
        self.ids.costo.text = ""

    def cargar_meta(self, meta):
        self.meta_id = str(meta[0])
        self.ids.curso_btn.text = meta[1]
        self.ids.nombre.text = meta[2]
        self.ids.fecha.text = meta[3]
        self.ids.costo.text = str(meta[4])

    def guardar_meta(self, instance):
        curso = self.ids.curso_btn.text
        nombre = self.ids.nombre.text.strip()
        fecha = self.ids.fecha.text.strip()
        costo = self.ids.costo.text.strip()

        if curso == "Seleccionar curso" or not nombre or not fecha or not costo:
            print("⚠️ Completa todos los campos")
            return

        try:
            costo_num = parsear_monto(costo)
        except:
            print("⚠️ Monto inválido")
            return

        if self.meta_id:
            DB.actualizar_meta(self.meta_id, curso, nombre, fecha, costo_num)
            print("✅ Meta actualizada")
        else:
            DB.agregar_meta(curso, nombre, fecha, costo_num)
            print("✅ Meta agregada")

        self.manager.get_screen("metas").actualizar_lista()
        self.manager.current = "metas"

    def go_back(self, instance):
        self.manager.current = "metas"

# -----------------------------
# Pantalla Usuario Metas
# -----------------------------
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDRaisedButton
from kivy.metrics import dp

class UsuarioMetasScreen(Screen):
    usuario_correo = None
    usuario = None

    def set_usuario(self, correo):
        self.usuario_correo = correo
        self.usuario = DB.obtener_usuario_por_correo(self.usuario_correo)
        Clock.schedule_once(lambda dt: self.actualizar_vista(), 0)

    def actualizar_vista(self):
        if not self.usuario:
            return

        curso = self.usuario[3]
        user_id = self.usuario[0]

        metas = DB.obtener_metas_por_curso(curso, user_id)
        self.ids.metas_layout.clear_widgets()

        total_costo = sum(float(meta[4]) for meta in metas) if metas else 0.0
        total_ahorrado = 0.0

        for meta in metas:
            meta_id, meta_curso, nombre, fecha, costo = meta
            ahorrado_meta = DB.obtener_total_ahorrado(meta_id, user_id)
            total_ahorrado += ahorrado_meta

            btn = MDRaisedButton(
                text=f"{nombre} | {fecha} | {formato_pesos(costo)}",
                md_bg_color=(0.1, 0.2, 0.5, 1),
                text_color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(45)
            )
            btn.bind(on_release=lambda inst, m=meta: self.ir_a_meta(m))
            self.ids.metas_layout.add_widget(btn)

        faltante = max(total_costo - total_ahorrado, 0.0)
        progreso = (total_ahorrado / total_costo * 100) if total_costo > 0 else 0
        progreso = min(progreso, 100)

        self.ids.titulo_metas.text = f"Gastos {curso}"
        self.ids.progreso_label.text = (
            f"Progreso: {progreso:.2f}% | "
            f"Ahorrado: {formato_pesos(total_ahorrado)} | "
            f"Faltante: {formato_pesos(faltante)}"
        )
        self.ids.progress_bar.value = progreso

    def ir_a_meta(self, meta):
        detalle_screen = self.manager.get_screen("meta_detalle")
        detalle_screen.set_context(self.usuario, meta, origen="usuario_metas")
        self.manager.current = "meta_detalle"

    def go_back(self, *args):
        self.manager.current = "home"



class MetaDetalleScreen(Screen):
    usuario = None
    meta = None
    origen_default = "usuario_metas"

    def set_context(self, usuario, meta, origen=None):
        self.usuario = usuario
        self.meta = meta
        self._origen = origen or self.origen_default
        Clock.schedule_once(lambda dt: self.actualizar_vista(), 0)  # ✅ llama bien

    def actualizar_vista(self):  # ✅ este es el que te falta
        if not (self.usuario and self.meta):
            return

        meta_id, curso, nombre, fecha, costo = self.meta
        ahorrado = DB.obtener_total_ahorrado(meta_id, self.usuario[0])
        faltante = max(float(costo) - ahorrado, 0.0)
        progreso = (ahorrado / float(costo) * 100) if float(costo) > 0 else 0
        progreso = min(progreso, 100)

        self.ids.meta_nombre.text = nombre
        self.ids.meta_fecha.text = f"Fecha: {fecha}"
        self.ids.meta_total.text = (
            f"Costo: {formato_pesos(costo)} | Ahorrado: {formato_pesos(ahorrado)} | "
            f"Faltante: {formato_pesos(faltante)} | {progreso:.2f}%"
        )
        self.ids.progress_bar_meta.value = progreso

    def ir_registrar_ahorro(self, *args):
        scr = self.manager.get_screen("registrar_ahorro")
        scr.set_context(self.usuario, self.meta, origen="meta_detalle")
        self.manager.current = "registrar_ahorro"

    def ir_registrar_salida(self, *args):
        scr = self.manager.get_screen("registrar_salida")
        scr.set_context(self.usuario, self.meta, origen="meta_detalle")
        self.manager.current = "registrar_salida"

    def ir_historial(self, *args):
        scr = self.manager.get_screen("historial")
        scr.set_context(self.usuario, self.meta, origen="meta_detalle")
        self.manager.current = "historial"

    def ir_detalle_plan(self, *args):
        scr = self.manager.get_screen("detalle_plan")
        scr.set_context(self.usuario, self.meta, origen="meta_detalle")
        self.manager.current = "detalle_plan"

    def volver_curso(self, *args):
        self.manager.current = self._origen

# ----------------------------- #
# SCREEN AHORRO
# ----------------------------- #
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from datetime import datetime

# ----------------------------- #
# SCREEN AHORRO
# ----------------------------- #
class RegistrarAhorroScreen(Screen):
    usuario = None
    meta = None
    origen = "meta_detalle"

    def set_context(self, usuario, meta, origen="meta_detalle"):
        self.usuario = usuario
        self.meta = meta
        self.origen = origen
        Clock.schedule_once(lambda dt: self._reset_fields(), 0)

    def _reset_fields(self):
        self.ids.monto.text = ""

    def guardar(self, *args):
        try:
            cantidad = parsear_monto(self.ids.monto.text)
            if cantidad <= 0:
                return
            user_id = self.usuario[0]
            meta_id = self.meta[0]

            fecha = datetime.now().strftime("%d/%m/%Y")
            # Guardar ahorro en DB
            DB.registrar_ahorro(meta_id, user_id, cantidad)

            # Actualizar pantallas
            self.manager.get_screen("meta_detalle").set_context(self.usuario, self.meta)
            self.manager.get_screen("historial").set_context(self.usuario, self.meta)
            self.manager.current = self.origen
        except Exception as e:
            print("❌ Error guardando ahorro:", e)

    def volver_meta(self, *args):
        self.manager.current = self.origen


# ----------------------------- #
# SCREEN SALIDA
# ----------------------------- #
class RegistrarSalidaScreen(Screen):
    usuario = None
    meta = None
    origen = "meta_detalle"

    def set_context(self, usuario, meta, origen="meta_detalle"):
        self.usuario = usuario
        self.meta = meta
        self.origen = origen
        Clock.schedule_once(lambda dt: self._reset_fields(), 0)

    def _reset_fields(self):
        self.ids.monto.text = ""

    def guardar(self, *args):
        try:
            cantidad = parsear_monto(self.ids.monto.text)
            if cantidad <= 0:
                return
            user_id = self.usuario[0]
            meta_id = self.meta[0]

            fecha = datetime.now().strftime("%d/%m/%Y")
            # Guardar salida en DB
            DB.registrar_salida(meta_id, user_id, cantidad)

            # Actualizar pantallas
            self.manager.get_screen("meta_detalle").set_context(self.usuario, self.meta)
            self.manager.get_screen("historial").set_context(self.usuario, self.meta)
            self.manager.current = self.origen
        except Exception as e:
            print("❌ Error guardando salida:", e)

    def volver_meta(self, *args):
        self.manager.current = self.origen



# ----------------------------- #
# SCREEN HISTORIAL
# ----------------------------- #
class HistorialScreen(Screen):
    usuario = None
    meta = None
    origen = "meta_detalle"

    def set_context(self, usuario, meta, origen="meta_detalle"):
        self.usuario = usuario
        self.meta = meta
        self.origen = origen
        Clock.schedule_once(lambda dt: self.cargar_historial(), 0)

    def cargar_historial(self, *args):
        # Limpiar la lista primero
        self.ids.lista.clear_widgets()

        if not (self.usuario and self.meta):
            print("⚠️ Usuario o meta no definidos")
            return

        user_id = self.usuario[0]
        meta_id = self.meta[0]
        print("DEBUG usuario_id:", user_id, "meta_id:", meta_id)

        try:
            conn = DB.conectar()
            cur = conn.cursor()
            cur.execute("""
                SELECT fecha, cantidad FROM ahorros WHERE meta_id=? AND usuario_id=?
                UNION ALL
                SELECT fecha, -cantidad FROM salidas WHERE meta_id=? AND usuario_id=?
                ORDER BY fecha DESC
            """, (meta_id, user_id, meta_id, user_id))
            rows = cur.fetchall()
            conn.close()
            print("DEBUG rows:", rows)
        except Exception as e:
            print("⚠️ No se pudo leer historial:", e)
            rows = []

        if not rows:
            lbl = MDLabel(
                text="No hay movimientos registrados",
                size_hint_y=None,
                height=dp(32),
                halign="center"
            )
            self.ids.lista.add_widget(lbl)
        else:
            for fecha, cantidad in rows:
                tipo = "Ahorro" if cantidad >= 0 else "Salida"
                lbl = MDLabel(
                    text=f"{fecha} | {formato_pesos(abs(cantidad))} | {tipo}",
                    size_hint_y=None,
                    height=dp(32),
                    halign="center"
                )
                print("Agregando al layout:", fecha, cantidad, tipo)
                self.ids.lista.add_widget(lbl)

    def volver_meta(self, *args):
        self.manager.current = self.origen




# ----------------------------- #
# SCREEN DETALLE PLAN
# ----------------------------- #
class DetallePlanScreen(Screen):
    usuario = None
    meta = None
    origen = "usuario_metas"

    def set_context(self, usuario, meta, origen="usuario_metas"):
        self.usuario = usuario
        self.meta = meta
        self.origen = origen
        Clock.schedule_once(lambda dt: self.refrescar(), 0)

    def refrescar(self, *args):
        if not (self.usuario and self.meta):
            return

        user_id = self.usuario[0]
        meta_id, curso, nombre, fecha, costo = self.meta

        ahorrado = DB.obtener_total_ahorrado(meta_id, user_id)
        faltante = max(float(costo) - ahorrado, 0.0)

        # Actualizar labels usando ids
        self.ids.meta_nombre.text = nombre
        self.ids.meta_fecha.text = f"Fecha límite: {fecha}"
        self.ids.meta_costo.text = f"Costo: {formato_pesos(costo)}"
        self.ids.meta_ahorrado.text = f"Ahorrado: {formato_pesos(ahorrado)}"
        self.ids.meta_faltante.text = f"Faltante: {formato_pesos(faltante)}"

    def volver_meta(self):
        self.manager.current = self.origen



class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(transition=FadeTransition(), **kwargs)


class MyApp(MDApp):
    def build(self):
        DB.crear_tabla()
        DB.crear_tablas()  # Ya crea todas las tablas y admin

        Builder.load_file("app.kv")

        sm = MyScreenManager()  # <- usar tu ScreenManager con FadeTransition

        # Agregar todas las pantallas
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(AdminPanelScreen(name="admin_panel"))
        sm.add_widget(MetasScreen(name="metas"))
        sm.add_widget(AgregarMetaScreen(name="agregar_meta"))
        sm.add_widget(UsuarioMetasScreen(name="usuario_metas"))
        sm.add_widget(MetaDetalleScreen(name="meta_detalle"))
        sm.add_widget(RegistrarAhorroScreen(name="registrar_ahorro"))
        sm.add_widget(RegistrarSalidaScreen(name="registrar_salida"))
        sm.add_widget(HistorialScreen(name="historial"))
        sm.add_widget(DetallePlanScreen(name="detalle_plan"))


        return sm


# Función genérica para mostrar popup (dummy, ajústala si ya tienes una definida)
def mostrar_popup(titulo, mensaje):
    from kivy.uix.popup import Popup
    from kivy.uix.label import Label
    popup = Popup(title=titulo,
                  content=Label(text=mensaje),
                  size_hint=(0.7, 0.4))
    popup.open()


if __name__ == "__main__":
    MyApp().run()
