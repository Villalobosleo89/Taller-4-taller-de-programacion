# -*- coding: utf-8 -*-
"""
Sistema de Reservas de Hotel - Taller de Programación Orientada a Objetos
Nivel intermedio-avanzado: clases, objetos, atributos y métodos.
Incluye persistencia en base de datos SQLite (reservas.db).
Leonardo Alexander Villalobos Patiño - Ingeniería de Software, UMB.
"""
import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta

NOMBRE_BD = "reservas.db"


class Cliente:
    """Representa al huésped del hotel (Atributos privados + propiedades)."""

    def __init__(self, id_cliente, nombres, apellidos, documento):
        self._id_cliente = id_cliente      # atributo privado por convención _
        self._nombres = nombres
        self._apellidos = apellidos
        self._documento = documento

    @property
    def id_cliente(self):
        return self._id_cliente

    @property
    def nombres(self):
        return self._nombres

    @property
    def apellidos(self):
        return self._apellidos

    @property
    def documento(self):
        return self._documento

    @property
    def nombre_completo(self):
        """Propiedad calculada: apellidos en mayúsculas + nombres."""
        return f"{self._apellidos.upper()}, {self._nombres}"

    def __str__(self):
        return (f"Cliente [{self._id_cliente}] {self.nombre_completo} "
                f"- Doc: {self._documento}")


class Habitacion:
    """Representa una habitación del hotel con su tarifa y capacidad."""

    def __init__(self, numero, tipo, tarifa_noche, capacidad):
        self._numero = numero
        self._tipo = tipo
        self._tarifa_noche = tarifa_noche
        self._capacidad = capacidad

    @property
    def numero(self):
        return self._numero

    @property
    def tipo(self):
        return self._tipo

    @property
    def tarifa_noche(self):
        return self._tarifa_noche

    @tarifa_noche.setter
    def tarifa_noche(self, valor):
        """Setter con validación de negocio (equivalente a un trigger)."""
        if valor <= 0:
            raise ValueError("Error: la tarifa por noche debe ser mayor que 0")
        self._tarifa_noche = valor

    @property
    def capacidad(self):
        return self._capacidad

    def __str__(self):
        return (f"Habitación {self._numero} ({self._tipo}) "
                f"- Tarifa: ${self._tarifa_noche:,}/noche "
                f"- Capacidad: {self._capacidad} huéspedes")


