# data/reference — Reglas de homologación CEN ↔ INE

Tablas **escritas a mano** y versionadas. F2 las **lee**: no están escritas en el código. Así cualquiera puede revisar las reglas sin ejecutar el notebook, y cada cambio queda en el historial de Git.

| Archivo | Lo lee | Qué contiene |
|---|---|---|
| `equivalencias_comunas.csv` | F2 §6.6.3 | Nombres de comuna del CEN que no calzan textualmente con el INE, con su clave y código oficial |
| `equivalencias_regiones.csv` | F2 §6.7 | Nombres de región abreviados del CEN y su nombre oficial INE (para la auditoría geográfica) |

## Regla de normalización (antes de comparar)

Las claves se generan con `normalizar_comuna()` (F2 §5) **sin modificar el dato original**:

1. Se limpian los espacios al inicio y al final, y los espacios repetidos.
2. Se quitan tildes y diacríticos (descomposición Unicode NFKD): `Viña del Mar` → `Vina del Mar`.
3. Todo pasa a mayúsculas: `VINA DEL MAR`.

Para las regiones (`crear_clave_region()`, F2 §6.7) además se reemplaza todo lo que no sea letra, número o espacio: `O'Higgins` → `O HIGGINS`.

## Orden de homologación

1. **Coincidencia exacta** de claves: 23.128 vínculos (99,33 %).
2. **Equivalencia** de `equivalencias_comunas.csv` + la región del INE coincide con la `Zona Afectada` del CEN: 128 vínculos.
3. **Equivalencia multirregión**: igual que la anterior, cuando `Zona Afectada` trae varias regiones separadas por `|`: 28 vínculos.

Si un nombre no calza por ninguna de estas tres vías, F2 lo deja en `data/processed/homologacion/denominaciones_no_homologadas.csv` y **no le asigna** comuna. Hoy ese archivo tiene 0 filas.

## Cómo agregar una equivalencia

1. Agregar una fila a `equivalencias_comunas.csv` con la clave del CEN **ya normalizada**, la clave del INE, el código comunal de 5 dígitos, el nombre oficial y el motivo.
2. Reejecutar F2 completo (*Restart & Run All*). La celda §6.6.3 verifica que la clave y el código existan en el INE y sean consistentes.
3. Anotar la decisión en `docs/decisiones.md` y subir el cambio por PR.
