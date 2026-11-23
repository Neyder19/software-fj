"""
main.py
=======
Punto de entrada: simula 20 operaciones (válidas e inválidas) de Software FJ.

Ejecución:  python main.py
Resultado:  salida en consola + archivo eventos.log con el detalle.
"""
from logger_config import configurar_logger

# Se reinicia el log para que cada ejecución deje evidencia limpia.
logger = configurar_logger(reiniciar=True)

from entidades import Cliente  # noqa: E402  (después de configurar el log)
from gestor import GestorSoftwareFJ  # noqa: E402
from servicios import (AlquilerEquipo, AsesoriaEspecializada,  # noqa: E402
                       ReservaSala)


def titulo(n: int, texto: str) -> str:
    """Imprime el encabezado de cada operación y lo devuelve."""
    print(f"\n[{n:02d}] {texto}")
    return f"Operación {n:02d}: {texto}"


def main() -> None:
    g = GestorSoftwareFJ()
    logger.info("===== INICIO DE LA SIMULACIÓN SOFTWARE FJ =====")
    print("=" * 70)
    print(" SOFTWARE FJ - Gestión de Clientes, Servicios y Reservas")
    print("=" * 70)

    # ---------------- CLIENTES ----------------
    t = titulo(1, "Registrar cliente VÁLIDO (Ana Torres)")
    ana = g.ejecutar(t, g.registrar_cliente, nombre="Ana Torres",
                     documento="1012345678", email="ana@correo.com",
                     telefono="3101234567")

    t = titulo(2, "Registrar cliente VÁLIDO (Luis Pérez)")
    luis = g.ejecutar(t, g.registrar_cliente, nombre="Luis Pérez",
                      documento="80123456", email="luis.perez@mail.co",
                      telefono="3209876543")

    t = titulo(3, "Cliente INVÁLIDO: correo sin dominio")
    g.ejecutar(t, g.registrar_cliente, nombre="Carlos Ruiz",
               documento="1098765432", email="carlos@", telefono="3001112233")

    t = titulo(4, "Cliente INVÁLIDO: documento con letras")
    g.ejecutar(t, g.registrar_cliente, nombre="Marta Gil",
               documento="ABC123", email="marta@mail.com",
               telefono="3001112233")

    t = titulo(5, "Cliente DUPLICADO (mismo documento de Ana)")
    g.ejecutar(t, g.registrar_cliente, nombre="Ana Copia",
               documento="1012345678", email="copia@mail.com",
               telefono="3115556677")

    t = titulo(6, "Cliente con parámetro FALTANTE (sin teléfono)")
    g.ejecutar(t, g.registrar_cliente, nombre="Pedro Díaz",
               documento="70123456", email="pedro@mail.com", telefono=None)

    # ---------------- SERVICIOS ----------------
    t = titulo(7, "Crear 3 servicios VÁLIDOS (sala, equipo, asesoría)")
    sala = g.ejecutar(t, lambda: g.registrar_servicio(
        ReservaSala("Sala Innovación", 80000, capacidad=10)))
    equipo = g.ejecutar(t, lambda: g.registrar_servicio(
        AlquilerEquipo("Portátil Pro", 15000, stock=5)))
    asesoria = g.ejecutar(t, lambda: g.registrar_servicio(
        AsesoriaEspecializada("Asesoría Cloud", 120000, "Computación en la nube")))

    t = titulo(8, "Servicio INVÁLIDO: tarifa negativa")
    g.ejecutar(t, lambda: ReservaSala("Sala Fantasma", -500, capacidad=8))

    t = titulo(9, "Servicio INVÁLIDO: stock cero")
    g.ejecutar(t, lambda: AlquilerEquipo("Proyector", 20000, stock=0))

    # ---------------- RESERVAS ----------------
    t = titulo(10, "Reserva EXITOSA de sala (3 h, 6 asistentes, con IVA)")
    r1 = g.ejecutar(t, g.crear_reserva, ana, sala, 3, asistentes=6)
    g.ejecutar("Procesar " + t, r1.procesar)

    t = titulo(11, "Reserva EXITOSA de equipo (8 h, 2 unidades, 10% desc.)")
    r2 = g.ejecutar(t, g.crear_reserva, luis, equipo, 8, cantidad=2)
    g.ejecutar("Procesar " + t, r2.procesar, descuento=0.10)

    t = titulo(12, "Reserva EXITOSA de asesoría (2 h, nivel senior)")
    r3 = g.ejecutar(t, g.crear_reserva, ana, asesoria, 2, nivel="senior")
    g.ejecutar("Procesar " + t, r3.procesar)

    t = titulo(13, "Reserva FALLIDA: asistentes exceden capacidad (25 > 10)")
    r4 = g.ejecutar(t, g.crear_reserva, luis, sala, 2, asistentes=25)
    g.ejecutar("Procesar " + t, r4.procesar)

    t = titulo(14, "Reserva FALLIDA: asesoría sin 'nivel' (parámetro faltante)")
    r5 = g.ejecutar(t, g.crear_reserva, ana, asesoria, 1)
    g.ejecutar("Procesar " + t, r5.procesar)

    t = titulo(15, "Reserva FALLIDA: servicio NO disponible")
    equipo.disponible = False
    r6 = g.ejecutar(t, g.crear_reserva, luis, equipo, 4, cantidad=1)
    g.ejecutar("Procesar " + t, r6.procesar)
    equipo.disponible = True

    t = titulo(16, "Reserva FALLIDA: duración negativa (-3 h)")
    r7 = g.ejecutar(t, g.crear_reserva, ana, sala, -3, asistentes=4)
    g.ejecutar("Procesar " + t, r7.procesar)

    t = titulo(17, "Reserva FALLIDA: cliente None (objeto inválido)")
    g.ejecutar(t, g.crear_reserva, None, sala, 2, asistentes=3)

    t = titulo(18, "Cálculo inconsistente: descuento del 150%")
    r8 = g.ejecutar(t, g.crear_reserva, luis, sala, 2, asistentes=3)
    g.ejecutar("Procesar " + t, r8.procesar, descuento=1.5)

    # ---------------- CANCELACIONES / ESTADOS ----------------
    t = titulo(19, "Cancelar reserva CONFIRMADA (r1)")
    g.ejecutar(t, r1.cancelar, "El cliente reprogramó")

    t = titulo(20, "Cancelar de nuevo la misma reserva (operación no permitida)")
    g.ejecutar(t, r1.cancelar, "Segundo intento")

    t = titulo(21, "Confirmar una reserva ya confirmada (r2)")
    g.ejecutar(t, r2.confirmar)

    t = titulo(22, "Error INESPERADO (no del dominio): división por cero")
    g.ejecutar(t, lambda: 1 / 0)

    # ---------------- RESULTADOS ----------------
    print("\n" + "=" * 70)
    print(" LISTADO FINAL (polimorfismo: cada objeto se describe a sí mismo)")
    print("=" * 70)
    for entidad in (*g.clientes, *g.servicios, *g.reservas):
        print(" -", entidad)
    print("\n RESUMEN:", g.resumen())
    print(" El programa terminó SIN interrupciones. Revise 'eventos.log'.")
    logger.info("===== FIN DE LA SIMULACIÓN =====")


if __name__ == "__main__":
    main()
