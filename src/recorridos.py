"""
Recorridos de la jerarquía región -> comuna -> tipo de instalación (Fase 3).

Dos implementaciones equivalentes (recursiva e iterativa con pila) para
comparar su eficiencia. La jerarquía tiene profundidad fija, por lo que la
versión elegida es la iterativa (F3 §5.4).
"""


def construir_jerarquia(tabla):
    """
    Construye un árbol de diccionarios:

    Región -> Comuna -> Tipo -> Asociaciones.
    """

    arbol = {}

    for (
        region,
        comuna,
        instalacion,
        asociaciones
    ) in tabla[
        [
            "region_oficial",
            "codigo_comuna",
            "tipo_instalacion",
            "asociaciones"
        ]
    ].itertuples(index=False, name=None):

        if region not in arbol:
            arbol[region] = {}

        if comuna not in arbol[region]:
            arbol[region][comuna] = {}

        arbol[region][comuna][instalacion] = int(
            asociaciones
        )

    return arbol


def sumar_asociaciones_recursivo(nodo):
    """
    Recorre una estructura jerárquica.

    Caso base:
        Valor entero no negativo.

    Caso recursivo:
        Diccionario con elementos anidados.
    """

    # Caso base.

    if isinstance(nodo, int):

        if nodo < 0:
            raise ValueError(
                "No se permiten asociaciones negativas."
            )

        return nodo

    # Validar estructura.

    if not isinstance(nodo, dict):
        raise TypeError(
            "La estructura debe contener "
            "diccionarios o enteros."
        )

    # Caso recursivo.

    total = 0

    for elemento in nodo.values():

        total += sumar_asociaciones_recursivo(
            elemento
        )

    return total


def sumar_asociaciones_iterativo(arbol):
    """
    Recorre la estructura utilizando
    una pila y un ciclo while.
    """

    pila = [arbol]

    total = 0

    while pila:

        nodo = pila.pop()

        if isinstance(nodo, int):

            if nodo < 0:
                raise ValueError(
                    "No se permiten asociaciones negativas."
                )

            total += nodo

        elif isinstance(nodo, dict):

            pila.extend(
                nodo.values()
            )

        else:

            raise TypeError(
                "La estructura debe contener "
                "diccionarios o enteros."
            )

    return total
