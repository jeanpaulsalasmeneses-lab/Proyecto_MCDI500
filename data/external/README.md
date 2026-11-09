# data/external — Datos de referencia externos (INE)

Archivos oficiales de terceros que el proyecto **no modifica**. A diferencia de `data/raw/`, esta carpeta sí se versiona, porque el archivo pesa poco (0,5 MB) y no cambia mes a mes.

## `ine_censo2024_poblacion_comunal.xlsx`

| Campo | Valor |
|---|---|
| Organismo | Instituto Nacional de Estadísticas (INE) |
| Publicación | Censo de Población y Vivienda 2024: *Población censada por sexo y edad en grupos quinquenales* |
| URL de descarga | https://censo2024.ine.gob.cl/wp-content/uploads/2025/03/D1_Poblacion-censada-por-sexo-y-edad-en-grupos-quinquenales.xlsx |
| Página de resultados | https://censo2024.ine.gob.cl/resultados/ |
| Nombre original | `D1_Poblacion-censada-por-sexo-y-edad-en-grupos-quinquenales.xlsx` (se renombró en el commit `b1ec1cb`) |
| Publicado por el INE | 2025-12-04 (`Last-Modified` del servidor) |
| Tamaño | 505.437 bytes |
| SHA-256 | `1f3a9c97a1b3defa47a2fc3b8495688c4e08f164063cab704e7a18c41239e009` |
| Hoja usada en F2 | «2»: población censada por sexo, según comuna (código región, región, código provincia, provincia, código comuna, comuna, población) |

## Cómo verificar o volver a descargar

```bash
curl -L -o data/external/ine_censo2024_poblacion_comunal.xlsx \
  "https://censo2024.ine.gob.cl/wp-content/uploads/2025/03/D1_Poblacion-censada-por-sexo-y-edad-en-grupos-quinquenales.xlsx"
sha256sum data/external/ine_censo2024_poblacion_comunal.xlsx   # Windows: certutil -hashfile <archivo> SHA256
```

Si el SHA-256 no coincide, el INE publicó una versión nueva. En ese caso hay que reejecutar F2, revisar el maestro territorial (F2 §6.5) y anotar el cambio en `docs/decisiones.md`.
