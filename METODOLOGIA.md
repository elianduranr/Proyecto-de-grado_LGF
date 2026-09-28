# Metodología vigente del proyecto

## 1. Problema analítico

Estudiar las diferencias entre estimado y producción reportada por producto, color y variedad, y preparar un sistema de actualización del pronóstico. La producción depende de siembras, población, edad y curvas; clima y producción reciente son variables candidatas, no causas demostradas.

El flujo organiza y valida datos, construye la base, realiza EDA, prepara variables y compara primeros modelos. La hipótesis central es que la producción real reciente informa el ajuste de las semanas siguientes; no se afirma que cortar hoy cause biológicamente mayor producción futura. No se selecciona todavía un ganador operativo.

## 2. Fuentes y unidad de análisis

Se utilizan cinco familias Excel originales: producción real, estimados del ingeniero, planos de siembra, curvas empíricas y clima. WebFlor aporta sólo proyecciones almacenadas y coeficientes internos con sus dimensiones.

Las limpiezas conservan sus fincas originales. La base principal filtra GAITANA exacta. Su grano es finca × producto × color × variedad × semana objetivo con producción observada. La unidad del target es tallos reportados; no se presume equivalencia automática con ESTI. EXPORTABLE.

La semana 53 se transforma en semana 1 del año siguiente por la regla del ingeniero; las fechas y etiquetas fuente se conservan. Las auditorías SQL no se reinterpretan como semanas de generación.

## 3. Limpieza conservando la lógica original

Cada familia tiene un notebook autocontenido en `Notebooks/Limpieza data, Notebooks y Scripts/`. Las transformaciones y controles se leen directamente en sus celdas.

### Producción

Se leen todas las hojas de detalle; sólo se eliminan filas completamente vacías en las columnas productivas. Se normalizan dimensiones, fecha, enteros y hora. No se eliminan cortes legítimos por tener valores repetidos.

Tipo Corte se imputa con la moda de producto/color/variedad en las semanas anterior, actual y siguiente dentro del libro, conservando el valor original y una bandera. Esta reconstrucción retrospectiva no se usa como predictor al origen.

### Estimados

Se extraen registros TIPO=ESTIMADO de la caché interna Excel. Se elige el archivo principal no ajustado por año/semana con las prioridades del proceso original. El año se interpreta desde el nombre antes que desde la carpeta.

Si falta un archivo, se usa el siguiente disponible del mismo año. H1–H5 se calculan desde la semana solicitada y se extraen del archivo elegido. Se conservan origen solicitado, origen nominal del archivo, objetivo, horizonte y marca de archivo posterior. Nunca se desplaza el objetivo ni se inventan cantidades.

La recuperación de un archivo posterior es necesaria para reconstruir el benchmark solicitado; no demuestra disponibilidad histórica del pronóstico.

### Planos, curvas y clima

Los planos representan estado semanal, no nuevas siembras para sumar entre semanas. Se identifica edición, ambigüedad de segmentos y validez de edad.

La edad reportada usa la fórmula Excel ROUND((AL1 − fecha_siembra)/7, 0), reconocida en los 293 libros con hoja Datos. Se valida contra AL1, no contra el lunes del nombre del archivo. La edad al lunes se conserva como semanas completas desde la siembra. Se guardan ambas fechas/edades y las discrepancias reales. AL1 no se interpreta como fecha de publicación.

Las observaciones piloto se desduplican entre libros acumulativos con llaves defendibles, sin elegir coincidencias ambiguas. Los coeficientes SQL no se sustituyen por estas curvas empíricas.

El clima se desduplica por medición y finca; conflictos y tiempos inválidos se señalan. Se agrega por día y luego semana para no sesgar por frecuencia de muestreo.

## 4. Base analítica y benchmark

La producción agregada es la tabla izquierda de todas las uniones. Cada auxiliar se lleva al grano adecuado antes del join. Se validan unicidad, cardinalidad, pendientes y conservación de tallos por llave.

El benchmark conserva dos etapas: unión estricta por finca/producto/color/variedad/semana y recuperación sólo del remanente por finca/producto/variedad/semana con relación 1:1. Si hay varios candidatos no se fuerza una equivalencia. Se mantienen el color de producción y el del estimado, además del método de unión.

H1–H5 se guardan como columnas para no multiplicar producción. Los objetivos sin real permanecen en el limpio de estimados. Ausencia de dato no equivale a cero.

Se integra sólo el estado actual WebFlor agregado. Sus archivos históricos permanecen identificados en el limpio SQL; no se suman entre sí ni se consideran automáticamente corridas completas.

El potencial plantas × rendimiento mediano por edad es un proxy descriptivo con controles de soporte/cobertura, no una reproducción exacta de WebFlor ni producción observada.

## 5. EDA y evaluación del error

Se examinan cobertura, composición productiva, población/edad, potencial, clima y rezagos. Se estudian asociaciones por serie y periodo para evitar que el volumen agregado oculte diferencias de color/variedad.

