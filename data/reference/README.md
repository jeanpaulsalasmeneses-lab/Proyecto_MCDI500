# data/reference — Reglas de homologación y equivalencias

Tablas **escritas a mano** y versionadas. F2 (comunas y regiones) y F4 (causas) las **leen**: no están escritas en el código. Así cualquiera puede revisar las reglas sin ejecutar el notebook, y cada cambio queda en el historial de Git.

| Archivo | Lo lee | Qué contiene |
|---|---|---|
| `equivalencias_comunas.csv` | F2 §6.6.3 | Nombres de comuna del CEN que no calzan textualmente con el INE, con su clave y código oficial |
| `equivalencias_regiones.csv` | F2 §6.7 | Nombres de región abreviados del CEN y su nombre oficial INE (para la auditoría geográfica) |
| `equivalencias_causas.csv` | F4 §4 (`src/causas.py`) | Descripciones causales del CEN con errores de escritura y su forma corregida (D-15). Se aplica solo en F4: F2 y F3 conservan el texto original del CEN |

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

## Cómo agregar una equivalencia de causa

1. Agregar una fila a `equivalencias_causas.csv` con la descripción **exacta** del CEN, la forma corregida y el motivo. Solo corresponde para errores de escritura: no se agrupan causas distintas.
2. Ejecutar `python -m unittest tests.test_causas`. Las pruebas fallan si la descripción no existe en los datos de F2, si se repite o si la corrección es a su vez una descripción a corregir.
3. Reejecutar F4 (*Restart & Run All*) y subir el cambio por PR.