class Reserva:
    """Representa la reserva de una habitación por un cliente."""

    ESTADOS_VALIDOS = ("Confirmada", "En curso", "Finalizada",
                       "Cancelada", "Expirada")

    def __init__(self, id_reserva, cliente, habitacion,
                 fecha_ingreso, noches):
        # Validación de negocio al construir el objeto (como BEFORE INSERT)
        if not isinstance(fecha_ingreso, date):
            raise TypeError("Error: la fecha de ingreso debe ser de tipo date")
        if noches <= 0 or noches > 30:
            raise ValueError("Error: el número de noches debe estar "
                             "entre 1 y 30")
        self._id_reserva = id_reserva
        self._cliente = cliente
        self._habitacion = habitacion
        self._fecha_ingreso = fecha_ingreso
        self._noches = noches
        self._estado = "Confirmada"

    @property
    def id_reserva(self):
        return self._id_reserva

    @property
    def cliente(self):
        return self._cliente

    @property
    def habitacion(self):
        return self._habitacion

    @property
    def fecha_ingreso(self):
        return self._fecha_ingreso

    @property
    def noches(self):
        return self._noches

    @property
    def estado(self):
        return self._estado

    @noches.setter
    def noches(self, valor):
        if valor <= 0 or valor > 30:
            raise ValueError("Error: el número de noches debe estar "
                             "entre 1 y 30")
        self._noches = valor

    @property
    def fecha_salida(self):
        """Propiedad calculada a partir de otros atributos."""
        return self._fecha_ingreso + timedelta(days=self._noches)

    @property
    def costo_total(self):
        """Lógica de negocio compleja: descuento según número de noches."""
        subtotal = self._noches * self._habitacion.tarifa_noche
        if self._noches >= 10:
            descuento = 0.20
        elif self._noches >= 5:
            descuento = 0.10
        else:
            descuento = 0.00
        return round(subtotal * (1 - descuento))

    @staticmethod
    def es_fecha_valida(texto):
        """Método estático: valida el formato AAAA-MM-DD sin usar self."""
        try:
            datetime.strptime(texto, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @classmethod
    def crear_por_texto(cls, id_reserva, cliente, habitacion,
                        fecha_texto, noches):
        """Método de clase: constructor alternativo desde texto."""
        if not cls.es_fecha_valida(fecha_texto):
            raise ValueError("Error: fecha inválida, use AAAA-MM-DD")
        fecha = datetime.strptime(fecha_texto, "%Y-%m-%d").date()
        return cls(id_reserva, cliente, habitacion, fecha, noches)

    def se_solapa_con(self, otra_reserva):
        """Determina si dos reservas de la misma habitación comparten fechas."""
        return (self._fecha_ingreso < otra_reserva.fecha_salida
                and otra_reserva.fecha_ingreso < self.fecha_salida)

    def actualizar_estado(self, fecha_actual):
        """Actualiza el estado comparando las fechas con la fecha actual."""
        if self._estado == "Cancelada":
            return
        if fecha_actual < self._fecha_ingreso:
            self._estado = "Confirmada"
        elif fecha_actual < self.fecha_salida:
            self._estado = "En curso"
        else:
            self._estado = "Finalizada"

    def cancelar(self):
        if self._estado in ("Finalizada", "Cancelada"):
            return (f"Error: la reserva {self._id_reserva} no puede "
                    f"cancelarse ({self._estado}).")
        self._estado = "Cancelada"
        return f"Éxito: reserva {self._id_reserva} cancelada."

    def restaurar_estado(self, estado):
        """Restaura el estado guardado al reconstruir la base de datos."""
        if estado in self.ESTADOS_VALIDOS:
            self._estado = estado

    def __str__(self):
        return (f"Reserva {self._id_reserva} | {self.cliente.nombre_completo} "
                f"| Hab {self.habitacion.numero} | "
                f"{self._fecha_ingreso:%d/%m/%Y} -> "
                f"{self.fecha_salida:%d/%m/%Y} ({self._noches} noches) "
                f"| ${self.costo_total:,} | Estado: {self._estado}")


class AuditoriaReservas:
    """Registro automático de operaciones (equivalente a un trigger
    AFTER INSERT sobre la tabla de auditoría)."""

    def __init__(self):
        self._eventos = []

    def registrar(self, operacion, id_reserva, detalle=""):
        """Guarda el evento y lo devuelve para que pueda persistirse."""
        evento = {
            "consecutivo": len(self._eventos) + 1,
            "operacion": operacion,
            "id_reserva": id_reserva,
            "detalle": detalle,
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "usuario": "recepcion",
        }
        self._eventos.append(evento)
        return evento

    def restaurar(self, eventos):
        """Carga los eventos guardados en la base de datos."""
        self._eventos = list(eventos)

    def __iter__(self):
        """Convierte la auditoría en un objeto iterable."""
        return iter(self._eventos)

    def __str__(self):
        lineas = ["CONSECUTIVO | OPERACIÓN | RESERVA | FECHA | USUARIO"]
        for evento in self:
            lineas.append(
                f"{evento['consecutivo']:>11} | {evento['operacion']:<12} | "
                f"{str(evento['id_reserva']):>7} | {evento['fecha']} | "
                f"{evento['usuario']}")
        return "\n".join(lineas)


class RepositorioSQLite:
    """Capa de persistencia: guarda y recupera los objetos en SQLite.

    El gestor la recibe por inyección de dependencias: con ella, cada
    operación queda guardada en la base de datos; sin ella, el sistema
    funciona únicamente en memoria (actividades 1 a 5).
    """

    def __init__(self, nombre_bd=NOMBRE_BD):
        self._nombre_bd = nombre_bd
        self._crear_tablas()

    def _conectar(self):
        """Abre una conexión con el archivo de la base de datos."""
        return sqlite3.connect(self._nombre_bd)

    def _ejecutar(self, sentencia, parametros=()):
        """Ejecuta una sentencia de escritura y cierra la conexión."""
        with closing(self._conectar()) as conexion:
            with conexion:
                conexion.execute(sentencia, parametros)

    def _consultar(self, sentencia, parametros=()):
        """Ejecuta una consulta SELECT y devuelve todas las filas."""
        with closing(self._conectar()) as conexion:
            return conexion.execute(sentencia, parametros).fetchall()

    def _crear_tablas(self):
        """Crea el esquema si no existe (CREATE TABLE IF NOT EXISTS)."""
        with closing(self._conectar()) as conexion:
            with conexion:
                conexion.execute(
                    "CREATE TABLE IF NOT EXISTS CLIENTES ("
                    "id INTEGER PRIMARY KEY,"
                    "nombres TEXT NOT NULL,"
                    "apellidos TEXT NOT NULL,"
                    "documento TEXT NOT NULL)")
                conexion.execute(
                    "CREATE TABLE IF NOT EXISTS HABITACIONES ("
                    "numero INTEGER PRIMARY KEY,"
                    "tipo TEXT NOT NULL,"
                    "tarifa_noche REAL NOT NULL,"
                    "capacidad INTEGER NOT NULL)")
                conexion.execute(
                    "CREATE TABLE IF NOT EXISTS RESERVAS ("
                    "id_reserva INTEGER PRIMARY KEY,"
                    "id_cliente INTEGER NOT NULL,"
                    "numero_habitacion INTEGER NOT NULL,"
                    "fecha_ingreso TEXT NOT NULL,"
                    "noches INTEGER NOT NULL,"
                    "estado TEXT NOT NULL,"
                    "FOREIGN KEY (id_cliente) REFERENCES CLIENTES(id),"
                    "FOREIGN KEY (numero_habitacion)"
                    " REFERENCES HABITACIONES(numero))")
                conexion.execute(
                    "CREATE TABLE IF NOT EXISTS AUDITORIA ("
                    "consecutivo INTEGER PRIMARY KEY AUTOINCREMENT,"
                    "operacion TEXT NOT NULL,"
                    "id_reserva INTEGER NOT NULL,"
                    "fecha TEXT NOT NULL,"
                    "usuario TEXT NOT NULL)")

    def guardar_cliente(self, cliente):
        """Persiste un cliente (INSERT OR REPLACE sobre CLIENTES)."""
        self._ejecutar(
            "INSERT OR REPLACE INTO CLIENTES (id, nombres, apellidos,"
            " documento) VALUES (?, ?, ?, ?)",
            (cliente.id_cliente, cliente.nombres, cliente.apellidos,
             cliente.documento))

    def guardar_habitacion(self, habitacion):
        """Persiste una habitación (INSERT OR REPLACE sobre HABITACIONES)."""
        self._ejecutar(
            "INSERT OR REPLACE INTO HABITACIONES (numero, tipo,"
            " tarifa_noche, capacidad) VALUES (?, ?, ?, ?)",
            (habitacion.numero, habitacion.tipo,
             habitacion.tarifa_noche, habitacion.capacidad))

    def guardar_reserva(self, reserva):
        """Persiste la reserva junto con el estado que tenga en memoria."""
        self._ejecutar(
            "INSERT OR REPLACE INTO RESERVAS (id_reserva, id_cliente,"
            " numero_habitacion, fecha_ingreso, noches, estado)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (reserva.id_reserva, reserva.cliente.id_cliente,
             reserva.habitacion.numero,
             f"{reserva.fecha_ingreso:%Y-%m-%d}",
             reserva.noches, reserva.estado))

    def guardar_evento(self, evento):
        """Persiste un evento de auditoría (INSERT sobre AUDITORIA)."""
        self._ejecutar(
            "INSERT INTO AUDITORIA (operacion, id_reserva, fecha, usuario)"
            " VALUES (?, ?, ?, ?)",
            (evento["operacion"], evento["id_reserva"],
             evento["fecha"], evento["usuario"]))

    def cargar_todo(self):
        """SELECT de las tres tablas y reconstrucción de los objetos."""
        clientes = []
        for id_cliente, nombres, apellidos, documento in self._consultar(
                "SELECT id, nombres, apellidos, documento FROM CLIENTES"):
            clientes.append(Cliente(id_cliente, nombres, apellidos,
                                    documento))
        habitaciones = []
        for numero, tipo, tarifa, capacidad in self._consultar(
                "SELECT numero, tipo, tarifa_noche, capacidad"
                " FROM HABITACIONES"):
            # REAL devuelve 120000.0: se normaliza de nuevo a entero
            habitaciones.append(Habitacion(numero, tipo, int(tarifa),
                                            capacidad))
        clientes_por_id = {c.id_cliente: c for c in clientes}
        habitaciones_por_numero = {h.numero: h for h in habitaciones}
        reservas = []
        for (id_reserva, id_cliente, numero, fecha_texto, noches,
                estado) in self._consultar(
                "SELECT id_reserva, id_cliente, numero_habitacion,"
                " fecha_ingreso, noches, estado FROM RESERVAS"):
            reserva = Reserva(id_reserva,
                             clientes_por_id[id_cliente],
                             habitaciones_por_numero[numero],
                             datetime.strptime(fecha_texto,
                                               "%Y-%m-%d").date(),
                             noches)
            reserva.restaurar_estado(estado)
            reservas.append(reserva)
        return clientes, habitaciones, reservas

    def cargar_eventos(self):
        """SELECT de los eventos de auditoría, en orden de consecutivo."""
        eventos = []
        for consecutivo, operacion, id_reserva, fecha, usuario in (
                self._consultar(
                    "SELECT consecutivo, operacion, id_reserva, fecha,"
                    " usuario FROM AUDITORIA ORDER BY consecutivo")):
            eventos.append({
                "consecutivo": consecutivo,
                "operacion": operacion,
                "id_reserva": id_reserva,
                "detalle": "",
                "fecha": fecha,
                "usuario": usuario,
            })
        return eventos


