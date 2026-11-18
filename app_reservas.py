# -*- coding: utf-8 -*-
"""
Aplicación de escritorio del Sistema de Reservas (interfaz gráfica).
Reutiliza las clases del taller (Cliente, Habitacion, Reserva,
GestorReservas, RepositorioSQLite) sin modificar la lógica de negocio.

Leonardo Alexander Villalobos Patiño - Ingeniería de Software, UMB.
"""
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox
from datetime import date, datetime

from sistema_reservas import (Cliente, Habitacion, Reserva,
                              GestorReservas, RepositorioSQLite,
                              NOMBRE_BD)


# ---------- paleta sobria (rojo vino + neutros) ----------
CLARO = "#F6F3F3"      # fondo general
BLANCO = "#FFFFFF"     # tarjetas y campos
TINTA = "#2B2426"      # texto principal
SUAVE = "#6B5C62"      # texto secundario
BORDE = "#D4C7C7"      # bordes de campos
PRINCIPAL = "#8C2B2B"      # botón principal / cabeceras
PRINCIPAL_OSC = "#6E2020"  # hover del botón principal
ACENTO = "#B08A47"     # acento dorado (títulos / filas alternas)

class AppReservas(tk.Tk):
    """Ventana principal: panel izquierdo de acciones + tabla de reservas."""

    def __init__(self):
        super().__init__()
        self.title("Sistema de Reservas — Hotel UMB")
        self.geometry("980x640")
        self.minsize(760, 520)
        self.configure(bg=CLARO)

        self.gestor = GestorReservas(RepositorioSQLite(NOMBRE_BD))
        if not self.gestor.habitaciones:
            from sistema_reservas import cargar_datos_iniciales
            cargar_datos_iniciales(self.gestor)

        self._montar_estilos()
        self._montar_widgets()
        self.refrescar_reservas()

    # ---------------- estilos ttk ----------------
    def _montar_estilos(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        base = tkfont.nametofont("TkDefaultFont")
        base.configure(family="Segoe UI", size=10)
        for nombre in ("Treeview", "Treeview.Heading"):
            estilo.configure(nombre, background=BLANCO,
                             fieldbackground=BLANCO, foreground=TINTA,
                             font=("Segoe UI", 10), rowheight=26,
                             borderwidth=0)
        estilo.configure("Treeview.Heading", background=PRINCIPAL,
                          foreground=BLANCO, font=("Segoe UI", 10, "bold"),
                          relief="flat")
        estilo.map("Treeview", background=[("selected", "#E8DCDC")],
                   foreground=[("selected", TINTA)])
        estilo.map("Treeview.Heading", background=[("active", PRINCIPAL)])
        estilo.configure("TCombobox", fieldbackground=BLANCO,
                         background=CLARO, arrowsize=14)

    # ---------------- construcción de la interfaz ----------------
    def _montar_widgets(self):
        # >>> cabecera
        cab = tk.Frame(self, bg=PRINCIPAL, height=64)
        cab.pack(fill="x", side="top")
        cab.pack_propagate(False)
        tk.Label(cab, text="SISTEMA DE RESERVAS", font=("Segoe UI", 16, "bold"),
                 fg=BLANCO, bg=PRINCIPAL).pack(side="left", padx=(24, 0), pady=16)
        self.lbl_estado = tk.Label(cab, text="", font=("Segoe UI", 10),
                                   fg="#E8CFCF", bg=PRINCIPAL, anchor="e")
        self.lbl_estado.pack(side="right", padx=(0, 24))

        # >>> cuerpo: panel izquierdo (acciones) + derecho (tabla)
        cuerpo = tk.Frame(self, bg=CLARO)
        cuerpo.pack(fill="both", expand=True, padx=16, pady=(16, 8))
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(0, weight=1)

        panel = tk.Frame(cuerpo, bg=BLANCO, highlightthickness=1,
                         highlightbackground=BORDE)
        panel.grid(row=0, column=0, sticky="nsw", padx=(0, 12))
        self._panel_acciones(panel)

        tabla = tk.Frame(cuerpo, bg=BLANCO, highlightthickness=1,
                         highlightbackground=BORDE)
        tabla.grid(row=0, column=1, sticky="nsew")
        self._panel_tabla(tabla)

        self.lbl_detalle = tk.Label(self, text="", font=("Segoe UI", 9),
                                    fg=SUAVE, bg=CLARO, anchor="w",
                                    justify="left")
        self.lbl_detalle.pack(fill="x", padx=16, pady=(4, 10))

    def _panel_acciones(self, panel):
        tk.Label(panel, text="ACCIONES", font=("Segoe UI", 10, "bold"),
                 fg=SUAVE, bg=BLANCO, anchor="w").pack(fill="x",
                                                       padx=16, pady=(14, 2))
        for etiqueta, comando in (
                ("  Registrar cliente  ", self.registrar_cliente),
                ("  Registrar reserva  ", self.registrar_reserva),
                ("  Consultar disponibilidad  ", self.consultar_disponibilidad),
                ("  Cancelar reserva  ", self.cancelar_reserva),
                ("  Actualizar estados  ", self.actualizar_estados),
                ("  Ver auditoría  ", self.ver_auditoria)):
            btn = tk.Button(panel, text=etiqueta.strip(), command=comando,
                            font=("Segoe UI", 10), cursor="hand2",
                            bg=BLANCO, fg=TINTA, activebackground="#EDE3E3",
                            activeforeground=TINTA, relief="flat",
                            overrelief="flat", bd=0, highlightthickness=1,
                            highlightbackground=BORDE, highlightcolor=PRINCIPAL,
                            padx=14, pady=7, anchor="w")
            btn.pack(fill="x", padx=16, pady=4)
        tk.Frame(panel, bg=BORDE, height=1).pack(fill="x",
                                                 padx=16, pady=(10, 4))
        tk.Label(panel, text="SEDE DE DATOS", font=("Segoe UI", 10, "bold"),
                 fg=SUAVE, bg=BLANCO, anchor="w").pack(fill="x",
                                                       padx=16, pady=(0, 2))
        tk.Label(panel, text=f"Base de datos SQLite:\n{NOMBRE_BD} (guardado "
                             "automático)", font=("Segoe UI", 9),
                 fg=SUAVE, bg=BLANCO, anchor="w", justify="left"
                 ).pack(fill="x", padx=16, pady=(0, 6))
        tk.Button(panel, text="Reiniciar base de datos", command=self.resetear_bd,
                  font=("Segoe UI", 9), cursor="hand2", fg=ACENTO, bg=BLANCO,
                  activebackground="#F5EFDF", activeforeground=ACENTO,
                  relief="flat", bd=0, padx=14, pady=6, anchor="w"
                  ).pack(fill="x", padx=16, pady=(2, 14), side="bottom")

    def _panel_tabla(self, tabla):
        tk.Label(tabla, text="RESERVAS REGISTRADAS", font=("Segoe UI", 10, "bold"),
                 fg=SUAVE, bg=BLANCO, anchor="w").pack(fill="x",
                                                       padx=14, pady=(12, 4))
        marco = tk.Frame(tabla, bg=BLANCO)
        marco.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        columnas = ("id", "cliente", "habitacion", "ingreso", "salida",
                    "noches", "costo", "estado")
        self.tabla = ttk.Treeview(marco, columns=columnas, show="headings",
                                  selectmode="browse")
        encabezados = {"id": "ID", "cliente": "Cliente", "habitacion": "Hab.",
                       "ingreso": "Ingreso", "salida": "Salida",
                       "noches": "Noches", "costo": "Costo total",
                       "estado": "Estado"}
        anchos = {"id": 44, "cliente": 170, "habitacion": 50, "ingreso": 78,
                  "salida": 78, "noches": 56, "costo": 90, "estado": 84}
        for col in columnas:
            self.tabla.heading(col, text=encabezados[col])
            self.tabla.column(col, width=anchos[col], anchor="center",
                              stretch=(col in ("cliente", "costo")))
        alt = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=alt.set)
        alt.pack(side="right", fill="y")
        self.tabla.pack(fill="both", expand=True)
        self.tabla.tag_configure("alterna", background="#F5EFEF")
        self.tabla.tag_configure("Cancelada", foreground="#9C6B54")
        self.tabla.tag_configure("Finalizada", foreground=SUAVE)
        self.tabla.tag_configure("Confirmada", foreground="#A52323",
                                  font=("Segoe UI", 10, "bold"))
        self.tabla.tag_configure("En curso", foreground=ACENTO)
        self.tabla.bind("<<Double-1>>",
                        lambda _e: self._detalle_reserva_seleccionada())

    # ---------------- helpers ----------------
    def _fecha_de_hoy(self):
        return date.today()

    def _dialogo(self, titulo, campos):
        """Ventana modal genérica: devuelve dict con los valores o None."""
        win = tk.Toplevel(self)
        win.title(titulo)
        win.configure(bg=BLANCO, padx=18, pady=14)
        win.transient(self); win.grab_set(); win.resizable(False, False)
        win.geometry(f"+{self.winfo_rootx() + 80}+{self.winfo_rooty() + 80}")
        variables, fila = {}, 0
        for etiqueta, tipo, opciones in campos:
            tk.Label(win, text=etiqueta, font=("Segoe UI", 10), fg=TINTA,
                     bg=BLANCO).grid(row=fila, column=0, sticky="w",
                                     pady=5, padx=(0, 10))
            if tipo == "combo":
                var = tk.StringVar()
                ttk.Combobox(win, textvariable=var, values=opciones,
                             state="readonly", width=28).grid(row=fila,
                                                              column=1, pady=5)
            else:
                var = tk.StringVar()
                tk.Entry(win, textvariable=var, width=30, font=("Segoe UI", 10),
                         relief="solid", bd=0, highlightthickness=1,
                         highlightbackground=BORDE, highlightcolor=PRINCIPAL
                         ).grid(row=fila, column=1, pady=5)
            variables[etiqueta] = var
            fila += 1
        resultado = {}
        def aceptar():
            for nombre, var in variables.items():
                resultado[nombre] = var.get().strip()
            win.destroy()
        def cancelar():
            resultado.clear()
            win.destroy()
        botones = tk.Frame(win, bg=BLANCO)
        botones.grid(row=fila, column=0, columnspan=2, pady=(14, 0))
        tk.Button(botones, text="Aceptar", command=aceptar, font=("Segoe UI", 10),
                  bg=PRINCIPAL, fg=BLANCO, activebackground=PRINCIPAL_OSC,
                  activeforeground=BLANCO, relief="flat", padx=18, pady=6,
                  cursor="hand2").pack(side="left", padx=6)
        tk.Button(botones, text="Cancelar", command=cancelar,
                  font=("Segoe UI", 10), bg=BLANCO, fg=TINTA,
                  highlightthickness=1, highlightbackground=BORDE,
                  activebackground="#EDE3E3", relief="flat", padx=18, pady=6,
                  cursor="hand2").pack(side="left", padx=6)
        win.wait_window()
        return resultado or None

    def _seleccion(self):
        item = self.tabla.selection()
        if not item:
            messagebox.showwarning("Reservas", "Seleccione una reserva "
                                            "de la tabla.")
            return None
        return self.tabla.item(item[0])["values"]

    # ---------------- refresco de la tabla ----------------
    def refrescar_reservas(self):
        self.tabla.delete(*self.tabla.get_children())
        for i, r in enumerate(self.gestor.reservas):
            etiquetas = ["alterna"] if i % 2 else []
            etiquetas.append(r.estado)
            self.tabla.insert("", "end", values=(
                r.id_reserva, r.cliente.nombre_completo,
                r.habitacion.numero, f"{r.fecha_ingreso:%d/%m/%Y}",
                f"{r.fecha_salida:%d/%m/%Y}", r.noches,
                f"${r.costo_total:,}", r.estado), tags=etiquetas)
        total = len(self.gestor.reservas)
        self.lbl_estado.config(
            text=f"Base: {NOMBRE_BD}   |   {total} reserva"
                 f"{'s' if total != 1 else ''}   |   "
                 f"{len(self.gestor.clientes)} clientes · "
                 f"{len(self.gestor.habitaciones)} habitaciones")

    # ---------------- acciones ----------------
    def registrar_cliente(self):
        datos = self._dialogo("Registrar cliente", (
            ("ID del cliente", "texto", None),
            ("Nombres", "texto", None),
            ("Apellidos", "texto", None),
            ("Documento", "texto", None)))
        if datos is None:
            return
        try:
            id_cliente = int(datos["ID del cliente"])
        except ValueError:
            messagebox.showerror("Validación",
                                 "El ID del cliente debe ser un número.")
            return
        nombres = datos["Nombres"]
        apellidos = datos["Apellidos"]
        documento = datos["Documento"]
        if not (nombres and apellidos and documento):
            messagebox.showerror("Validación",
                                 "Nombres, apellidos y documento son "
                                 "obligatorios.")
            return
        if self.gestor.buscar_cliente(id_cliente) is not None:
            messagebox.showerror(
                "Registrar cliente",
                f"Ya existe un cliente con el ID {id_cliente} "
                f"({self.gestor.buscar_cliente(id_cliente).nombre_completo}).")
            return
        self.gestor.registrar_cliente(Cliente(id_cliente, nombres, apellidos,
                                              documento))
        self.refrescar_reservas()
        messagebox.showinfo(
            "Registrar cliente",
            f"Éxito: cliente {id_cliente} ({apellidos.upper()}, {nombres}) "
            "registrado y guardado en la base de datos.")

    def registrar_reserva(self):
        habitaciones = [str(h.numero) for h in self.gestor.habitaciones]
        clientes = [f"{c.id_cliente} — {c.nombre_completo}"
                    for c in self.gestor.clientes]
        datos = self._dialogo("Registrar reserva", (
            ("ID de la reserva", "texto", None),
            ("Cliente", "combo", clientes),
            ("Habitación", "combo", habitaciones),
            ("Fecha de ingreso (AAAA-MM-DD)", "texto", None),
            ("Número de noches", "texto", None)))
        if datos is None:
            return
        try:
            id_reserva = int(datos["ID de la reserva"])
            id_cliente = int(datos["Cliente"].split(" — ")[0])
            numero_hab = int(datos["Habitación"])
            noches = int(datos["Número de noches"])
            fecha = datetime.strptime(datos["Fecha de ingreso (AAAA-MM-DD)"],
                                      "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Validación",
                                 "Revise los datos: el ID, la habitación y "
                                 "las noches deben ser números, y la fecha "
                                 "debe venir como AAAA-MM-DD.")
            return
        mensaje = self.gestor.registrar_reserva(id_reserva, id_cliente,
                                                 numero_hab, fecha, noches)
        self.refrescar_reservas()
        (messagebox.showinfo if mensaje.startswith("Éxito")
         else messagebox.showerror)("Registrar reserva", mensaje)

    def consultar_disponibilidad(self):
        habitaciones = [str(h.numero) for h in self.gestor.habitaciones]
        datos = self._dialogo("Consultar disponibilidad", (
            ("Habitación", "combo", habitaciones),
            ("Fecha de ingreso (AAAA-MM-DD)", "texto", None),
            ("Número de noches", "texto", None)))
        if datos is None:
            return
        try:
            numero_hab = int(datos["Habitación"])
            fecha = datetime.strptime(datos["Fecha de ingreso (AAAA-MM-DD)"],
                                      "%Y-%m-%d").date()
            noches = int(datos["Número de noches"])
        except ValueError:
            messagebox.showerror("Validación",
                                 "La fecha debe venir como AAAA-MM-DD y las "
                                 "noches deben ser un número.")
            return
        habitacion = self.gestor.buscar_habitacion(numero_hab)
        if habitacion is None:
            messagebox.showerror("Disponibilidad", "Esa habitación no existe.")
            return
        disponible = self.gestor.verificar_disponibilidad(habitacion, fecha,
                                                           noches)
        messagebox.showinfo(
            "Disponibilidad",
            f"Habitación {numero_hab} ({habitacion.tipo}) para "
            f"{noches} noche(s) desde el {fecha:%d/%m/%Y}:\n\n"
            + ("DISPONIBLE — puede registrarse la reserva."
               if disponible else
               "NO DISPONIBLE — ya existe una reserva en esas fechas."))

    def cancelar_reserva(self):
        valores = self._seleccion()
        if valores is None:
            return
        id_reserva = int(valores[0])
        if messagebox.askyesno("Cancelar reserva",
                               f"¿Cancelar la reserva {id_reserva} de "
                               f"{valores[1]}?"):
            mensaje = self.gestor.cancelar_reserva(id_reserva)
            self.refrescar_reservas()
            (messagebox.showinfo if mensaje.startswith("Éxito")
             else messagebox.showerror)("Cancelar reserva", mensaje)

    def actualizar_estados(self):
        self.gestor.actualizar_estados(self._fecha_de_hoy())
        self.refrescar_reservas()
        messagebox.showinfo("Actualizar estados",
                            "Estados recalculados con la fecha de hoy "
                            f"({self._fecha_de_hoy():%d/%m/%Y}).")

    def ver_auditoria(self):
        lineas = []
        for evento in self.gestor.iterar_eventos():
            lineas.append(f"{evento['consecutivo']:>3}. {evento['operacion']:<12}"
                          f" reserva {evento['id_reserva']:<6} "
                          f"{evento['fecha']}  ({evento['usuario']})")
        texto = "\n".join(lineas) or "Sin eventos registrados."
        win = tk.Toplevel(self)
        win.title("Auditoría de reservas")
        win.configure(bg=BLANCO, padx=16, pady=12)
        # centrada sobre la ventana principal y con título interno
        self.update_idletasks()
        ancho, alto = 560, 360
        x = self.winfo_rootx() + (self.winfo_width() - ancho) // 2
        y = self.winfo_rooty() + (self.winfo_height() - alto) // 2
        win.geometry(f"{ancho}x{alto}+{max(x, 0)}+{max(y, 0)}")
        tk.Label(win, text="AUDITORÍA DE RESERVAS",
                 font=("Segoe UI", 11, "bold"), fg=PRINCIPAL, bg=BLANCO
                 ).pack(fill="x", pady=(0, 8))
        txt = tk.Text(win, font=("Consolas", 10), bg=BLANCO, fg=TINTA,
                      relief="flat", wrap="none")
        txt.insert("1.0", texto); txt.config(state="disabled")
        txt.pack(fill="both", expand=True)
        tk.Button(win, text="Cerrar", command=win.destroy,
                  font=("Segoe UI", 10), bg=PRINCIPAL, fg=BLANCO,
                  activebackground=PRINCIPAL_OSC, relief="flat", padx=18, pady=6,
                  cursor="hand2").pack(pady=(10, 0))

    def resetear_bd(self):
        if not messagebox.askyesno("Reiniciar base de datos",
                                   "Se borrarán TODAS las reservas, "
                                   "clientes y habitaciones guardadas, "
                                   "y se volverán a cargar los datos de "
                                   "ejemplo. ¿Continuar?"):
            return
        import os
        from sistema_reservas import cargar_datos_iniciales
        if os.path.exists(NOMBRE_BD):
            os.remove(NOMBRE_BD)
        self.gestor = GestorReservas(RepositorioSQLite(NOMBRE_BD))
        cargar_datos_iniciales(self.gestor)
        self.refrescar_reservas()
        messagebox.showinfo("Reiniciar base de datos",
                            "Base recreada con los datos de ejemplo.")

    def _detalle_reserva_seleccionada(self):
        valores = self._seleccion()
        if valores is None:
            return
        r = next((x for x in self.gestor.reservas
                  if x.id_reserva == int(valores[0])), None)
        if r is None:
            return
        habitacion = r.habitacion
        self.lbl_detalle.config(
            text=f"Reserva {r.id_reserva} · {r.cliente.nombre_completo} · "
                 f"Hab. {habitacion.numero} ({habitacion.tipo}, "
                 f"${habitacion.tarifa_noche:,}/noche) · "
                 f"{r.noches} noche(s) · total ${r.costo_total:,} · "
                 f"estado {r.estado}")


if __name__ == "__main__":
    app = AppReservas()
    app.mainloop()
