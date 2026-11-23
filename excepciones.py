"""
excepciones.py
==============
Jerarquía de excepciones personalizadas del sistema Software FJ.

Se define una excepción base (SoftwareFJError) de la que heredan todas las
demás. Así, en cualquier parte del programa se puede capturar TODO error
propio del dominio con un único ``except SoftwareFJError`` y distinguir los
casos específicos con excepciones más concretas.
"""


class SoftwareFJError(Exception):
    """Excepción base de todo el sistema Software FJ."""

    # Código corto que identifica la categoría del error en los logs.
    codigo = "FJ-000"

    def __init__(self, mensaje: str = "Error general en Software FJ") -> None:
        # Se guarda el mensaje para poder mostrarlo o registrarlo después.
        self.mensaje = mensaje
        # Se delega en Exception para conservar el comportamiento estándar.
        super().__init__(mensaje)

    def __str__(self) -> str:
        # Formato uniforme: [CÓDIGO] mensaje
        return f"[{self.codigo}] {self.mensaje}"


class ClienteInvalidoError(SoftwareFJError):
    """Datos personales inválidos o cliente duplicado."""

    codigo = "FJ-101"


class ServicioInvalidoError(SoftwareFJError):
    """Parámetros inválidos al crear o usar un servicio."""

    codigo = "FJ-201"


class ServicioNoDisponibleError(SoftwareFJError):
    """El servicio existe pero no está disponible para reservar."""

    codigo = "FJ-202"


class ParametroFaltanteError(SoftwareFJError):
    """Falta un parámetro obligatorio para completar una operación."""

    codigo = "FJ-301"


class ReservaInvalidaError(SoftwareFJError):
    """La reserva no pudo crearse o procesarse correctamente."""

    codigo = "FJ-401"


class OperacionNoPermitidaError(SoftwareFJError):
    """Operación incompatible con el estado actual de la reserva."""

    codigo = "FJ-402"


class CalculoInconsistenteError(SoftwareFJError):
    """El cálculo de costos produjo un resultado inconsistente."""

    codigo = "FJ-501"
