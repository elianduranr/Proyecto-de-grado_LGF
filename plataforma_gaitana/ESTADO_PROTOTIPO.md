# Estado comprobado del prototipo

Actualización operativa: 29 de octubre de 2026. Corte de evaluación: 28/10/2026. Fuentes nuevas activadas en SQL y controles de revisión comprobados.

## Comprobación actualizada del 28/10/2026

Datos activos: `evaluacion_local_20261028`, con producción hasta el 27/10. Persistencia SQL EP verificada contra las cinco fuentes limpias: conteos y total de tallos coinciden con Parquet. Evidencia: `storage/verification_sql_evaluacion_20261028.json`.

El cuaderno 26 ejecutado evalúa 43 semanas objetivo hasta 2026-10-19; conserva configuración, separaciones temporales, controles por corte y contraste mensual/congelado. El histórico actualizado usa esa evaluación y las últimas fuentes validadas; la prueba original sigue accesible por separado.

El frontend compila y se aprobaron las 54 pruebas del backend, incluyendo comparación, actualización de métricas, ajustes, revisión persistente, conservación de inventario y transporte SQL. Las verificaciones de navegador registran selección múltiple de variedades, rango de semanas, controles de curvas, navegación de regreso y ausencia de desbordamiento móvil. Evidencia: `storage/verification_review_ui.json` y `storage/verification_comparison_navigation.json`.

El borrador operativo `a90ff882-4f89-46c5-81d7-1052c54956ef` contiene 565 líneas para 113 series y cinco horizontes. Coincide con el cálculo del cuaderno 26: diferencia máxima de 0 tallos. No fue publicado automáticamente. Evidencia: `storage/verification_updated_evaluation.json`.

La lista siguiente conserva la evidencia del cierre anterior del 26/10; sus cantidades y fechas se interpretan como referencia histórica, no como la fuente activa actual.

## Comprobaciones ejecutadas · referencia del 26/10

| Comprobación | Resultado |
| --- | --- |
| Frontend React/TypeScript | `npm.cmd run build` termina correctamente. |
| API FastAPI y migración Alembic | Funcionan contra SQL Server `Proyectos`, esquema `EP`; migraciones hasta 0007. Documentación en `/docs`. |
| Reglas críticas del backend | 29 pruebas aprobadas, incluyendo recepción de archivos sin bloquear otras peticiones e inspección acotada sin cadenas compartidas, además de comparador, ETL, inferencia, ajustes, publicaciones y persistencia. |
| Regresión del adaptador 19 | 584 casos del origen 2026-08-03, incluyendo H1–H5. Diferencia máxima y media frente a las predicciones archivadas: **0 tallos**. |
| Generación real mediante trabajador | Última propuesta: origen 2026-10-26 (S44), 565 líneas, 113 series y cinco horizontes, sin clima. Borrador; no se publicó automáticamente. |
| Navegador de escritorio | Cuatro módulos. Comparador revisado con Microsoft Edge/Playwright: semana única, rango, filtros, producto → color → variedad, búsqueda, cantidades y conservación del contexto del resumen. Sin errores JavaScript. |
| Flujo operativo | Generar, filtrar producto/color/variedad, ajustar, restaurar y descargar un Excel real. Los ajustes de prueba se restauraron al valor inicial. |
| Curva de variedad | DINO, 64 puntos de rendimiento por planta/edad desde el archivo de curvas de proyecciones 2026; sin reconstruir otra normalización. |
| Móvil | Ancho 390 px, navegación y pronóstico revisados, sin desbordamiento horizontal del documento. Las tablas tienen su propio desplazamiento. |
| Persistencia de versiones | El borrador local y sus 590 líneas se transfirieron a SQL Server conservando identificadores, ajustes y auditoría. Los servicios se reiniciaron contra SQL Server. |
| Archivos privados | `.env`, `.venv`, `storage/` y `node_modules/` quedan excluidos de Git. |
| WebFlor, descubrimiento y empalme | Conexión de lectura al procedimiento real; 142.159 registros descargados, 4.318 combinaciones de empalme idénticas tras normalizar nombres y 43.863 registros nuevos incorporados y activados en SQL; 6.543.848 registros reales, con último movimiento el 24/10/2026. |
| Preparación visual | Tabla de fuentes con fechas, archivos, siguiente acción y requisitos relativos a H1; controles separados de recepción y activación. Escritorio y móvil sin errores JavaScript ni desbordamiento en la revisión durante ETL. |

