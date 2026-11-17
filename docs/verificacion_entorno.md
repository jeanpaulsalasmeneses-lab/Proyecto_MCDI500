# Verificación de reproducibilidad en un segundo equipo

La rúbrica de la Sumativa 1 (criterio 5) pide **comprobar en un segundo equipo** que otro integrante clone el repositorio, reconstruya el entorno desde `requirements.txt` y ejecute ambos notebooks. Este archivo registra cada comprobación. **Cada integrante que la haga agrega su fila y la sube en su propio commit.**

## Registro de ejecuciones

| Fecha | Integrante | Sistema | Python | Commit verificado | F1 | F2 | Dependencias | SHA-256 de F2 | Observaciones |
|---|---|---|---|---|---|---|---|---|---|
| 2026-11-08 | Pavel Chávez | Linux (Fedora 44) | 3.13.12 | `a1cfb26` y siguientes | OK, ejecución 1→n | OK, ejecución 1→n | 106 de 106 (pywinpty se omite en Linux) | 7 de 7 coinciden | Clon limpio, sin los ZIP de `data/raw/`. Además se reconstruyeron los consolidados desde los 33 ZIP del CEN: contenido idéntico (`docs/fuente_dataset.md`). |
| 2026-11-09 | Javier Huamani Barrera | Windows (x64) | 3.12.8 | `7e20d27` y dev-javier | OK, ejecución 1→n | OK, ejecución 1→n | 107 de 107 (incluye pywinpty y nbstripout) | 7 de 7 coinciden | Verificación del ecosistema completo (Guía Parte V) en Windows con .venv. Dependencias y kernel validados. |

## Procedimiento (Windows, PowerShell)

Hacerlo en una carpeta **nueva**, no en la copia de trabajo habitual:

```powershell
git clone https://github.com/jeanpaulsalasmeneses-lab/Proyecto_MCDI500.git verificacion_mcdi500
cd verificacion_mcdi500
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

1. Abrir la carpeta en VS Code y seleccionar el kernel `.venv`.
2. Abrir `F1/F1_Definición.ipynb` y usar **Restart Kernel and Run All Cells**. Revisar que:
   - la celda §8.1.1 diga «9 de 9 coinciden» (todas las dependencias declaradas en `requirements.txt`);
   - el notebook termine sin errores, con la numeración de ejecución continua.
3. Repetir con `F2/F2_Exploracion_y_Preprocesamiento.ipynb`. La celda §6.15.5 debe decir «Las huellas SHA-256 coinciden».
4. En una terminal, comprobar que los datos procesados quedaron idénticos:

   ```powershell
   git status --short data/
   ```

   Solo debería aparecer `data/processed/f2/manifest_f2.json`, que cambia por la fecha de exportación. Si aparece un CSV, avisar en el grupo.
5. Completar la fila en la tabla de arriba y subirla:

   ```powershell
   git checkout -b docs/verificacion-windows
   git add docs/verificacion_entorno.md
   git commit -m "docs: verificación de reproducibilidad en Windows"
   git push -u origin docs/verificacion-windows
   ```

   Después, abrir el pull request en GitHub. No hacer commit de los notebooks reejecutados: la evidencia es la fila de la tabla.

---

## Registro de ejecuciones — Fase 3 (Sumativa 2)

| Fecha | Integrante | Sistema | Python | Commit verificado | Pruebas unitarias | Núcleo F3 | Dependencias | Observaciones |
|---|---|---|---|---|---|---|---|---|
| 2026-11-16 | Javier Huamani Barrera | Windows 11 (x64) | 3.12.8 | `f3-javier` | 35 de 35 OK | OK (`ejecutar_f3.py`) | 9 de 9 (`requirements.txt`) | Verificación independiente del núcleo algorítmico, POO y pruebas automatizadas en Windows 11 con .venv. |

### Procedimiento de verificación (Windows, PowerShell) — Fase 3

Para comprobar de forma independiente la Fase 3 en Windows:

1. Activar el entorno virtual `.venv` y asegurar las 9 dependencias fijas:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Ejecutar la suite de 35 pruebas unitarias automatizadas (POO, transformadores y excepciones):
   ```bash
   python -m unittest discover tests
   ```
   *Criterio de éxito:* Deben aprobarse las 35 pruebas unitarias sin fallos (`Ran 35 tests ... OK`).

3. Ejecutar el script de verificación del núcleo analítico sin notebook:
   ```bash
   python F3/ejecutar_f3.py
   ```
   *Criterio de éxito:* Debe confirmar la reproducibilidad funcional (`[OK] Reproducibilidad funcional del núcleo verificada`), reconstruyendo las 1.915 asociaciones, 15 comunas y los 954 intervalos temporales elegibles.