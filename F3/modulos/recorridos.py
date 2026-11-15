
def construir_jerarquia(tabla):
    """Construye jerarquía región-comuna-instalación."""

    arbol = {}

    for region, comuna, instalacion, asociaciones in tabla[
        [
            "region_oficial",
            "codigo_comuna",
            "tipo_instalacion",
            "asociaciones"
        ]
    ].itertuples(index=False, name=None):

        arbol.setdefault(
            region, {}
        ).setdefault(
            comuna, {}
        )[instalacion] = int(asociaciones)

    return arbol


def sumar_asociaciones_recursivo(nodo):
    """Recorre recursivamente una jerarquía."""

    if isinstance(nodo, int):

        if nodo < 0:
            raise ValueError("Asociaciones negativas.")

        return nodo

    if not isinstance(nodo, dict):
        raise TypeError("Nodo inválido.")

    total = 0

    for elemento in nodo.values():

        total += sumar_asociaciones_recursivo(
            elemento
        )

    return total


def sumar_asociaciones_iterativo(arbol):
    """Recorre una jerarquía mediante una pila."""

    pila = [arbol]
    total = 0

    while pila:

        nodo = pila.pop()

        if isinstance(nodo, int):

            if nodo < 0:
                raise ValueError("Asociaciones negativas.")

            total += nodo

        elif isinstance(nodo, dict):

            pila.extend(nodo.values())

        else:

            raise TypeError("Nodo inválido.")

    return total