La evidencia numérica de regresión está en [evidencia_regresion_modelo19.json](evidencia_regresion_modelo19.json). Capturas de revisión, logs, archivo Excel de prueba y modelos entrenados están en `storage/`, fuera de Git. El registro de pruebas del navegador conserva un borrador real en la base local; no publicó una versión oficial.

## Qué no está certificado todavía

- Regresión completa de todos los orígenes/cortes históricos y emisión operativa del jueves. La coincidencia de un origen con cinco horizontes es evidencia parcial, no una certificación de toda la evaluación.
- Réplica exacta de las hojas/tablas dinámicas del Excel del ingeniero. El archivo exportado actual se identifica como formato preliminar.
- Construcción y ejecución Docker: configuración preparada y YAML revisado; no hay Docker disponible en esta estación para probar las imágenes.
- Usuarios/SSO corporativos, operación pública, recuperación integral y entrenamiento para otras fincas. El modo local y los tokens sirven para revisar el prototipo.

## ETL y cierre operativo anterior · referencia del 26/10

Se implementó la cadena de archivos originales → limpiezas de referencia → proyecciones → base analítica y variables → fuentes limpias SQL → activación transaccional. Los originales se archivan fuera de SQL; las fuentes sin cambios reutilizan su versión SQL. [ETL_Y_SQL.md](ETL_Y_SQL.md) describe las modalidades por fuente y las vistas vigentes de EP.

Se recuperó la hoja adicional de producción `Hoja1` y se incorporó el incremento de WebFlor. La versión activa `769d857a-6995-457d-a161-22d199701861` contiene 6.543.848 registros de producción real, hasta el 24/10/2026. El origen analítico es 26/10/2026 (S44). Las cinco vistas vigentes de EP y los totales de tallos coinciden con los Parquet: `storage/verification_operational.json` tiene `passed: true`. Se eliminaron únicamente las filas de una carga fallida nunca activada ni referenciada, conservando su trazabilidad.

El clima llega al 21/09/2026 y los planos a S41: `Sin_clima` está disponible y la propuesta actual utiliza la ruta validada de producción reciente. Para incorporar teoría del origen S44 hace falta su plano; para habilitar clima hace falta actualizar esa fuente. Las estadísticas históricas siguen siendo utilizables. ARABELLA se conserva en las fuentes; la inferencia inicial está validada para GAITANA.

La interfaz muestra los sesgos del modelo y del ingeniero y las semanas exactas del panel de prueba. La evaluación retrospectiva archivada del 19 se conserva aparte de los pronósticos operativos nuevos. La regresión se repitió tras los cambios de integración: 584 casos de H1–H5, diferencia máxima de 0 tallos.

`python -u -m scripts.verify_operational actualizacion_20261026 --wait` espera la activación, comprueba catálogo/esquema/estado, genera un borrador por HTTP y verifica sus cinco horizontes y la conservación de las versiones anteriores. Guarda su resultado en `storage/verification_operational.json`; sólo la existencia de un reporte con `passed: true` confirma que ese cierre terminó. No publica un pronóstico.

El cierre ampliado `python -u -m scripts.finish_operational_workflow` verifica primero esa carga, solicita la actualización de WebFlor mediante el mismo endpoint del botón y después verifica un nuevo borrador sobre la base resultante. Conserva la evidencia inicial en `verification_initial_sql.json` y deja la evidencia más reciente en `verification_operational.json`. Ver [WEBFLOR.md](WEBFLOR.md) para límites de la fuente y reglas de incorporación.

## Cómo leer el histórico