class GestorReservas:
    """Administra clientes, habitaciones, reservas y disponibilidad.

    Recibe el repositorio por inyección de dependencias: con él cada
    operación queda guardada en la base de datos; sin él, el sistema
    opera únicamente en memoria.
    """

    def __init__(self, repositorio=None):
        self._clientes = []
        self._habitaciones = []
        self._reservas = []
        self._auditoria = AuditoriaReservas()
        self._repositorio = repositorio
        if repositorio is not None:
            self._cargar_de_bd()

    def _cargar_de_bd(self):
        """Reconstruye los objetos del dominio desde las tablas."""
        clientes, habitaciones, reservas = self._repositorio.cargar_todo()
        self._clientes.extend(clientes)
        self._habitaciones.extend(habitaciones)
        self._reservas.extend(reservas)
        self._auditoria.restaurar(self._repositorio.cargar_eventos())

    @property
    def reservas(self):
        return list(self._reservas)        # copia defensiva (encapsulamiento)

    @property
    def habitaciones(self):
        return list(self._habitaciones)

    @property
    def clientes(self):
        return list(self._clientes)        # copia defensiva (encapsulamiento)

    def registrar_cliente(self, cliente):
        self._clientes.append(cliente)
        if self._repositorio is not None:
            self._repositorio.guardar_cliente(cliente)

    def registrar_habitacion(self, habitacion):
        self._habitaciones.append(habitacion)
        if self._repositorio is not None:
            self._repositorio.guardar_habitacion(habitacion)

    def buscar_cliente(self, id_cliente):
        for cliente in self._clientes:
            if cliente.id_cliente == id_cliente:
                return cliente
        return None

    def buscar_habitacion(self, numero):
        for habitacion in self._habitaciones:
            if habitacion.numero == numero:
                return habitacion
        return None

    def verificar_disponibilidad(self, habitacion, fecha_ingreso, noches):
        """Devuelve True si la habitación está libre en el rango pedido."""
        provisional = Reserva(0, None, habitacion, fecha_ingreso, noches)
        for reserva in self._reservas:
            if (reserva.habitacion.numero == habitacion.numero
                    and reserva.estado in ("Confirmada", "En curso")
                    and provisional.se_solapa_con(reserva)):
                return False
        return True

    def registrar_reserva(self, id_reserva, id_cliente, numero_habitacion,
                          fecha_ingreso, noches):
        """Equivalente al SP_RegistrarMatricula: valida y devuelve mensaje."""
        cliente = self.buscar_cliente(id_cliente)
        habitacion = self.buscar_habitacion(numero_habitacion)
        if cliente is None or habitacion is None:
            return ("Error: el cliente o la habitación no existen "
                    "en el sistema.")
        if not self.verificar_disponibilidad(habitacion, fecha_ingreso, noches):
            return ("Error: la habitación no está disponible en las "
                    "fechas solicitadas.")
        reserva = Reserva(id_reserva, cliente, habitacion,
                          fecha_ingreso, noches)
        self._reservas.append(reserva)
        evento = self._auditoria.registrar("Registro", id_reserva,
                                           f"Hab {numero_habitacion}")
        if self._repositorio is not None:      # persistencia opcional
            self._repositorio.guardar_reserva(reserva)
            self._repositorio.guardar_evento(evento)
        return f"Éxito: reserva {id_reserva} registrada correctamente."

    def cancelar_reserva(self, id_reserva):
        for reserva in self._reservas:
            if reserva.id_reserva == id_reserva:
                mensaje = reserva.cancelar()
                if mensaje.startswith("Éxito"):
                    evento = self._auditoria.registrar("Cancelación",
                                                       id_reserva)
                    if self._repositorio is not None:
                        self._repositorio.guardar_reserva(reserva)
                        self._repositorio.guardar_evento(evento)
                return mensaje
        return f"Error: la reserva {id_reserva} no existe en el sistema."

    def iterar_reservas(self):
        """Generador: entrega las reservas una a una (como un cursor)."""
        for reserva in self._reservas:
            yield reserva

    def actualizar_estados(self, fecha_actual):
        """Recorre fila por fila y persiste los cambios de estado."""
        for reserva in self.iterar_reservas():
            anterior = reserva.estado
            reserva.actualizar_estado(fecha_actual)
            if reserva.estado != anterior and self._repositorio is not None:
                self._repositorio.guardar_reserva(reserva)

    def listar_reservas(self):
        if not self._reservas:
            return "No hay reservas registradas."
        return "\n".join(str(reserva) for reserva in self._reservas)

    def iterar_eventos(self):
        """Generador: entrega los eventos de auditoría uno a uno."""
        yield from self._auditoria

    def mostrar_auditoria(self):
        return str(self._auditoria)


