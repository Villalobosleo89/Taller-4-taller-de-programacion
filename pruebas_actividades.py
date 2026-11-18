# -*- coding: utf-8 -*-
"""Pruebas de las Actividades 1 a 6 para el documento del taller POO."""
import os
from datetime import date
from sistema_reservas import (Cliente, Habitacion, Reserva,
                              GestorReservas, AuditoriaReservas,
                              RepositorioSQLite)

print("========== ACTIVIDAD 1: CREACIÓN DE OBJETOS ==========")
cliente1 = Cliente(1, "María Fernanda", "Gómez Ruiz", "1020304050")
cliente2 = Cliente(2, "Carlos Andrés", "Restrepo León", "5140302010")
hab101 = Habitacion(101, "Sencilla", 120000, 2)
hab102 = Habitacion(102, "Doble", 180000, 4)
hab201 = Habitacion(201, "Suite", 350000, 6)

print(cliente1)
print(cliente2)
print(hab101)
print(hab102)
print(hab201)
print("Encapsulamiento -> nombres (solo lectura):", cliente1.nombres,
      "| tarifa hab 101:", hab101.tarifa_noche)
hab101.tarifa_noche = 130000          # modificación controlada por el setter
print("Setter con validación -> nueva tarifa hab 101:", hab101.tarifa_noche)
hab101.tarifa_noche = 120000          # se devuelve la tarifa original
cliente_prueba = Cliente(99, "Prueba", "Demostración", "0000000000")
cliente_prueba._nombres = "Otro"      # acceso directo al atributo privado
print("Acceso directo a _nombres:", cliente_prueba.nombres,
      "-> Python no bloquea el acceso (convención _ = uso interno)")

print()
print("========== ACTIVIDAD 2: REGISTRO Y DISPONIBILIDAD ==========")
gestor = GestorReservas()
gestor.registrar_cliente(cliente1)
gestor.registrar_cliente(cliente2)
gestor.registrar_habitacion(hab101)
gestor.registrar_habitacion(hab102)
gestor.registrar_habitacion(hab201)

# Prueba #1: cliente y habitación válidos
print(gestor.registrar_reserva(2001, 1, 102, date(2026, 11, 15), 7))

# Prueba #2: cliente que no existe (99) -> mensaje de error
print(gestor.registrar_reserva(2002, 99, 102, date(2026, 12, 1), 3))

# Prueba #3: fechas que se solapan en la habitación 102 -> error
print(gestor.registrar_reserva(2003, 2, 102, date(2026, 11, 18), 4))

# Prueba #4: otra habitación sí está disponible
print(gestor.registrar_reserva(2004, 2, 201, date(2026, 11, 18), 4))

print("\n--- Cálculo de tarifas con descuentos (IF/ELIF) ---")
reserva_corta = Reserva(3001, cliente1, hab101, date(2026, 12, 10), 3)
reserva_media = Reserva(3002, cliente2, hab102, date(2026, 12, 10), 7)
reserva_larga = Reserva(3003, cliente1, hab201, date(2026, 12, 10), 12)
for reserva in (reserva_corta, reserva_media, reserva_larga):
    print(f"Reserva {reserva.id_reserva} | {reserva.noches} noches | "
          f"Tarifa ${reserva.habitacion.tarifa_noche:,} | "
          f"Total: ${reserva.costo_total:,}")

print()
print("========== ACTIVIDAD 3: PROPIEDADES Y MÉTODOS ESPECIALES ==========")
print("nombre_completo (propiedad calculada):", cliente1.nombre_completo)
print("fecha_salida (propiedad calculada) de la reserva 2001:",
      f"{gestor.reservas[0].fecha_salida:%d/%m/%Y}")
print("es_fecha_valida (método estático) '2026-11-15' ->",
      Reserva.es_fecha_valida("2026-11-15"))
print("es_fecha_valida (método estático) '15-11-2026' ->",
      Reserva.es_fecha_valida("15-11-2026"))
