"""
entidades.py
============
Clase abstracta base del sistema (EntidadBase) y la clase Cliente.

Principios aplicados:
- Abstracción: EntidadBase define el contrato común (id y descripción).
- Encapsulación: los datos del cliente son privados y se acceden por
  propiedades que validan cada cambio.
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from itertools import count

from excepciones import ClienteInvalidoError, ParametroFaltanteError
from logger_config import obtener_logger

logger = obtener_logger()


class EntidadBase(ABC):
    """Entidad general del sistema: todo objeto de negocio tiene un id."""

    def __init__(self, identificador: str) -> None:
        # Atributo protegido: solo lectura desde fuera (ver propiedad 'id').
        self._id = identificador

    @property
    def id(self) -> str:
        """Identificador único de la entidad (solo lectura)."""
        return self._id

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción legible. Cada subclase la implementa."""

    def __str__(self) -> str:
        # Polimorfismo: str(entidad) usa la descripción propia de cada clase.
        return self.describir()


class Cliente(EntidadBase):
    """Cliente de Software FJ con validaciones estrictas y datos privados."""

    # Contador compartido para generar ids consecutivos: CLI-001, CLI-002...
    _contador = count(1)

    # Expresiones regulares de validación.
    _RE_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü]+(?: [A-Za-zÁÉÍÓÚáéíóúÑñÜü]+)*$")
    _RE_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(?:\.[\w-]+)+$")
    _RE_DOCUMENTO = re.compile(r"^\d{6,12}$")
    _RE_TELEFONO = re.compile(r"^3\d{9}$")  # Celular colombiano: 10 dígitos

    def __init__(self, nombre: str, documento: str, email: str,
                 telefono: str) -> None:
        # Se validan los 4 datos ANTES de asignar un id: si algo falla, no se
        # consume un consecutivo ni queda un objeto a medio crear.
        nombre_ok = self._validar_nombre(nombre)
        documento_ok = self._validar_documento(documento)
        email_ok = self._validar_email(email)
        telefono_ok = self._validar_telefono(telefono)

        super().__init__(f"CLI-{next(Cliente._contador):03d}")
        # Atributos privados (encapsulación): prefijo doble guion bajo.
        self.__nombre = nombre_ok
        self.__documento = documento_ok
        self.__email = email_ok
        self.__telefono = telefono_ok
        logger.info("Cliente creado: %s (%s)", self.id, self.__nombre)

    # ---------------- Validadores (métodos estáticos) ----------------
    @staticmethod
    def _requerido(valor, campo: str) -> str:
        """Verifica que el valor exista y sea texto no vacío."""
        if valor is None:
            raise ParametroFaltanteError(f"El campo '{campo}' es obligatorio.")
        if not isinstance(valor, str):
            raise ClienteInvalidoError(
                f"El campo '{campo}' debe ser texto, se recibió "
                f"{type(valor).__name__}.")
        valor = valor.strip()
        if not valor:
            raise ParametroFaltanteError(f"El campo '{campo}' está vacío.")
        return valor

    @classmethod
    def _validar_nombre(cls, nombre) -> str:
        nombre = cls._requerido(nombre, "nombre")
        if len(nombre) < 3 or not cls._RE_NOMBRE.match(nombre):
            raise ClienteInvalidoError(
                f"Nombre inválido: '{nombre}' (solo letras, mínimo 3).")
        return nombre.title()

    @classmethod
    def _validar_documento(cls, documento) -> str:
        documento = cls._requerido(documento, "documento")
        if not cls._RE_DOCUMENTO.match(documento):
            raise ClienteInvalidoError(
                f"Documento inválido: '{documento}' (6 a 12 dígitos).")
        return documento

    @classmethod
    def _validar_email(cls, email) -> str:
        email = cls._requerido(email, "email")
        if not cls._RE_EMAIL.match(email):
            raise ClienteInvalidoError(f"Correo inválido: '{email}'.")
        return email.lower()

    @classmethod
    def _validar_telefono(cls, telefono) -> str:
        telefono = cls._requerido(telefono, "teléfono")
        if not cls._RE_TELEFONO.match(telefono):
            raise ClienteInvalidoError(
                f"Teléfono inválido: '{telefono}' (celular de 10 dígitos "
                "que inicia en 3).")
        return telefono

    # ---------------- Propiedades (acceso controlado) ----------------
    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def documento(self) -> str:
        return self.__documento

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, nuevo: str) -> None:
        # El setter reutiliza la validación: no se puede dejar un dato malo.
        self.__email = self._validar_email(nuevo)

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, nuevo: str) -> None:
        self.__telefono = self._validar_telefono(nuevo)

    def describir(self) -> str:
        # Se oculta parcialmente el documento (protección de datos).
        oculto = "*" * (len(self.__documento) - 3) + self.__documento[-3:]
        return (f"Cliente {self.id} | {self.__nombre} | Doc: {oculto} | "
                f"{self.__email}")
