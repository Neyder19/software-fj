"""
servicios.py
============
Clase abstracta Servicio y tres servicios especializados.

Principios aplicados:
- Herencia: Servicio -> ReservaSala, AlquilerEquipo, AsesoriaEspecializada.
- Polimorfismo: cada hija sobrescribe calcular_costo_base, describir y
  validar_parametros; el código cliente los usa sin conocer el tipo exacto.
- Sobrecarga: Python no tiene sobrecarga nativa; se simula con parámetros
  opcionales (impuesto, descuento) y variantes con nombre propio
  (calcular_costo_con_impuesto, calcular_costo_con_descuento).
"""
from __future__ import annotations

import math
from abc import abstractmethod
from itertools import count

from entidades import EntidadBase
from excepciones import (CalculoInconsistenteError, ParametroFaltanteError,
                         ServicioInvalidoError, ServicioNoDisponibleError)
from logger_config import obtener_logger

logger = obtener_logger()

IVA = 0.19  # Impuesto al valor agregado en Colombia


def _es_numero(valor) -> bool:
    """True si es int/float real (los booleanos NO cuentan como número)."""
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


class Servicio(EntidadBase):
    """Clase abstracta: define qué debe saber hacer cualquier servicio."""

    _contador = count(1)
    HORAS_MAXIMAS = 24

    def __init__(self, nombre: str, tarifa_hora: float,
                 disponible: bool = True) -> None:
        # Validaciones comunes a todos los servicios.
        if nombre is None or not isinstance(nombre, str) or not nombre.strip():
            raise ServicioInvalidoError("El servicio requiere un nombre.")
        if not _es_numero(tarifa_hora) or not math.isfinite(tarifa_hora) \
                or tarifa_hora <= 0:
            raise ServicioInvalidoError(
                f"Tarifa inválida: {tarifa_hora!r} (debe ser un número > 0).")
        super().__init__(f"SRV-{next(Servicio._contador):03d}")
        self._nombre = nombre.strip()
        self._tarifa_hora = float(tarifa_hora)
        self._disponible = bool(disponible)

    # ---------------- Propiedades ----------------
    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_hora(self) -> float:
        return self._tarifa_hora

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        self._disponible = bool(valor)
        logger.info("Servicio %s disponibilidad -> %s", self.id, self._disponible)

    # ---------------- Métodos abstractos (contrato) ----------------
    @abstractmethod
    def calcular_costo_base(self, horas: float, **parametros) -> float:
        """Costo sin impuestos ni descuentos. Cada servicio lo define."""

    @abstractmethod
    def validar_parametros(self, horas: float, **parametros) -> None:
        """Lanza excepción si los parámetros de la reserva no son válidos."""

    # (describir() sigue siendo abstracto, heredado de EntidadBase)

    # ---------------- Utilidades compartidas ----------------
    def verificar_disponibilidad(self) -> None:
        """Lanza ServicioNoDisponibleError si el servicio está inactivo."""
        if not self._disponible:
            raise ServicioNoDisponibleError(
                f"El servicio {self.id} '{self._nombre}' no está disponible.")

    def _validar_horas(self, horas, minimo: float = 0.5,
                       maximo: float | None = None) -> None:
        """Validación de duración reutilizada por las clases hijas."""
        maximo = maximo if maximo is not None else self.HORAS_MAXIMAS
        if horas is None:
            raise ParametroFaltanteError("La duración (horas) es obligatoria.")
        if not _es_numero(horas) or not math.isfinite(horas):
            raise ServicioInvalidoError(f"Duración inválida: {horas!r}.")
        if horas < minimo or horas > maximo:
            raise ServicioInvalidoError(
                f"Duración fuera de rango: {horas} h (permitido "
                f"{minimo}-{maximo} h).")

    # ---------------- Sobrecarga simulada del cálculo de costos ----------------
    def calcular_costo(self, horas: float, impuesto: float = 0.0,
                       descuento: float = 0.0, **parametros) -> float:
        """Variante general: costo base + descuento + impuesto opcionales.

        ``calcular_costo(2)``                       -> solo costo base
        ``calcular_costo(2, impuesto=0.19)``        -> con IVA
        ``calcular_costo(2, descuento=0.10)``       -> con descuento
        ``calcular_costo(2, 0.19, 0.10)``           -> ambos
        """
        for nombre, valor in (("impuesto", impuesto), ("descuento", descuento)):
            if not _es_numero(valor) or not 0 <= valor <= 1:
                raise CalculoInconsistenteError(
                    f"{nombre.capitalize()} inválido: {valor!r} "
                    "(debe estar entre 0 y 1).")
        self.validar_parametros(horas, **parametros)
        base = self.calcular_costo_base(horas, **parametros)
        total = base * (1 - descuento) * (1 + impuesto)
        # Verificación de consistencia del cálculo.
        if not math.isfinite(total) or total <= 0:
            raise CalculoInconsistenteError(
                f"Cálculo inconsistente: total={total!r} para {self.id}.")
        return round(total, 2)

    def calcular_costo_con_impuesto(self, horas: float, impuesto: float = IVA,
                                    **parametros) -> float:
        """Variante: solo impuesto (IVA por defecto)."""
        return self.calcular_costo(horas, impuesto=impuesto, **parametros)

    def calcular_costo_con_descuento(self, horas: float, descuento: float,
                                     **parametros) -> float:
        """Variante: solo descuento (sin impuesto)."""
        return self.calcular_costo(horas, descuento=descuento, **parametros)


