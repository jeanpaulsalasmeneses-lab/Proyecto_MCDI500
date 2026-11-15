"""
Medición reproducible de eficiencia (Fase 3): tiempo con timeit y memoria
con tracemalloc, ambos de la biblioteca estándar.
"""

import statistics
import timeit
import tracemalloc


def medir_tiempo(funcion, estructura, ejecuciones, repeticiones=7):
    """
    Mide el tiempo de ejecución mediante timeit.

    Retorna la mediana del tiempo por ejecución
    expresada en milisegundos.
    """

    # Ejecución inicial de preparación.

    funcion(estructura)

    mediciones = timeit.repeat(
        stmt=lambda: funcion(estructura),
        repeat=repeticiones,
        number=ejecuciones
    )

    tiempo_mediano = (
        statistics.median(mediciones)
        / ejecuciones
        * 1000
    )

    return tiempo_mediano


def medir_memoria(funcion, estructura):
    """
    Mide el pico de memoria asignada por Python
    durante la ejecución del algoritmo.

    No representa la memoria total del proceso.
    """

    picos = []

    for _ in range(5):

        tracemalloc.start()

        try:

            funcion(estructura)

            _, memoria_pico = (
                tracemalloc.get_traced_memory()
            )

        finally:

            tracemalloc.stop()

        picos.append(
            memoria_pico / 1024
        )

    return statistics.median(picos)


def construir_estructura_prueba(arbol, factor):
    """
    Construye una estructura de mayor carga.

    Reutiliza referencias de la jerarquía original,
    sin crear nuevos informes documentales.

    El objetivo es evaluar el recorrido algorítmico.
    """

    if factor < 1:
        raise ValueError(
            "El factor debe ser positivo."
        )

    return {
        f"replica_{i:03d}": arbol
        for i in range(factor)
    }