La desviación se define como real − estimado. Se calculan error absoluto, MAE, WAPE y sesgo donde hay pares; se informan cobertura y tamaño de muestra. Los porcentajes individuales excluyen denominadores inadecuados.

También se excluyen de las métricas las sumas de estimados con alguna cantidad fuente faltante. Se conserva su registro y su bandera en la base; una suma parcial no se interpreta como pronóstico completo.

Se separan archivos posteriores de archivos nominales y recuperaciones por variedad de coincidencias estrictas. Estas métricas son diagnósticos descriptivos condicionados a las unidades y fechas disponibles, no validación certificada de una corrección histórica WebFlor.

## 6. Prevención de fuga temporal y disponibilidad

Una fila predictiva es serie × origen × horizonte. El origen es el lunes; H1 corresponde a la semana que comienza, H5 a cuatro semanas después (+1…+5 desde la última semana cerrada). Se usan producción pasada, medias no centradas, clima pasado y estado agronómico anterior. Se excluyen clima futuro, producción objetivo, imputación retrospectiva de Tipo Corte, curvas de todo el histórico y estimados recuperados como si hubieran sido conocidos antes.

El experimento supone disponibilidad de producción y clima al cerrar la semana. Para planos usa la última observación bajo disponibilidad supuesta posterior al cierre nominal y a AL1, con tolerancia de cuatro semanas. No se certifica recepción real: se repite una evaluación con demora adicional de una semana. El clima exige cinco días para representar una media semanal. No se calcula energía o lluvia acumulada sin definición de unidades/intervalo.

Una prueba altera cantidades futuras y comprueba que las features de orígenes anteriores permanecen iguales. Detecta fuga en el código, no demuestra fechas reales de publicación.

Una proyección WebFlor puede permanecer vigente entre semanas. Para corregirla históricamente hacen falta evidencia de disponibilidad, ámbito y eventos de sustitución o retiro; no imponer corridas semanales.

Decisión WebFlor: no asignar proyecciones históricas mediante as-of sobre FechaAuditoria. El archivo se asocia a erradicación y no acredita cuándo era conocido. Una futura asignación usaría la última referencia acreditada anterior al origen, por ámbito y objetivo, y terminaría ante reemplazo o retiro. No se exige recalcular semanalmente.

## 7. Comparación de modelos

09 implementa tres cortes temporales (2025-07-07, 2026-01-05 y 2026-05-04), ocho orígenes semanales por corte y H1–H5. El entrenamiento sólo incluye objetivos cerrados al corte. Se requieren 26 observaciones previas y cuatro semanas recientes completas; se informa cobertura por casos y volumen. No se imputa y ni se puntúan ausencias como cero. Por ello no es una evaluación de toda combinación potencialmente activa de la finca.

Se comparan último valor, media cuatro semanas, una reacción fija del 50% a la producción más reciente, Ridge y variantes de HistGradientBoosting. Las variantes añaden memoria productiva, siembras y clima sobre idénticos casos. Una variante aprende la corrección a media4; es una corrección estadística válida bajo los supuestos, no una corrección WebFlor. La referencia estacional de 52 semanas se compara sólo en su población común.

Imputación y codificación se ajustan dentro de cada train. No hay split aleatorio ni early stopping con validación aleatoria. Se usan parámetros fijos, sin búsqueda masiva. El modelo queda fijo en cada bloque y recibe nuevas features al avanzar el origen.

Se reportan MAE, RMSE, WAPE, sesgo real−predicción y proporción dentro de ±8% del real positivo. Se desagrega por corte, horizonte, producto, color, variedad y volumen histórico. El umbral ±8% viene del Plan de Proyecto y requiere confirmación operativa. El agregado no reemplaza el error desagregado.

La evaluación es retrospectiva bajo supuestos, no un test prospectivo intacto. La simulación final usa un candidato fijado, media4 corregida, desde el último origen local. No se anuncia como pronóstico emitido en ese origen ni como pronóstico actualizado a hoy. Quedan pendientes equivalencia exportable, disponibilidad, ausencias/cero y validación con datos nuevos. No se instala ARIMA/SARIMAX ni se multiplica el número de algoritmos en esta primera comparación.

## 8. Implementación sencilla y trazabilidad

Cada limpieza exporta una sola tabla. SQL exporta dos complementos finales; sus dependencias viven en memoria. `06_construccion_base_analitica.ipynb` exporta una sola `base_analitica.parquet`; 07, 08 y 09 no crean datasets adicionales. 09 incluye explícitamente la misma preparación de 08 para poder ejecutarse solo, sin scripts auxiliares.

Las salidas están en `Datos_analiticos_proyecto/`. No hay versiones por ejecución, backups automáticos, cifrado, manifiestos técnicos ni módulos propios obligatorios.

El detalle de rutas, ejemplos de recuperación y controles está en [GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md](GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md).