class ReservaSala(Servicio):
    """Reserva de salas de reuniones o capacitación."""

    def __init__(self, nombre: str, tarifa_hora: float, capacidad: int,
                 disponible: bool = True) -> None:
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) \
                or capacidad <= 0:
            raise ServicioInvalidoError(
                f"Capacidad inválida: {capacidad!r} (entero > 0).")
        super().__init__(nombre, tarifa_hora, disponible)
        self._capacidad = capacidad

    @property
    def capacidad(self) -> int:
        return self._capacidad

    def validar_parametros(self, horas, asistentes=None, **_) -> None:
        self._validar_horas(horas, minimo=1, maximo=12)
        if asistentes is None:
            raise ParametroFaltanteError("Falta el número de 'asistentes'.")
        if not isinstance(asistentes, int) or isinstance(asistentes, bool) \
                or asistentes <= 0:
            raise ServicioInvalidoError(f"Asistentes inválidos: {asistentes!r}.")
        if asistentes > self._capacidad:
            raise ServicioInvalidoError(
                f"{asistentes} asistentes exceden la capacidad "
                f"({self._capacidad}) de '{self._nombre}'.")

    def calcular_costo_base(self, horas, asistentes=None, **_) -> float:
        # Tarifa plana por hora de uso de la sala.
        return self._tarifa_hora * horas

    def describir(self) -> str:
        return (f"Sala '{self._nombre}' [{self.id}] | capacidad "
                f"{self._capacidad} | ${self._tarifa_hora:,.0f}/h")


class AlquilerEquipo(Servicio):
    """Alquiler de equipos (portátiles, proyectores, etc.)."""

    SEGURO = 0.05  # 5 % de seguro sobre el valor del alquiler

    def __init__(self, nombre: str, tarifa_hora: float, stock: int,
                 disponible: bool = True) -> None:
        if not isinstance(stock, int) or isinstance(stock, bool) or stock <= 0:
            raise ServicioInvalidoError(f"Stock inválido: {stock!r} (entero > 0).")
        super().__init__(nombre, tarifa_hora, disponible)
        self._stock = stock

    @property
    def stock(self) -> int:
        return self._stock

    def validar_parametros(self, horas, cantidad=1, **_) -> None:
        self._validar_horas(horas, minimo=1, maximo=72)
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) \
                or cantidad <= 0:
            raise ServicioInvalidoError(f"Cantidad inválida: {cantidad!r}.")
        if cantidad > self._stock:
            raise ServicioInvalidoError(
                f"Solo hay {self._stock} unidades de '{self._nombre}'; "
                f"se pidieron {cantidad}.")

    def calcular_costo_base(self, horas, cantidad=1, **_) -> float:
        # Alquiler por unidades y horas, más el recargo de seguro.
        alquiler = self._tarifa_hora * horas * cantidad
        return alquiler * (1 + self.SEGURO)

    def describir(self) -> str:
        return (f"Equipo '{self._nombre}' [{self.id}] | stock {self._stock} | "
                f"${self._tarifa_hora:,.0f}/h (+5% seguro)")


class AsesoriaEspecializada(Servicio):
    """Asesoría con tarifa según el nivel del consultor."""

    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, nombre: str, tarifa_hora: float, especialidad: str,
                 disponible: bool = True) -> None:
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise ServicioInvalidoError("La asesoría requiere una especialidad.")
        super().__init__(nombre, tarifa_hora, disponible)
        self._especialidad = especialidad.strip()

    @property
    def especialidad(self) -> str:
        return self._especialidad

    def validar_parametros(self, horas, nivel=None, **_) -> None:
        self._validar_horas(horas, minimo=1, maximo=8)
        if nivel is None:
            raise ParametroFaltanteError("Falta el 'nivel' del consultor.")
        if nivel not in self.NIVELES:
            raise ServicioInvalidoError(
                f"Nivel '{nivel}' inválido. Opciones: "
                f"{', '.join(self.NIVELES)}.")

    def calcular_costo_base(self, horas, nivel="junior", **_) -> float:
        # El multiplicador de nivel encarece al consultor más experimentado.
        return self._tarifa_hora * horas * self.NIVELES[nivel]

    def describir(self) -> str:
        return (f"Asesoría '{self._nombre}' [{self.id}] | {self._especialidad} "
                f"| ${self._tarifa_hora:,.0f}/h x nivel")