El selector distingue entrenamiento (diagnóstico H1 del ajuste archivado con corte 03/08/2026), validación de 2025 (selección de variantes), prueba de 2026 (panel conservado del cuadernillo 19) y seguimiento de nuevas semanas. Cada vista muestra sus semanas exactas, WAPE y sesgo de ambos, calculados sobre las mismas combinaciones con real, modelo e ingeniero. Entrenamiento no mide anticipación: sus resultados ya se conocían al ajustar. No hay predicciones individuales de entrenamiento archivadas para H2–H5.

Para entrenamiento y validación se cruza el estimado por finca/producto/color/variedad, origen y horizonte nominal; el inicio del nombre del archivo sigue identificando H1. Se informa cuántos casos quedan fuera de la comparación por no tener estimado nominal del ingeniero. No se completan con cero ni se convierten estimados de otra edición en H1.

El seguimiento aumenta al incorporar cortes reales, pero sólo para publicaciones anteriores al inicio de su origen y semanas objetivo terminadas. Los borradores y las simulaciones hechas después no cuentan como validación nueva. Por ahora no hay publicaciones anticipadas evaluables. Las cargas nuevas no reescriben los archivos originales de validación y prueba. **Actualizar evaluación** vuelve a consultar los datos disponibles.

## Comparador independiente

El menú tiene cuatro secciones. **Histórico y desempeño** conserva una vista general por evaluación y horizonte. **Comparador de errores** permite seleccionar una semana o un rango y filtrar producto, color y variedad; el botón **Explorar errores** del resumen conserva su evaluación y horizonte al abrirlo.

El comparador muestra WAPE, sesgo porcentual y neto en tallos, trayectoria real/modelo/ingeniero y una tabla con cantidades y contribuciones al error absoluto. Cada grupo permite bajar al siguiente detalle; la tabla tiene búsqueda y páginas de 20 filas. La búsqueda sólo afecta la tabla, no cambia los indicadores generales. Los mayores aportes se ordenan según modelo o ingeniero.

La comparación sigue usando los mismos casos nominales para ambos y un horizonte por consulta. El error absoluto se calcula por caso antes de agrupar: diferencias positivas y negativas no se cancelan. La suma del desglose reproduce el total y el WAPE total no promedia los WAPE de los grupos. La evidencia del navegador está en `storage/verification_comparison.json`, con capturas de escritorio y móvil; no hubo desbordamiento horizontal del documento.

## Recepción de archivos y planos múltiples

Se sustituyó la apertura inicial con openpyxl por lectura acotada del índice XML. La apertura anterior podía cargar cadenas y cachés de libros grandes dentro de una petición asíncrona y bloquear la API. Ahora la inspección y el registro SQL se ejecutan fuera del bucle HTTP; no se cambió el ETL estadístico.

La ventana de carga muestra progreso real del envío y después confirmación del servidor, con resultado individual, errores y reintento. Para planos acepta varios archivos del mismo año y los envía secuencialmente; un error no impide confirmar el siguiente. Los recibidos quedan pendientes del ETL y los repetidos no se duplican. Mientras se envía un lote, la ventana conserva el proceso visible.

Prueba en navegador contra SQL: dos planos existentes en 4,927 s, estimado existente en 3,097 s y clima existente de 196.161.897 bytes en 5,625 s; se reconocieron sin duplicar ni activar datos. La comprobación del encabezado de ese clima, medida por separado, tardó 0,005 s. Estos tiempos corresponden a recepción/reconocimiento, no a la limpieza completa. La API respondió durante la prueba (18 consultas de salud, máximo 2,102 s). Evidencia: `storage/verification_upload_fix.json`. También se comprobó que un Excel inválido muestra su error y permite continuar con otro plano.

Las cargas del usuario `Informe Clima  2026 a sem 42.xlsx` y `Plano de Siembras Sem 42.xlsx` constaban como `pendiente_etl` al verificar: ya fueron recibidas y no requieren otra subida. Después de completar el lote se debe solicitar **Procesar archivos** para incorporarlas a la base vigente.
