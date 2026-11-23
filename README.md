# Software FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto del curso **Programación (213023)** - UNAD, Fase 4 (Manejo de excepciones en POO).

Sistema orientado a objetos en Python 3.10+ **sin base de datos**: los datos viven en listas
en memoria y solo se usa un archivo para el registro de eventos y errores (`eventos.log`).

## Estructura
| Archivo | Responsabilidad |
|---|---|
| `main.py` | Simulación de 22 operaciones (válidas e inválidas) |
| `excepciones.py` | Jerarquía de excepciones personalizadas |
| `entidades.py` | `EntidadBase` (abstracta) y `Cliente` |
| `servicios.py` | `Servicio` (abstracta), `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada` |
| `reserva.py` | `Reserva` y `EstadoReserva` |
| `gestor.py` | `GestorSoftwareFJ`: listas internas y ejecución protegida |
| `logger_config.py` | Configuración del log |

## Ejecución
```bash
python main.py
```
No requiere librerías externas. Genera `eventos.log` con todos los eventos y errores.

## Conceptos aplicados
- **Abstracción:** `EntidadBase` y `Servicio` (clases abstractas con `ABC`).
- **Herencia y polimorfismo:** tres servicios que sobrescriben `calcular_costo_base`, `validar_parametros` y `describir`.
- **Encapsulación:** atributos privados y propiedades con validación en `Cliente`.
- **Sobrecarga (simulada):** `calcular_costo` con parámetros opcionales y variantes `con_impuesto` / `con_descuento`.
- **Excepciones:** personalizadas, `try/except`, `try/except/else`, `try/except/finally` y encadenamiento con `raise ... from`.