r_texto = Reserva.crear_por_texto(3004, cliente2, hab101, "2026-12-20", 2)
print("crear_por_texto (método de clase):", r_texto)
print("\n__str__ de los objetos:")
for objeto in (cliente1, hab102, reserva_media):
    print(objeto)

print()
print("========== ACTIVIDAD 4: RECORRIDO FILA POR FILA (ITERADOR) ==========")
gestor2 = GestorReservas()
gestor2.registrar_cliente(cliente1)
gestor2.registrar_cliente(cliente2)
gestor2.registrar_habitacion(hab101)
gestor2.registrar_habitacion(hab102)
gestor2.registrar_habitacion(hab201)
gestor2.registrar_reserva(4001, 1, 101, date(2026, 10, 20), 5)   # ya pasó
gestor2.registrar_reserva(4002, 2, 102, date(2026, 11, 8), 6)    # en curso
gestor2.registrar_reserva(4003, 1, 201, date(2026, 11, 25), 4)   # futura
gestor2.registrar_reserva(4004, 2, 102, date(2026, 12, 5), 10)   # futura
gestor2.cancelar_reserva(4003)

print("--- Estado de las reservas ANTES del recorrido ---")
print(gestor2.listar_reservas())

fecha_actual = date(2026, 11, 12)
for reserva in gestor2.iterar_reservas():          # una a una, como un cursor
    reserva.actualizar_estado(fecha_actual)

print("\n--- Estado de las reservas DESPUÉS del recorrido ---")
print(gestor2.listar_reservas())

print()
print("========== ACTIVIDAD 5: VALIDACIÓN, EXCEPCIONES Y AUDITORÍA ==========")
print("--- Prueba del error (equivalente al trigger BEFORE INSERT) ---")
try:
    Reserva(5001, cliente1, hab101, date(2026, 11, 20), 45)
except ValueError as error:
    print(f"ValueError: {error}")

try:
    hab201.tarifa_noche = -5000
except ValueError as error:
    print(f"ValueError: {error}")

print("\n--- Prueba válida y revisión de auditoría ---")
gestor3 = GestorReservas()
gestor3.registrar_cliente(cliente1)
gestor3.registrar_cliente(cliente2)
gestor3.registrar_habitacion(hab101)
gestor3.registrar_habitacion(hab102)
gestor3.registrar_habitacion(hab201)
print(gestor3.registrar_reserva(6001, 1, 101, date(2026, 11, 20), 5))
print(gestor3.registrar_reserva(6002, 2, 102, date(2026, 11, 22), 6))
print(gestor3.cancelar_reserva(6001))
print(gestor3.registrar_reserva(6003, 2, 101, date(2026, 11, 20), 2))
print("\nRegistro de auditoría (equivalente al trigger AFTER INSERT):")
print(gestor3.mostrar_auditoria())

print()
print("========== ACTIVIDAD 6: PERSISTENCIA EN BASE DE DATOS ==========")
BD_PRUEBA = "prueba_persistencia.db"
if os.path.exists(BD_PRUEBA):
    os.remove(BD_PRUEBA)

print("--- Prueba #1: gestor con repositorio (guarda en SQLite) ---")
gestor_bd = GestorReservas(RepositorioSQLite(BD_PRUEBA))
gestor_bd.registrar_cliente(cliente1)
gestor_bd.registrar_habitacion(hab101)
print(gestor_bd.registrar_reserva(7001, 1, 101, date(2026, 12, 1), 6))
print(gestor_bd.cancelar_reserva(7001))

print()
print("--- Prueba #2: reconexión a la misma base de datos ---")
gestor_recargado = GestorReservas(RepositorioSQLite(BD_PRUEBA))
print("Reservas recuperadas de la base de datos:")
print(gestor_recargado.listar_reservas())
print("Auditoría recuperada de la base de datos:")
print(gestor_recargado.mostrar_auditoria())
os.remove(BD_PRUEBA)   # la base de datos de prueba se elimina al final