def cargar_datos_iniciales(gestor):
    """Carga inicial de clientes, habitaciones y una reserva.
    Se ejecuta únicamente cuando la base de datos está vacía."""
    gestor.registrar_cliente(Cliente(1, "María Fernanda", "Gómez Ruiz",
                                     "1020304050"))
    gestor.registrar_cliente(Cliente(2, "Carlos Andrés", "Restrepo León",
                                     "5140302010"))
    gestor.registrar_habitacion(Habitacion(101, "Sencilla", 120000, 2))
    gestor.registrar_habitacion(Habitacion(102, "Doble", 180000, 4))
    gestor.registrar_habitacion(Habitacion(201, "Suite", 350000, 6))
    gestor.registrar_reserva(1000, 1, 101, date(2026, 11, 8), 5)


def menu():
    print("\n===== SISTEMA DE RESERVAS - HOTEL UMB =====")
    print("1) Registrar cliente")
    print("2) Registrar reserva")
    print("3) Consultar disponibilidad")
    print("4) Listar reservas")
    print("5) Cancelar reserva")
    print("6) Ver auditoría")
    print("0) Salir")


def main():
    """Punto de entrada: conecta la base de datos y levanta el menú."""
    gestor = GestorReservas(RepositorioSQLite(NOMBRE_BD))
    if not gestor.habitaciones:          # base de datos vacía (primer uso)
        cargar_datos_iniciales(gestor)
        print("Carga inicial de datos de ejemplo completada.")
    print(f"Base de datos lista ({NOMBRE_BD}): "
          f"{len(gestor.reservas)} reservas recuperadas.")
    while True:
        menu()
        opcion = input("Seleccione una opción: ").strip()
        if opcion == "0":
            print("Sesión finalizada. ¡Gracias por usar el sistema!")
            break
        elif opcion == "1":
            try:
                id_cliente = int(input("ID del cliente: "))
                nombres = input("Nombres: ").strip()
                apellidos = input("Apellidos: ").strip()
                documento = input("Documento: ").strip()
                if not (nombres and apellidos and documento):
                    raise ValueError("nombres, apellidos y documento son "
                                      "obligatorios")
                if gestor.buscar_cliente(id_cliente) is not None:
                    print(f"Error: ya existe un cliente con el ID "
                          f"{id_cliente} "
                          f"({gestor.buscar_cliente(id_cliente).nombre_completo}).")
                else:
                    gestor.registrar_cliente(Cliente(
                        id_cliente, nombres, apellidos, documento))
                    print(f"Éxito: cliente {id_cliente} "
                          f"({apellidos.upper()}, {nombres}) registrado.")
            except ValueError as error:
                print(f"Error de validación: {error}")
        elif opcion == "2":
            try:
                id_reserva = int(input("ID de la reserva: "))
                id_cliente = int(input("ID del cliente: "))
                numero_hab = int(input("Número de habitación: "))
                fecha_texto = input("Fecha de ingreso (AAAA-MM-DD): ")
                noches = int(input("Número de noches: "))
                reserva = Reserva.crear_por_texto(
                    id_reserva, gestor.buscar_cliente(id_cliente),
                    gestor.buscar_habitacion(numero_hab), fecha_texto, noches)
                mensaje = gestor.registrar_reserva(
                    id_reserva, id_cliente, numero_hab,
                    reserva.fecha_ingreso, noches)
                print(mensaje)
            except ValueError as error:
                print(f"Error de validación: {error}")
        elif opcion == "3":
            numero_hab = int(input("Número de habitación: "))
            fecha_texto = input("Fecha de ingreso (AAAA-MM-DD): ")
            noches = int(input("Número de noches: "))
            habitacion = gestor.buscar_habitacion(numero_hab)
            if habitacion is None:
                print("Error: la habitación no existe en el sistema.")
            elif not Reserva.es_fecha_valida(fecha_texto):
                print("Error: fecha inválida, use el formato AAAA-MM-DD.")
            else:
                fecha = datetime.strptime(fecha_texto, "%Y-%m-%d").date()
                disponible = gestor.verificar_disponibilidad(
                    habitacion, fecha, noches)
                print(f"Disponibilidad habitación {numero_hab}: "
                      f"{'DISPONIBLE' if disponible else 'NO DISPONIBLE'}")
        elif opcion == "4":
            print(gestor.listar_reservas())
        elif opcion == "5":
            id_reserva = int(input("ID de la reserva a cancelar: "))
            print(gestor.cancelar_reserva(id_reserva))
        elif opcion == "6":
            print(gestor.mostrar_auditoria())
        else:
            print("Opción no válida, intente de nuevo.")


if __name__ == "__main__":
    main()
