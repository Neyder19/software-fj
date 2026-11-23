"""
gestor.py
=========
GestorSoftwareFJ: administra las listas internas de clientes, servicios y
reservas (sin base de datos) y garantiza que ningún error detenga el programa.
"""
from __future__ import annotations

from typing import Any, Callable

from entidades import Cliente
from excepciones import ClienteInvalidoError, SoftwareFJError
from logger_config import obtener_logger
from reserva import EstadoReserva, Reserva
from servicios import Servicio

logger = obtener_logger()


class GestorSoftwareFJ:
    """Coordina el sistema. Los datos viven solo en listas en memoria."""

    def __init__(self) -> None:
        self._clientes: list[Cliente] = []
        self._servicios: list[Servicio] = []
        self._reservas: list[Reserva] = []

    # ---------------- Registro de entidades ----------------
    def registrar_cliente(self, **datos) -> Cliente:
        """Crea un cliente y lo agrega a la lista (documento único)."""
        # Se verifica el duplicado ANTES de crear el objeto, así un cliente
        # rechazado no consume un consecutivo de id.
        documento = str(datos.get("documento") or "").strip()
        if documento and any(c.documento == documento for c in self._clientes):
            raise ClienteInvalidoError(
                f"Ya existe un cliente con documento {documento}.")
        cliente = Cliente(**datos)
        self._clientes.append(cliente)
        return cliente

    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        """Agrega un servicio (ya construido y validado) a la lista."""
        self._servicios.append(servicio)
        logger.info("Servicio registrado: %s", servicio.id)
        return servicio

    def crear_reserva(self, cliente: Cliente, servicio: Servicio,
                      duracion: float, **parametros) -> Reserva:
        """Crea una reserva pendiente y la guarda en la lista."""
        reserva = Reserva(cliente, servicio, duracion, **parametros)
        self._reservas.append(reserva)
        return reserva

    # ---------------- Ejecución protegida ----------------
    def ejecutar(self, titulo: str, funcion: Callable[..., Any],
                 *args, **kwargs) -> Any:
        """Ejecuta una operación sin que un error detenga el programa.

        - Errores del dominio (SoftwareFJError): se registran como ERROR.
        - Errores inesperados (Exception): se registran como CRITICAL.
        En ambos casos devuelve None y el sistema sigue activo.
        """
        try:
            resultado = funcion(*args, **kwargs)
        except SoftwareFJError as error:
            causa = f" | Causa: {error.__cause__!r}" if error.__cause__ else ""
            logger.error("%s -> %s%s", titulo, error, causa)
            print(f"   [X] ERROR CONTROLADO: {error}")
            return None
        except Exception as error:  # noqa: BLE001 - red de seguridad final
            logger.critical("%s -> Error inesperado %s: %s", titulo,
                            type(error).__name__, error, exc_info=True)
            print(f"   [!] ERROR INESPERADO ({type(error).__name__}): {error}")
            return None
        else:
            logger.info("%s -> OK", titulo)
            print(f"   [OK] {resultado if resultado is not None else 'Hecho'}")
            return resultado
        finally:
            logger.debug("Operación finalizada: %s", titulo)

    # ---------------- Reportes ----------------
    @property
    def clientes(self) -> list[Cliente]:
        return list(self._clientes)       # copia: protege la lista interna

    @property
    def servicios(self) -> list[Servicio]:
        return list(self._servicios)

    @property
    def reservas(self) -> list[Reserva]:
        return list(self._reservas)

    def resumen(self) -> str:
        confirmadas = [r for r in self._reservas
                       if r.estado is EstadoReserva.CONFIRMADA]
        ingresos = sum(r.costo_total or 0 for r in confirmadas)
        por_estado = {e.value: sum(1 for r in self._reservas if r.estado is e)
                      for e in EstadoReserva}
        return (f"Clientes: {len(self._clientes)} | Servicios: "
                f"{len(self._servicios)} | Reservas: {len(self._reservas)} "
                f"{por_estado} | Ingresos confirmados: ${ingresos:,.2f}")
