"""
logger_config.py
================
Configuración centralizada del registro de eventos y errores.

Toda la información operativa se escribe en ``eventos.log`` (el único uso de
archivos permitido por el enunciado). No se emplea ninguna base de datos.
"""
import logging
from pathlib import Path

# Ruta del archivo de logs: junto a este módulo, sin depender del directorio
# desde el cual se ejecute el programa.
RUTA_LOG = Path(__file__).resolve().parent / "eventos.log"

# Nombre del logger principal compartido por todos los módulos.
NOMBRE_LOGGER = "software_fj"


def configurar_logger(reiniciar: bool = False) -> logging.Logger:
    """Crea (una sola vez) y devuelve el logger principal del sistema.

    :param reiniciar: si es True, vacía el archivo de log antes de empezar
                      (útil para que cada simulación deje un log limpio).
    """
    logger = logging.getLogger(NOMBRE_LOGGER)
    logger.setLevel(logging.DEBUG)

    # Evita duplicar manejadores si la función se llama varias veces.
    if logger.handlers:
        return logger

    # 'w' sobrescribe el archivo; 'a' agrega al final.
    modo = "w" if reiniciar else "a"
    manejador = logging.FileHandler(RUTA_LOG, mode=modo, encoding="utf-8")
    formato = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(module)-12s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    manejador.setFormatter(formato)
    logger.addHandler(manejador)

    # No propagar al logger raíz para no imprimir mensajes duplicados.
    logger.propagate = False
    return logger


def obtener_logger() -> logging.Logger:
    """Devuelve el logger principal (lo configura si aún no existe)."""
    return configurar_logger()
