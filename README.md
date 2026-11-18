TALLER DE PROGRAMACION ORIENTADA A OBJETOS - SISTEMA DE RESERVAS
Leonardo Alexander Villalobos Patino
Ingenieria de Software - Universidad Manuela Beltran


CONTENIDO DEL PAQUETE
---------------------
1) sistema_reservas.py     Modelo POO y programa de consola
                           (menu de texto con persistencia SQLite).
2) app_reservas.py         APLICACION DE ESCRITORIO con ventana
                           y botones (tkinter): reutiliza las mismas
                           clases del modelo sin duplicar logica.
3) pruebas_actividades.py  Pruebas de las Actividades 1 a 6 del
                           taller (salidas en memoria y con BD).
4) README.txt              Este archivo.

REQUISITOS
----------
- Python 3.8 o superior.
- No se necesitan librerias externas: tkinter, sqlite3, datetime
  y contextlib vienen incluidos en la biblioteca estandar de
  Python (tkinter viene con el instalador oficial de Python
  en Windows y macOS; en Linux: sudo apt install python3-tk).

COMO EJECUTAR LA APLICACION (ventana)
-------------------------------------
1) Abra una terminal en la carpeta donde quedo este archivo.
2) Ejecute:      python app_reservas.py
   (en algunas instalaciones:  python3 app_reservas.py)
3) La primera ejecucion crea reservas.db y siembra los datos
   de ejemplo del taller; despues abre la ventana principal.

USO DE LA VENTANA
-----------------
- La tabla central lista las reservas (ID, cliente, habitacion,
  fechas, noches, costo con descuento y estado, con colores).
- Botones del panel izquierdo:
  * Registrar cliente       ID, nombres, apellidos y documento;
                           el cliente queda guardado en la base
                           de datos y aparece en la lista
                           desplegable de "Registrar reserva";
                           un ID repetido es rechazado.
  * Registrar reserva       abre un dialogo con listas
                           desplegables de clientes y
                           habitaciones; valida fechas y
                           solapamientos antes de guardar.
  * Consultar disponibilidad habitacion + fechas -> mensaje.
  * Cancelar reserva       seleccione la fila y pulse el boton
                           (pide confirmacion).
  * Actualizar estados     recalcula En curso / Finalizada con
                           la fecha del equipo y persiste el
                           cambio.
  * Ver auditoria          ventana con el historico completo.
- Doble clic sobre una fila muestra el detalle de la reserva
  (tarifa por noche, desglose) en la barra inferior.
- Todo queda guardado al instante en la base de datos: al
  cerrar y volver a abrir la aplicacion, la informacion sigue.
- "Reiniciar base de datos" borra reservas.db y vuelve a los
  datos de ejemplo (pide confirmacion).

COMO EJECUTAR EL PROGRAMA DE CONSOLA
-------------------------------------
Ejecute:      python sistema_reservas.py
Mismo modelo y misma base de datos que la aplicacion; util para
demostrar el taller en consola o revisarlo rapido. El menu ofrece
la opcion 1) Registrar cliente (ID, nombres, apellidos y documento)
y las demas operaciones sobre reservas.

COMO EJECUTAR LAS PRUEBAS DEL TALLER
------------------------------------
Ejecute:      python pruebas_actividades.py
Reproduce las salidas de las Actividades 1 a 6 (usa una base de
datos temporal prueba_persistencia.db que se elimina al final).

BASE DE DATOS
-------------
- Archivo: reservas.db (se crea junto a los scripts en la
  primera ejecucion; formato SQLite 3).
- Tablas: CLIENTES, HABITACIONES, RESERVAS y AUDITORIA.
- Para empezar de cero basta con borrar reservas.db (o usar el
  boton Reiniciar base de datos): el programa lo recrea y
  vuelve a sembrar los datos de ejemplo.

ESTRUCTURA DE CLASES (resumen)
------------------------------
Cliente             Huesped: atributos privados + @property.
Habitacion          Recurso reservable: setter con validacion.
Reserva             Logica de negocio: descuentos IF/ELIF,
                    solapamiento de fechas, estados, __str__.
AuditoriaReservas   Registro automatico de operaciones.
RepositorioSQLite   Persistencia: CREATE TABLE, INSERT OR
                    REPLACE, SELECT y reconstruccion de objetos.
GestorReservas      Orquestador: recibe el repositorio por
                    inyeccion de dependencias; sin el funciona
                    en memoria pura.
AppReservas         (app_reservas.py) interfaz grafica tkinter
                    que consume el gestor sin tocar la logica.
