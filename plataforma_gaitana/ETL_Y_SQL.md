# Cargas y persistencia de la plataforma

El destino es **Proyectos**, esquema **EP**. Las credenciales se leen del `.env` local, excluido de Git. El lanzador ejecuta las migraciones antes de iniciar los servicios. Las tablas existentes de otras aplicaciones no se modifican.

## Qué se guarda

- Los Excel originales se conservan por SHA-256 en `storage/source_archive/`. SQL almacena su catálogo y trazabilidad; no guarda copias de los libros.
- Las cinco fuentes limpias se guardan en `EP.lgf_produccion_real_limpio`, `EP.lgf_clima_limpio`, `EP.lgf_planos_siembra_limpio`, `EP.lgf_curvas_variedad_limpio` y `EP.lgf_estimados_semanales_limpio`. Sus columnas corresponden a los Parquet existentes, más el identificador de ejecución y número de registro.
- Cada ejecución conserva un directorio privado en `storage/datasets/`: fuentes congeladas, notebooks congelados, maestros, resultados derivados y logs. Las proyecciones y variables derivadas se leen desde ese directorio para inferencia; no duplicamos esos mismos derivados en SQL.
- `EP.lgf_datasets` registra la ejecución y `EP.lgf_active_dataset` identifica la única base vigente. `EP.lgf_source_files` mantiene el catálogo de archivos que se utilizará en las siguientes cargas.
- `EP.lgf_dataset_sources` vincula cada ejecución con las versiones de sus cinco fuentes. Si una fuente limpia conserva la misma huella, reutilizamos sus registros SQL; no insertamos otra copia por actualizar una fuente diferente. Las vistas `EP.vw_lgf_produccion_real`, `EP.vw_lgf_clima`, `EP.vw_lgf_planos_siembra`, `EP.vw_lgf_curvas_variedad` y `EP.vw_lgf_estimados_semanales` devuelven directamente la información vigente.
- Pronósticos, ajustes, publicaciones y auditoría continúan en sus tablas `EP.lgf_*`. Generar una simulación no publica un estimado.

Los datos y el archivo original deben respaldarse juntos: reconstruir los contenedores no debe borrar el volumen `storage`.

## Recorrido de una actualización

1. Revisar el estado de las fuentes en **Generar y ajustar**. Si el Excel ya está en las carpetas originales, no hay que subirlo otra vez.
2. Cargar las fuentes adicionales que hagan falta, indicando fuente, año y modalidad. El archivo se archiva y queda pendiente; todavía no sustituye los datos vigentes.
3. Pulsar **Procesar archivos**. El trabajador ejecuta fuera de HTTP las limpiezas 01–05, catálogo 00, proyecciones de todos los años desde Excel, auditoría de curvas, consolidación de proyecciones, base analítica 10 y variables diarias 01.
4. Comprobar estructura, unicidad de casos, horizontes y conservación de tallos. Persistir las tablas limpias por bloques y verificar sus conteos.
5. Cambiar la referencia vigente en una transacción, registrar auditoría y marcar las cargas como procesadas. Solo entonces el front avanza su fecha disponible.

Si falla una etapa, la base vigente permanece intacta. Los logs indican el notebook y la etapa. Los bloques SQL incompletos pertenecen a una ejecución sin activar y no se presentan como datos actuales. Reanudar la misma ejecución permite continuar desde sus controles; un nuevo intento tiene su propio identificador.

Las etapas que conservan los mismos archivos, maestros y código reutilizan sus resultados validados. El lector XML procesa bloques acotados y almacena una caché privada por huella de archivo y código; mantiene el decodificador, filtro final y orden del notebook. El cambio se contrastó con el lector original en tres libros: 4.026 filas idénticas, incluidos sus metadatos.

## Modalidades y límites explícitos

| Fuente | Regla |
| --- | --- |
| Producción real | Completo reemplaza lógicamente el año indicado. Adicional admite fechas posteriores al último corte procesado; un archivo que cruza fechas existentes requiere carga completa. No se eliminan movimientos legítimos por tener los mismos valores. |
| Clima | Completo reemplaza ese año. Adicional conserva la hoja BD y admite fechas nuevas. Los conflictos y repeticiones de mediciones siguen las reglas del notebook. |
| Planos | Solo se añaden semanas faltantes. Una edición distinta para una semana existente requiere revisión explícita. |
| Estadísticas | Archivo completo por año y familia: Clavel, Mini Clavel, Green Ball o Raffine/Solomio/Otros. Las otras familias y años permanecen. |
| Estimados | Se conservan las semanas y ediciones anteriores. Reemplazar el mismo nombre afecta solo esa edición en la nueva ejecución; las ejecuciones previas conservan el original. El nombre identifica H1, según la regla validada del notebook. |

Esta primera integración conserva los formatos conocidos de 2021–2026. Las cargas deben mantener hojas y encabezados originales. Un formato nuevo requiere revisar su contrato; no se inventan equivalencias ni columnas.

