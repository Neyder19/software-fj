"""
reserva.py
==========
Clase Reserva: integra cliente, servicio, duración y estado.

Demuestra los bloques try/except, try/except/else, try/except/finally y el
encadenamiento de excepciones (``raise ... from ...``).
"""
from __future__ import annotations

from enum import Enum
from itertools import count

from entidades import Cliente, EntidadBase
from excepciones import (CalculoInconsistenteError, OperacionNoPermitidaError,
                         ParametroFaltanteError, ReservaInvalidaError,
                         ServicioInvalidoError, ServicioNoDisponibleError)
from logger_config import obtener_logger
from servicios import IVA, Servicio

logger = obtener_logger()


class EstadoReserva(Enum):
    """Ciclo de vida de una reserva."""

    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    CANCELADA = "Cancelada"
    FALLIDA = "Fallida"


class Reserva(EntidadBase):
    """Reserva de un servicio por parte de un cliente."""

    _contador = count(1)

    def __init__(self, cliente: Cliente, servicio: Servicio, duracion: float,
                 **parametros) -> None:
        # Validación de tipos: evita reservas con objetos inválidos.
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError(
                f"Cliente inválido: se recibió {type(cliente).__name__}.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError(
                f"Servicio inválido: se recibió {type(servicio).__name__}.")
        super().__init__(f"RES-{next(Reserva._contador):03d}")
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._parametros = parametros      # asistentes, cantidad, nivel...
        self._estado = EstadoReserva.PENDIENTE
        self._costo_total: float | None = None
        logger.info("Reserva %s creada (cliente=%s, servicio=%s)",
                    self.id, cliente.id, servicio.id)

    # ---------------- Propiedades de solo lectura ----------------
    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def duracion(self) -> float:
        return self._duracion

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def costo_total(self) -> float | None:
        return self._costo_total

    # ---------------- Operaciones del ciclo de vida ----------------
    def confirmar(self) -> None:
        """Confirma la reserva (solo si está pendiente y ya fue costeada)."""
        if self._estado is not EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar {self.id}: estado "
                f"{self._estado.value}.")
        if self._costo_total is None:
            raise OperacionNoPermitidaError(
                f"{self.id} no tiene costo calculado; use procesar().")
        self._estado = EstadoReserva.CONFIRMADA
        logger.info("Reserva %s CONFIRMADA por $%s", self.id,
                    f"{self._costo_total:,.2f}")

    def cancelar(self, motivo: str = "Sin motivo") -> None:
        """Cancela la reserva si aún no está cancelada ni fallida."""
        if self._estado in (EstadoReserva.CANCELADA, EstadoReserva.FALLIDA):
            raise OperacionNoPermitidaError(
                f"No se puede cancelar {self.id}: estado "
                f"{self._estado.value}.")
        self._estado = EstadoReserva.CANCELADA
        logger.info("Reserva %s CANCELADA. Motivo: %s", self.id, motivo)

    def procesar(self, impuesto: float = IVA, descuento: float = 0.0) -> float:
        """Valida, calcula el costo y confirma la reserva.

        Usa try / except / else / finally y encadena la causa original:
        - try:     intenta validar y calcular.
        - except:  traduce errores de bajo nivel a ReservaInvalidaError
                   conservando la causa con ``from``.
        - else:    se ejecuta SOLO si no hubo error -> confirma.
        - finally: se ejecuta SIEMPRE -> deja constancia en el log.
        """
        try:
            self._servicio.verificar_disponibilidad()
            costo = self._servicio.calcular_costo(
                self._duracion, impuesto=impuesto, descuento=descuento,
                **self._parametros)
        except (ServicioNoDisponibleError, ServicioInvalidoError,
                ParametroFaltanteError, CalculoInconsistenteError) as causa:
            self._estado = EstadoReserva.FALLIDA
            # Encadenamiento: la causa original queda en __cause__.
            raise ReservaInvalidaError(
                f"No se pudo procesar {self.id}: {causa.mensaje}") from causa
        else:
            self._costo_total = costo
            self.confirmar()
            return costo
        finally:
            logger.debug("Fin de procesar(%s). Estado actual: %s",
                         self.id, self._estado.value)

    def describir(self) -> str:
        costo = (f"${self._costo_total:,.2f}"
                 if self._costo_total is not None else "sin calcular")
        return (f"Reserva {self.id} | {self._cliente.nombre} -> "
                f"{self._servicio.nombre} | {self._duracion} h | "
                f"{self._estado.value} | {costo}")
