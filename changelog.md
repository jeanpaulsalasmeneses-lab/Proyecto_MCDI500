# Registro de cambios — Proyecto MCDI500

**Proyecto:** Exposición operacional documentada de las 15 comunas más pobladas de Chile a las fallas del Sistema Eléctrico Nacional (2024–2026).

**Asignatura:** Programación para la Ciencia de Datos.

**Programa:** Magíster en Ciencia de Datos e Inteligencia Artificial.

**Equipo:** Grupo 7.

**Propósito del documento:** Registrar las modificaciones, incorporaciones, verificaciones y mejoras realizadas durante el desarrollo del proyecto, facilitando su trazabilidad mediante Git y GitHub.

---

## Fase 4 — Comunicación de resultados

**Fecha de registro:** 21 de noviembre de 2026.

**Rama de desarrollo:** `F4-JPSM-nueva`.

**Commit de referencia inicial:** `bb70bb6`.

**Estado:** En desarrollo. Pendiente de integración al repositorio principal.

### 1. Componentes incorporados

Se desarrolló el notebook:

`F4/F4_Comunicacion_Resultados.ipynb`

Este componente permite recuperar los indicadores consolidados durante F3 y desarrollar las actividades de validación, visualización, interpretación y comunicación de resultados.

Se incorporaron procedimientos para:

- Verificar la disponibilidad del entorno y los componentes del proyecto.
- Recuperar el panel integrado de las 15 comunas.
- Comprobar la consistencia aritmética de los indicadores.
- Construir tablas analíticas a partir de los resultados de F3.
- Generar visualizaciones mediante Matplotlib.
- Interpretar los principales resultados y sus limitaciones.
- Ejecutar comprobaciones técnicas de reproducibilidad y trazabilidad.

La implementación mantiene separados los procedimientos de procesamiento algorítmico de F3 y las operaciones de comunicación desarrolladas en F4.

### 2. Tablas analíticas generadas

Se incorporaron tres archivos CSV en `F4/resultados/`:

| Archivo | Contenido |
|---|---|
| `F4_Tabla_401_Frecuencia_Comunal.csv` | Frecuencia documental normalizada de las 15 comunas. |
| `F4_Tabla_402_Recurrencia_Causal.csv` | Descripciones causales predominantes y participación porcentual. |
| `F4_Tabla_403_Duracion_Cobertura.csv` | Mediana, percentil 75 y cobertura temporal. |

Las tablas utilizan los indicadores del archivo:

`F3/resultados/F3_701_Panel_Integrado_Comunal.csv`

No se introdujeron modificaciones en los algoritmos originales de cálculo de F3.

### 3. Visualizaciones incorporadas

Se generaron tres figuras en `F4/figuras/`:

| Figura | Archivo |
|---|---|
| Figura 5.1. Frecuencia documental normalizada | `F4_Figura_501_Frecuencia_Comunal.png` |
| Figura 5.2. Recurrencia causal documental | `F4_Figura_502_Recurrencia_Causal.png` |
| Figura 5.3. Duración y cobertura temporal | `F4_Figura_503_Duracion_Cobertura.png` |

Cada visualización incorpora identificación de comunas, unidades, etiquetas, fuente y consideraciones metodológicas.

Se desarrollaron interpretaciones académicas basadas en los resultados obtenidos.

### 4. Verificaciones técnicas realizadas

Se incorporaron procedimientos de verificación estructural, ejecución de pruebas automatizadas, revisión de dependencias, auditoría de productos y trazabilidad mediante Git.

**Resultados principales:**

| Verificación | Resultado |
|---|---|
| Integridad del panel integrado | 15 comunas, sin duplicados |
| Consistencia de frecuencias normalizadas | 15 de 15 verificadas |
| Consistencia de indicadores de recurrencia y duración | Verificaciones satisfactorias |
| Pruebas automatizadas | 35 pruebas y 3 subpruebas aprobadas |
| Dependencias declaradas | 10 verificadas |
| Compatibilidad del entorno | `pip check` satisfactorio |
| Tablas consistentes con F3 | 3 de 3 |
| Figuras con encabezado PNG válido | 3 de 3 |

Se generaron evidencias técnicas en los siguientes archivos:

- `F4_901_Verificacion_Tecnica.json`
- `F4_902_Salida_Pruebas.txt`
- `F4_902_Pruebas_Automatizadas.json`
- `F4_903_Verificacion_Dependencias.json`
- `F4_904_Auditoria_Productos.json`
- `F4_905_Trazabilidad_Git.json`

Todos estos registros se almacenan en `F4/resultados/`.

### 5. Modificaciones en dependencias

**Archivo modificado:** `requirements.txt`.

Se incorporó la dependencia:

`pytest==9.2.0`

**Justificación:** Durante la primera verificación de pruebas automatizadas se identificó que `pytest` no estaba instalado en el entorno virtual.

Después de instalarlo, se ejecutó satisfactoriamente la batería de pruebas del repositorio.

La incorporación al archivo de dependencias facilita su instalación en futuras ejecuciones.

### 6. Actualización de documentación

**Archivo modificado:** `README.md`.

Se realizaron las siguientes actualizaciones:

- Incorporación del comando de ejecución de pruebas mediante `pytest`.
- Actualización de la cantidad de dependencias declaradas, de nueve a diez.
- Actualización del estado de F4 a «En desarrollo».
- Incorporación de instrucciones para ejecutar el notebook F4.
- Actualización del árbol de directorios para incluir los productos de F4.

Estas modificaciones buscan facilitar la comprensión del proyecto y su ejecución por parte de otros integrantes del equipo o evaluadores.

### 7. Auditoría de integridad y trazabilidad

Se verificó la correspondencia entre las tablas generadas durante F4 y los indicadores consolidados en F3.

Las tres tablas presentaron resultados consistentes con el panel integrado, dentro de las tolerancias numéricas establecidas.

Se comprobó también la existencia y estructura básica de las figuras PNG.

Adicionalmente, se calcularon huellas digitales SHA-256 para registrar la integridad de los productos analíticos.

**SHA-256 del panel integrado utilizado:**

`a58addc332a552aea0361a2a21cf9edbb32994275652cf217b02072f73fc8dcc`

### 8. Alcances y verificaciones pendientes

Las comprobaciones realizadas proporcionan evidencia satisfactoria respecto del funcionamiento de los componentes evaluados y la consistencia de los productos de F4.

No obstante, permanecen pendientes:

- La reproducción integral de F1 a F4 desde un entorno completamente nuevo.
- La revisión final del informe técnico y sus referencias.
- La preparación de la presentación audiovisual.
- La revisión de los archivos que serán incorporados al repositorio.
- El registro de los cambios mediante commits y su posterior integración a la rama principal.

La aprobación de las pruebas automatizadas no implica una cobertura completa de todas las funcionalidades del proyecto.

Asimismo, las verificaciones de integridad de archivos no reemplazan la validación metodológica de los resultados.

---

## Registro de integración

**Estado actual:** Modificaciones locales en la rama `F4-JPSM-nueva`.

**Commit de integración:** Pendiente.

**Pull Request:** Pendiente.

**Integración a `main`:** Pendiente.

Este apartado deberá actualizarse una vez que se realicen y verifiquen las operaciones correspondientes en GitHub.