### Producción de 2026: hojas de detalle adicionales

La revisión de los originales encontró movimientos nuevos en `Hoja1` de `Producción Acumulada 2026.xlsx`, además de `BD`. El limpiador 05 ahora identifica hojas adicionales por sus encabezados de detalle (finca, fecha de corte, producto, color, variedad y tallos). No importa las hojas resumen ni tablas dinámicas como movimientos. Antes de unir un bloque adicional, comprueba que sus fechas no se solapen con las de otros bloques; un solapamiento requiere revisión y no se resuelve borrando cortes iguales.

En la ejecución `actualizacion_20261026`, `Hoja1` aporta **23.669 registros y 1.984.077 tallos**, con cortes del 5 al 10 de octubre: **18.086 registros y 1.545.620 tallos de GAITANA**, y 5.583 registros y 438.457 tallos de ARABELLA. El consolidado limpio contiene **6.499.985 registros**, con corte máximo el **10 de octubre de 2026**. La base analítica resultante llega al origen **12 de octubre de 2026 (S42)**. Estos conteos describen los resultados validados del ETL; la carga SQL debe terminar y activar esa ejecución antes de usarlos en la aplicación.

Las columnas de texto de las fuentes normalizadas usan `NVARCHAR(500)`, previa validación de longitud UTF-16; no se truncan valores. Se evita `NVARCHAR(MAX)` en estos campos porque perjudicaba el rendimiento de la carga masiva mediante ODBC. Un valor que exceda el contrato detiene la carga y requiere ampliar la columna mediante migración.

## Modelo y evaluación

Se conserva el adaptador del cuadernillo 19. No se ajustan hiperparámetros ni se incorporan estimados del ingeniero como predictores. El modelo usa la última ejecución activada; la huella de sus insumos invalida las cachés anteriores.

El panel de prueba histórico sigue siendo el validado del 19 y muestra sus semanas exactas, WAPE y sesgo del modelo y del ingeniero. Una carga de datos nuevos no convierte automáticamente esas semanas en nuevos casos de prueba ni reescribe esa evaluación. La producción reciente del módulo de pronóstico sí usa la base activada.

La prueba de regresión `python -m scripts.verify_model19` utiliza expresamente las entradas de referencia originales. Así se puede comprobar que modularizar el modelo no cambió sus predicciones, aunque la base operativa ya haya avanzado.

El clima atrasado no bloquea **Sin clima**. La variante climática se habilita cuando la fuente alcanza la semana previa al origen; no se inventan mediciones para habilitarla. La habilitación no afirma que estén presentes todas las mediciones esperadas de esa semana.

La reproducción exacta del Excel del ingeniero queda para la siguiente fase.

## Conexión directa de producción

[WEBFLOR.md](WEBFLOR.md) describe la fuente real comprobada, la ventana de 45 días del reporte, el empalme con el Excel, el botón de actualización y los controles para incorporar sólo cortes nuevos. La conexión de lectura a WebFlor es independiente de la conexión de escritura a `Proyectos.EP`.

Las fechas de las fuentes usan `DATETIME2` en SQL Server (migración 0006), conservando valores originales y banderas de calidad que no cabían en el rango de `DATETIME`. La migración 0007 limita las vistas al alcance registrado de cada versión para permitir adiciones sin repetir todo el histórico. No se cambió la limpieza estadística para resolver una limitación del tipo SQL.
# Transporte SQL verificado (29/10/2026)

La escritura conserva las mismas tablas tipadas, filas, límites por versión y transacciones. Para SQL Server 2016 o posterior con compatibilidad 130, los lotes viajan comprimidos y SQL los convierte a su esquema explícito mediante `DECOMPRESS` y `OPENJSON`. En otros motores se mantiene la inserción convencional. No cambia las limpiezas, las proyecciones, el entrenamiento ni las métricas.

La prueba temporal comparó todas las columnas de 2.000 filas por cada una de las cinco fuentes (10.000 filas en total), incluidos nulos, fechas, números y textos Unicode. El ensayo de producción midió 26,98 s con ODBC convencional y 2,06 s con compresión; es una medición local, no una garantía de tiempo para cualquier carga. Evidencia privada: `storage/verification_sql_transport.json` y `storage/verification_sql_transport_sources.json`.

Los lotes confirmados de una ejecución interrumpida se reutilizan sólo si el hash del archivo coincide; no se duplican. Los valores que exceden la longitud de su columna se rechazan antes de escribir, sin truncarlos. La activación sigue esperando todos los conteos y controles.

Referencia técnica: [OPENJSON y compatibilidad de SQL Server](https://learn.microsoft.com/en-us/sql/t-sql/functions/openjson-transact-sql), [DECOMPRESS y conversión a NVARCHAR](https://learn.microsoft.com/en-us/sql/t-sql/functions/decompress-transact-sql).
