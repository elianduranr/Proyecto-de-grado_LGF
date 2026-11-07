# Bitácora de la revisión conversada de la metodología

## ETL, SQL Server y actualización directa del corte — 26 de octubre de 2026

Se conectó el prototipo a `Proyectos` usando exclusivamente el esquema `EP`, con migraciones, fuentes limpias tipadas, catálogo, auditoría y una referencia transaccional a la base activa. Se implementó el procesamiento de los originales en versiones privadas, conservando las limpiezas, proyecciones y variables del proyecto. Una carga fallida no sustituye los datos vigentes; una fuente sin cambios reutiliza sus registros SQL. La regresión del adaptador del 19 sigue coincidiendo exactamente en los 584 casos de referencia de H1–H5.

La revisión de producción encontró una hoja adicional de detalle de 2026 que no se estaba leyendo. El limpiador reconoce sus encabezados y excluye resúmenes; `Hoja1` aporta 23.669 registros y 1.984.077 tallos hasta el 10 de octubre. Las fuentes conservan ARABELLA y GAITANA, pero la inferencia validada del prototipo sigue limitada a GAITANA. Se amplió el tipo SQL a `DATETIME2` para guardar fielmente fechas originales y sus banderas de calidad; no se alteró el criterio estadístico para adaptarlo a la base de datos.

Se comprobó la conexión de lectura de WebFlor y el procedimiento real `Reporte.InformeCorteInvVariedad`, que limita la consulta a 45 días. La descarga de días cerrados mostró 4.318 combinaciones comerciales/diarias idénticas al histórico tras normalizar nombres y 43.863 registros nuevos posteriores al 10 de octubre. El botón de actualización archiva la fuente, verifica el período común y añade sólo fechas nuevas mediante el mismo ETL. Una diferencia histórica exige revisión y no provoca sobreescrituras automáticas. La evidencia de activación completa y pronóstico nuevo se guarda separada de este diagnóstico de empalme.

La interfaz ahora distingue lo procesado de lo recomendable para H1: fecha o semana, archivos recientes, período necesario, pendientes y siguiente acción por fuente. Clima y estadísticas históricas no se convierten en una obligación de actualización semanal para Sin clima. Los planos se relacionan con la teoría del origen; si falta el plano, se explica la ruta de producción reciente. El histórico muestra también el sesgo del ingeniero y cada semana del panel de prueba. Las cargas nuevas no reescriben automáticamente la evaluación archivada ni demuestran una mejora de WAPE.

El recorrido y los pendientes verificables están en [el estado del prototipo](plataforma_gaitana/ESTADO_PROTOTIPO.md), [ETL y SQL](plataforma_gaitana/ETL_Y_SQL.md) y [WebFlor](plataforma_gaitana/WEBFLOR.md). El Excel oficial y la validación de emisión del jueves continúan separados de esta integración.

## Primer prototipo funcional — 23 de octubre de 2026

Se creó `plataforma_gaitana/` con React/TypeScript/Vite, FastAPI, trabajador independiente, SQLAlchemy/Alembic, recepción de Excel, ajustes con sumas exactas, auditoría y versiones con publicación explícita. La interfaz tiene los tres módulos solicitados, identidad vinotinto y curvas normalizadas existentes. La regresión del adaptador del 19 coincidió exactamente en 584 casos de H1–H5 de un origen; una generación real produjo 590 líneas y quedó en borrador. Se probaron escritorio, móvil, ajuste/restauración, descarga, permisos y persistencia tras reinicio. El entorno del prototipo está separado del de notebooks y las credenciales se conservan en `.env` local. Los límites —SQLite local, cargas pendientes de ETL, plantilla preliminar y Docker/SQL Server sin ejecución comprobada— se explicitan en [el estado del prototipo](plataforma_gaitana/ESTADO_PROTOTIPO.md); no se declara terminada toda la plataforma.

## Plataforma operativa — 23 de octubre de 2026

El usuario definió la aplicación empresarial y autorizó desarrollar por fases, empezando por revisar antes de programar. El alcance queda en [docs/ESPECIFICACION.md](docs/ESPECIFICACION.md); la evidencia local, arquitectura y plan están en [Fase 1](docs/FASE_1_REVISION_Y_ARQUITECTURA.md). Se acuerdan originales persistentes fuera de SQL, datos normalizados en `proyectos`, separación generar/ajustar/publicar y preservación del cuadernillo 19 antes de mejoras. La revisión recalculó métricas de predicciones existentes (19,36 % WAPE en 16.325 casos estrictos), identificó una ruta duplicada en el código del 19 y diferencias entre emisión real y origen nominal que deben resolverse para reproducir e integrar. Se registran huellas y entorno observado; no se reentrenó, no se modificaron notebooks ni fuentes y no se conectó al servidor. La plataforma, sus migraciones y su despliegue aún están pendientes.

Actualización: 8 de octubre de 2026.

## Instrucción vigente del usuario

El usuario autorizó aplicar la revisión acumulada: actualizar el EDA climático, el documento formal, la guía y las explicaciones metodológicas, conservando resultados y sin exagerar la extensión. Mantener todos los resultados diarios, pero marcar al inicio de sus secciones «(En revisión: desarrollo preliminar y siguientes pasos.)». Las señales diarias usadas para predecir semanas permanecen en el análisis semanal principal. No se solicitó entrenar nuevos candidatos ni ejecutar todavía los experimentos futuros de horizonte/producto. Esta bitácora resume acuerdos y evidencia; no es transcripción literal completa.

## Lo que ya se aclaró y modificó

### Notebook de lectura

En `lectura.ipynb` se añadió la carga del parquet común de 621.195 filas y 47 columnas, explicación del registro, ejemplo real ejecutado y diccionario. Una fila corresponde a finca/producto/color/variedad + origen + horizonte. La misma producción objetivo puede repetirse desde distintos orígenes: no sumar toda la columna `y` como producción física distinta. `y` es el resultado real posterior, no una entrada disponible al emitir el pronóstico. No contiene el pronóstico final ni el estimado del ingeniero.

Se explicó seno/coseno paso a paso, con calendario circular, dibujo y cálculo de la semana ISO 36: seno −0,935 y coseno −0,355. No son porcentajes ni indican subidas o bajadas de producción. Se obtienen de la semana objetivo, no del número H1–H5. El cálculo usa un ciclo fijo de 52 semanas.

Se aclaró que `teoria` corresponde solo a la semana objetivo, no al acumulado hasta el horizonte. `teoria_previa_1/2` son versiones anteriores para la MISMA semana y serie comercial, no H1/H2. Las teorías previas conservan solo valores completos, mientras `teoria` puede guardar una suma parcial. No se salta una versión incompleta para buscar una anterior completa.

Los horizontes del modelo y del generador teórico difieren: modelo H1–H5 contando H1 como la semana de origen; generador teórico 10 semanas contando desde la semana siguiente a fecha_plano. El ejemplo conversacional H5→H6→H7 fue simplificado y se corrigió con las fechas reales.

### Ejemplo real DINO y cobertura

Última fila en el orden del archivo con MINICARNATION, origen en 2026, historial admisible y producción real conocida: GAITANA / MINICARNATION / YELLOW / DINO, origen 2026-08-03, H5, objetivo 2026-08-31 a 2026-09-06. Producción real 18.970; última semana 19.202; media4 22.250,75; media8 22.893,75; 213 semanas históricas reportadas.

Plano seleccionado: semana 29, fecha 2026-07-13, disponibilidad asumida 2026-07-28. Teoría parcial 27.916,61; 25 cohortes; 2 sin cobertura. La cohorte agrupa plantas del mismo plano, finca/producto/color/variedad/clave de curva y fecha exacta de siembra: NO equivale necesariamente a una cama. Puede reunir varias camas; fechas distintas pueden compartir edad en semanas.

Detalle confirmado en `resultados_todos_los_anios/2026/proyecciones_teoricas.parquet`:

| Siembra | Plantas | Edad objetivo | Estado |
|---|---:|---:|---|
| 2026-05-12 | 5.040 | 16 semanas | edad_fuera_de_curva |
| 2026-07-02 | 13.104 | 9 semanas | edad_fuera_de_curva |

DINO sí tenía curva y la unión encontró su identidad; faltaban valores para esas edades. **Pendiente comprobar** si esos vacíos representan cero antes del inicio productivo o ausencia real de información. El usuario señaló que podrían ser ceros normales. No se ha verificado ni cambiado la regla. No afirmar que faltaba toda la curva de DINO ni que los grupos producían cero.

Para la misma semana objetivo, el plano semana 28 tenía teoría parcial 29.979,80 y dos grupos sin cobertura; el semana 27, 31.268,38 y dos grupos sin cobertura. Por eso las columnas previas quedan vacías, aunque existían las sumas parciales. Los horizontes teóricos son 7, 8 y 9 para planos semanas 29, 28 y 27, respectivamente; los tres alcanzan la semana objetivo.

### Notebook 12: diccionario ya incorporado

Se añadió al inicio de `Notebooks/Analisis/12_modelo_ajuste_proyecciones.ipynb` un diccionario de modelos, bloques de información, algoritmos, ejemplo de corrección, poblaciones comparadas y tablas de entradas. Se conservaron código y resultados.

Referencias sin aprendizaje: Ultimo_valor, Media4 y Teoria_sin_ajuste. Algoritmos aprendidos: Ridge y HistGradientBoostingRegressor. Con/sin memoria, con/sin clima e historia son variantes de entradas del boosting, no algoritmos diferentes. Sistema_teoria_con_respaldo selecciona una de dos rutas; no promedia ambas.

Memoria productiva = producción real pasada; historia de proyecciones = versiones teóricas anteriores. Identidad comercial significa producto, color y variedad. Finca identifica la serie en la base, pero no es una categoría entregada al algoritmo del 12.

Entradas originales antes de codificar categorías: ajuste Media4 21; teórico 24; teórico sin memoria 14; sin clima 18; Ridge teórico 24; teórico con historia 27. Sin memoria retira las nueve variables históricas y desviacion_reciente_teoria; conserva clima pasado. `y` nunca entra como predictor. Calidad, uniones, fechas y admisibilidad tienen otros usos. Recibir una variable no significa aprovecharla mucho.

## Evidencia y cambios pendientes para el final

### 1. Conectar EDA, hipótesis y comparaciones

El usuario no encuentra en el documento la justificación suficiente de tendencias y rezagos. Desarrollar la secuencia: asociación exploratoria → propuesta de variables → comparación predictiva. No presentar EDA como prueba de que cada rezago o ventana mejora el modelo.

Notebook 11, sección 4: Spearman dentro de cada serie y horizonte, mínimo 20 pares, objetivos cerrados antes de 2025-07-07, solo teoría completa. Relación con error real − teoría; medianas entre series:

| Variable | H1 | H5 |
|---|---:|---:|
| produccion_lag1 | 0,283869 | −0,027766 |
| cambio_reciente | 0,203639 | 0,061694 |
| media_4 | 0,134960 | −0,038431 |

Señal más clara cerca del origen, no causalidad ni porcentaje de mejora. El 12 contiene ablación del bloque de memoria; el 14 incorpora bloques de ventanas diarias, sin demostrar que cada ventana de 3/5 días aporte aisladamente. Importancia del 16 es por permutación, no SHAP ni efecto causal.

### 2. Corregir el resumen desactualizado del notebook 12

Las salidas ejecutadas vigentes difieren de las cifras escritas en su introducción. Corregir la narrativa al aplicar los cambios finales; no repetir como vigentes los 1.659 casos del texto antiguo.

Mismos **1.834 casos con teoría completa**, H1–H5, tres bloques temporales de evaluación:

| Método | WAPE (%) |
|---|---:|
| Teoria_sin_ajuste | 33,9730 |
| Teorico_sin_memoria | 25,4599 |
| Media4 | 24,3887 |
| Ridge_ajuste_teoria | 22,3834 |
| Ultimo_valor | 22,1507 |
| Ajuste_media4_sin_planos | 22,0540 |
| Modelo_teorico | 21,6781 |
| Modelo_teorico_historia | 21,4610 |
| Teorico_sin_clima | 21,3060 |

Aporte del bloque de memoria: reducción de 3,781849 puntos WAPE. Añadir clima empeora 0,372129 puntos en esa comparación. Historia reduce 0,217124 puntos, intervalo exploratorio [−0,01179752; 0,44829465], que incluye cero.

Sobre **14.108 casos admisibles**, ajuste Media4 21,1444 % frente a sistema con respaldo 21,1077 %: mejora de aproximadamente 0,04 puntos, pequeña. Coberturas de teoría por corte: 20,8421 %, 12,4607 %, 5,4454 %. No comparar métricas entre poblaciones diferentes como si fueran experimentos emparejados.

Notebook 12 es una etapa inicial, no la selección final. La configuración vigente se selecciona en 19 con validación temporal anterior a 2026: Sin_clima. Los periodos ya inspeccionados son desarrollo retrospectivo, no un test prospectivo intacto. No atribuir a 12 los resultados del 19.

### 3. Conectar el EDA climático 18 con las variables iniciales

Observación del usuario: el EDA 18 no parece justificar las variables climáticas usadas antes. Verificado: el 12 usa temperatura/humedad/radiación de semana anterior y media4 (seis variables). El EDA 18 analiza principalmente medias14 de temperatura/humedad/radiación y lluvia suma28. Además genera cambios7_28, otras variables de lluvia y cobertura que no estudia individualmente en sus gráficos principales. El 19 usa estos extras en Clima_ampliado.

El EDA 18 sí tiene función como extensión para el 19, pero no fundamenta por sí solo las seis variables originales. Para la actualización final: analizar las originales, explicar la hipótesis de las nuevas ventanas, compararlas con el mismo período y población, y conectar con las comparaciones con/sin clima. Mantener separado el desplazamiento temporal del corte del error de volumen. No prometer causalidad ni afirmar ausencia de efecto agronómico porque una variante sin clima gane.

### 4. Explicación didáctica de boosting para trasladar al material

HistGradientBoostingRegressor combina árboles pequeños por etapas para reducir errores. En la ruta teórica aprende y − teoria_modelo; después suma la corrección a teoría y limita a cero como mínimo. En respaldo aprende y − media4. Las condiciones de los árboles se aprenden; no se escriben reglas manuales como “si baja la producción, restar siempre”. Cada árbol puede combinar varias variables y no equivale a un bloque temático.

Ejemplos inventados usados para explicar deben etiquetarse como ilustrativos, no resultados reales. Se explicó por qué probarlo: relaciones no lineales, interacciones entre horizonte/serie/tendencia y datos tabulares; su utilidad debe sostenerse con evaluación temporal frente a referencias y Ridge. Parámetros verificados del 12: 80 etapas, learning_rate 0,08, máximo 15 hojas, mínimo 40 muestras por hoja, regularización L2 1, early_stopping desactivado. Hist agrupa valores en intervalos para buscar divisiones eficientemente. No significa que siempre sea superior o inmune al sobreajuste.

## Preferencias de presentación acordadas

- Conversación paso a paso, lenguaje natural y ejemplos concretos antes de fórmulas.
- En tablas de modelos, añadir SIEMPRE una descripción a la derecha, no solo nombres técnicos.
- Diferenciar referencia, algoritmo, entradas, corrección, ruta y horizonte.
- Explicar qué mide cada comparación y sobre qué población; no mezclar resultados semanales/diarios o etapas diferentes.
- Trasladar al documento (especialmente 4.2) y a la guía la lógica y definiciones al final de la revisión, evitando complejidad innecesaria.
- Continuar agregando aquí observaciones y decisiones futuras; no tratar hipótesis pendientes como hechos comprobados.

## Continuación: después de los modelos iniciales del 12

Se revisó el notebook 13 para explicar el siguiente paso: comparación del sistema teórico con respaldo frente al ingeniero sobre casos comunes de 2026, sin cambiar parámetros ni seleccionar retrospectivamente el ganador del 12. Reentrenamiento mensual con semanas objetivo ya cerradas; evaluación H1–H5. Comparación principal: 15.838 casos con unión comercial estricta y archivo no posterior bajo las fechas nominales. WAPE modelo 20,3561 %, ingeniero 19,7356 %. H1 modelo 17,0666 % vs. 17,0902 %; H2 18,4585 % vs. 19,2829 %; H3 20,6751 % vs. 20,3151 %; H4 22,6267 % vs. 20,9105 %; H5 23,4936 % vs. 21,4012 %. El sistema no supera al ingeniero en conjunto en esta etapa; ligera ventaja H1 y ventaja H2, desventaja H3–H5. No confundir con resultados vigentes posteriores del 19. Las limitaciones de unidad (estimado exportable vs. tallos reportados) y disponibilidad nominal siguen pendientes.

El paso posterior, notebook 14, propone añadir tendencias de corte diario disponibles antes del origen para comprobar si capturan movimientos que el agregado semanal oculta. Explicar esto como hipótesis a evaluar, no diagnóstico demostrado de la causa de los errores. Mantener la conversación por etapas.

## Continuación: primeras tendencias diarias del notebook 14

Se explica la hipótesis de añadir detalle de días recientes al pronóstico semanal, manteniendo inicialmente boosting, rutas y reentrenamiento mensual. Bloque añadido: ventanas de corte 3/5/7/14 días, promedios, sumas, conteos, dispersión, media exponencial, tendencias y días desde corte, además de variables climáticas diarias; todas anteriores al origen. No atribuir el cambio exclusivamente al corte diario ni a una ventana aislada.

Comparación inicial del 14 sobre 15.838 casos: Sistema_anterior 20,3561 % WAPE; Sistema_diario 20,0336 %; Ajuste_relativo_diario 20,6803 %; ingeniero 19,7356 %. Mejora del sistema aditivo de aproximadamente 0,32 puntos; aún no supera al ingeniero en conjunto. El relativo aprende log(1+y) − log(1+media4), no una simple corrección aditiva en tallos. Explicar que es una alternativa de cambios proporcionales, no otro algoritmo. La variante MAE posterior se tratará aparte: cambia pérdida y combinación de rutas y es exploratoria tras inspeccionar resultados. Esta primera tabla no es el inventario completo del 14 ni la selección vigente del 19.

## Variables exactas añadidas al segundo sistema del notebook 14

Verificadas en features_diarias.parquet y en la función construir_features_diarias de diario 01: **28 columnas nuevas = 19 de producción/reporte + 9 climáticas**. Por cada ventana 3, 5, 7 y 14 días: corte_media_{w}d, corte_suma_{w}d y corte_dias_{w}d (12). Además corte_std_7d, corte_lag1d, corte_lag7d, corte_ema_5d, corte_tendencia_3d, corte_tendencia_5d y dias_desde_corte (7). Clima: temperatura/humedad/radiacion_media_3d/5d/7d (9).

Precisiones para documentación: medias y sumas usan valores observados de la ventana (min_periods=1), con conteos explícitos; no sustituyen automáticamente faltantes por cero. corte_dias cuenta días con valor no nulo, incluidos ceros reportados; no necesariamente días con corte positivo. dias_desde_corte mide días desde el último dato no nulo, no desde el último corte estrictamente positivo. Tendencia3 = promedio días −1 a −3 menos promedio días −4 a −6; tendencia5 = promedio días −1 a −5 menos promedio días −6 a −10. EMA span5 da mayor peso a lo reciente, pero no trunca exactamente a cinco días. Todas las señales excluyen el día de origen. El sistema mantiene boosting y dos rutas; no debe describirse como un nuevo algoritmo ni atribuir toda la mejora a una ventana aislada.

## Continuación: del bloque diario a la separación de horizontes (15)

Antes del 15, el 14 ensayó boosting con pérdida absoluta y una ruta conjunta sobre Media4: WAPE 20,0312 % vs. 20,0336 % del sistema diario, prácticamente empate; no una mejora grande ni experimento puro de pérdida porque cambia también rutas.

El 15 mantiene HistGradientBoostingRegressor y prueba: Separado (ajustes distintos para H1–H2 y H3–H5, conservando teoría/respaldo en cada grupo); Memoria_larga (lo anterior + media12, desv8/12, reportes4/8/12 y tendencia4_12, siete columnas); Revisiones (lo anterior + tres columnas de historia teórica en ambas rutas); Combinacion (mezcla de Revisiones con referencia simple, pesos elegidos en noviembre–diciembre 2025). Los pesos elegidos fueron 1 para modelo en ambos grupos: Combinacion coincide con Revisiones.

Resultados ejecutados actuales del 15, mismos 15.838 casos: Sistema_diario 20,0336 %, Separado 19,6717 %, Memoria_larga 19,5682 %, Revisiones/Combinacion 19,6158 %, ingeniero 19,7356 %. Menor WAPE retrospectivo Memoria_larga, ventaja aproximada 0,17 puntos sobre ingeniero; no garantiza superioridad estable ni en cada horizonte. Comparación Antes_calidad ya no aísla calidad porque conserva clima histórico mientras los actuales se recalcularon. Mantener distinción con selección final posterior del 19.

## Presentación prevista: cuatro bloques

1. **Contexto.** Necesidad de anticipar tallos por producto/color/variedad en GAITANA, fuentes y alcance. Diferenciar plantas, rendimiento por planta, tallos reportados y estimado exportable. Definir origen, objetivo y H1–H5.
2. **EDA y descubrimientos metodológicos.** Calidad y homologación central de variedades; pilotos, camas/ciclos, ceros y faltantes; normalización corte/plantas, soporte e IQR; cohortes y cobertura; comparación de planos para objetivos comunes. Luego composición de producción, error teórico, memoria semanal/diaria y comparación climática que motiva hipótesis. Cada hallazgo debe ir acompañado de una decisión y su limitación.
3. **Modelos: qué es cada uno y por qué se probó.** Referencias simples, Ridge y boosting; aprendizaje de correcciones y dos rutas; memoria productiva frente a historia de planos; columnas añadidas/retiradas; 12 → benchmark13 → información diaria14 → grupos de horizontes y memoria15 → clima19. Separar train, validación y evaluación temporal, poblaciones y signos de sesgo. Mostrar resultados con una descripción al lado del nombre, y diagnóstico del error por producto/color/variedad.
4. **Pasos siguientes.** Los cuadernos 21–25 ya compararon modelos por horizonte, especialización por producto y n−1 sobre los mismos casos. La evaluación reciente favorece claramente H1, deja H2 prácticamente empatado y mantiene ventaja del ingeniero en H3–H5 y el total. El siguiente paso es probar la configuración en semanas futuras completas y seguir mejorando H3–H5; no vender una diferencia mínima como mejora confirmada. Verificar con el área agronómica las edades sin soporte antes de asignar cero. Pronóstico diario: profundizar EDA de calendario y faltantes, ajustar ventanas/parámetros y contrastar autonomía frente a coherencia semanal; presentarlo como desarrollo en revisión, conservando lo existente.

Este esquema queda registrado para preparar la presentación posteriormente; no se creó una presentación ni se ejecutaron aún estos experimentos.

## Implementación de la revisión autorizada

- Notebook 18: sección 1.1 de correspondencia entre seis variables semanales, nueve diarias y once ampliadas, con reglas de cobertura, modelos consumidores y preguntas. Comparación ejecutada de asociaciones sobre pares disponibles y casos comunes a 26 columnas, exportación Excel/Parquet y figura. Solo objetivos cerrados antes de 2025-07-07 y teoría completa. Se mantiene separado el análisis de desplazamiento.
- Resultado del EDA nuevo: 63,53–65,24 % de casos conservados por horizonte. H1: 4.993 casos / 142 orígenes y 91 series elegibles para señales físicas. Asociaciones H1 pequeñas; indicadores de cobertura sin variación suficiente en la muestra común, por lo que su correlación es no estimable, no cero.
- Verificación: las huellas de base_analitica_proyecciones.parquet y features_clima_ampliado.parquet son idénticas antes/después de ejecutar 18. No se cambiaron entradas ni se reentrenaron modelos para mejorar resultados durante esta revisión.
- Notebook 12: corregida la introducción desactualizada a los 1.834 casos, coberturas y WAPE de sus salidas ejecutadas. Diccionario y entradas conservados.
- Escrito: se preservaron resultados vigentes; se añadió el recorrido previo al modelo, significado de normalización, cohorte y ejemplo DINO, evidencia de EDA para rezagos/tendencias, puente climático, registro de la base, funcionamiento del boosting/Ridge, diccionario de modelos, entradas por bloque, evolución de comparaciones y cortes temporales. Anexo de 47 columnas. Las hipótesis no se presentan como validaciones causales o resultados futuros.
- Diario: se conservan secciones, tablas y notebooks; las secciones de pronóstico diario y SARIMA/SARIMAX y notebooks diarios 02–05 se marcan en revisión. Diario01 sigue siendo necesario para entradas del semanal.
- Guía: orden de lectura metodológico y orden técnico de ejecución separados. Diario01 debe preceder al EDA18 ampliado. Interpretación16 y errores20 se pueden leer/ejecutar en la ruta semanal sin tener que entrenar todos los diarios.
- Resumen y navegación: se mantiene el resultado vigente y se explicita el carácter preliminar del diario. Pendientes de curvas tempranas, disponibilidad, identidad, unidades y futura validación se conservan; no se sustituyeron desconocidos por cero.

### Cierre verificado de esta actualización

El Word se regeneró correctamente desde el Markdown: 26 tablas y 18 figuras. Se validaron los siete notebooks afectados; EDA18 tiene todas sus celdas ejecutadas sin errores. Se verificó que el código y las salidas de los modelos de 12 y diarios02–05 permanecen idénticos; solo cambió su documentación. El anexo contiene las 47 columnas. Se sincronizaron en lectura.ipynb únicamente las copias exactas del resumen y la guía anteriores, conservando sus demás celdas. Las comprobaciones no requieren repetir entrenamientos. Los experimentos futuros y la presentación quedan propuestos, no ejecutados.

## Revisión del 9 de octubre: edades tempranas y cobertura

El usuario pidió revisar rápidamente si las edades sin rendimiento correspondían a plantas que aún no debían producir y luego solicitó explícitamente un notebook separado, ejecutado y con tablas. Se creó `Notebooks/Proyecciones Teoricas Propias/02_EDA_edades_sin_cobertura.ipynb`. Es diagnóstico: no cambia ceros, curvas, proyecciones ni modelos. Lee ediciones 2021–2026 y verifica causas contra los casos de la base analítica.

Evidencia previa a ejecutar el resumen: en la ventana de DINO anterior al plano 2026-07-13 hay un positivo a edad 14 (288 tallos, 1.330 plantas, referencia dino-16-175, corte 2026-02-23, siembra 2025-11-18, fila estadística 234608). Edad original y calculada coinciden. Ese piloto solo aporta una observación en la ventana: requiere contraste antes de considerarlo una pauta general. Otro piloto registra ceros a 20 y 21 semanas. Las edades 9 y 16 no tienen puntos en la curva utilizada. No corresponde inferir automáticamente que ambas sean ceros: 9 es anterior al rango observado; 16 es un hueco posterior a un positivo observado. Tampoco se declara el punto de 14 erróneo sin verificación adicional.

La tabla de causas debe distinguir casos sin plano, sin pareja, teoría completa y grupos incompletos; el 78,75 % no significa fracaso de todas las uniones ni ausencia total de proyección. El diagnóstico de edades tempranas es una candidatura a revisión, no una corrección agronómica autorizada por sí sola.

### Recuento histórico verificado en la base (9 de octubre; reemplazado por la revisión del 19 de octubre)

Sobre los mismos 211.001 casos con y observado: teoría completa 44.848 (21,25 %); solo edades tempranas por verificar 33.047 (15,66 %); solo huecos interiores 18.172 (8,61 %); solo edades posteriores al rango 29.478 (13,97 %); mezcla de edades sin soporte 34.935 (16,56 %); otros estados o combinaciones 44.024 (20,86 %); sin pareja comercial/objetivo 5.523 (2,62 %); sin plano disponible 974 (0,46 %). Las categorías de casos son excluyentes y suman el total. Los 159.656 casos de teoría incompleta coinciden exactamente con el número de grupos faltantes reconstruido desde las proyecciones originales.

Los 33.047 casos tempranos representan 20,70 % de los incompletos y son candidatos a revisar, no producción cero confirmada. La clasificación depende del soporte de cada curva a la fecha del plano; no equivale a etapa fisiológica certificada. Para DINO no aparecen filas a edades 9/16 ni en la ventana utilizable, ni en la auditoría de esa ventana, ni en todo el pasado utilizable de la edición 2026. No es un cero observado eliminado durante la limpieza. La observación aislada positiva a 14 y los ceros a 20/21 exigen revisión de pilotos; no validan rellenar ambos grupos automáticamente. Mantener esta precisión al explicar la cobertura en la presentación.


## Revisión de cruces y regeneración de resultados — 19 de octubre de 2026

El usuario pidió comprobar los cruces entre camas piloto y estadísticas, corregir el vocabulario de cobertura y regenerar la cadena. La curva representa productividad por edad; cada plano calcula esa edad desde la siembra hasta la semana objetivo.

- Se normalizaron mayúsculas, espacios y etiquetas homologadas al comparar candidatas. Las copias equivalentes del mismo ciclo dejaron de generar ambigüedad. La identidad de variedad ausente se recupera sólo si la referencia completa en el mismo libro identifica una combinación comercial única compatible con el producto. No se sumaron ni borraron movimientos de corte.
- Cortes fechados en 2026: 32.986 de 33.039 estadísticas con correspondencia única (99,84 %). Quedan 52 estadísticas ambiguas y una identidad incompleta; sus referencias están en `revision_cruces_20261019/referencias_pendientes_cortes_2026.csv`.
- La edad coincide con fechas de siembra y corte en 477.426 estadísticas utilizables y con siembra y objetivo en 1.064.620 filas de proyección de 2026.
- Base analítica: 46.051 de 211.001 casos con producción real observada (21,83 %) permiten aplicar la curva a todas las edades de sus cohortes, frente a 44.848 (21,25 %) antes de la revisión. Es serie–origen–horizonte; no es tasa de cruce ni porcentaje de datos conservados. En los demás casos, la referencia directa de curva no aplica a todas las cohortes; la producción real permanece y el sistema usa producción reciente como ruta de respaldo cuando el caso es admisible.
- Se ejecutaron las 20 etapas: auditoría, proyecciones 2021–2026, procedencia, base/EDA, modelos semanales, benchmark, clima, error por producto/color/variedad y diarios. Los estados terminaron completos. Se mantuvieron ceros registrados, edades por fecha y ventana de 78 semanas.
- WAPE semanal seleccionado: 19,33 % frente a 19,74 % del ingeniero en 15.838 casos; sesgo −2,59 % frente a −9,75 %. H1: 15,66 % frente a 17,09 %; sesgo −1,34 % frente a −7,56 %. Diario reconciliado: 27,26 %; autónomo: 26,72 %, en 22.973 días reportados. Diario sigue en revisión.
- El ejemplo DINO conserva edades sin rendimiento. Edad 9 está antes del rango observado y 16 es un hueco; primera positiva observada: 14. No se rellenan automáticamente con cero.
- Se regeneraron escrito, Word v4, guía, metodología, resumen de modelos y esta bitácora. El Word contiene 34 tablas y 18 figuras. Los conteos del 9 de octubre quedan identificados como históricos.

### Aclaración de vocabulario y diagrama — 19 de octubre de 2026

El 21,83 % se calcula **en la base analítica final** sobre casos con producción real observada. Significa que la curva empírica representa las edades de todas las cohortes del plano en esos casos y, por eso, puede calcularse un total teórico directo. No significa que solo se haya cruzado ese porcentaje, que el resto de la producción real se haya perdido o que esos casos queden sin pronóstico. El cruce se mide aparte: 99,84 % de las estadísticas fechadas en 2026 tienen correspondencia única.

El notebook 11 incorpora un diagrama de las dos rutas. Ejemplo: si un plano tiene dos cohortes y la curva representa la edad de una, pero no la de la otra, no se usa la suma parcial como total del plano; se conserva la fila real y el pronóstico admisible pasa a producción reciente. Es normal que una curva construida con observaciones piloto no represente todas las edades de todas las variedades. El EDA de edades describe ese alcance empírico; no diagnostica pérdida de filas de producción. Las etiquetas técnicas `curva_completa` y `sin_cobertura` se conservan por compatibilidad, pero se explican como aplicabilidad de curva a todas las cohortes.

## Comparación reciente por horizonte y actualización del informe — 21 de octubre de 2026

Se integraron los resultados de los cuadernos 21–25 en el resumen, la guía, la metodología y el trabajo escrito. La evaluación reciente comprende 1.226 casos de GAITANA en tres semanas objetivo y se presenta aparte de la evaluación anual para no mezclar periodos.

- H1: el candidato obtiene 12,28 % WAPE frente a 15,23 % del ingeniero; ventaja clara de 2,95 puntos.
- H2: 14,96 % frente a 14,98 %; diferencia de 0,02 puntos, descrita como empate práctico y pendiente de confirmación con más semanas.
- Total: 17,53 % frente a 16,34 %; el ingeniero conserva ventaja. También gana en H3–H5.
- El cuaderno 25 mejora el WAPE total del candidato propio previo (17,80 %) a 17,53 %, pero no demuestra que ya reemplacemos al ingeniero globalmente. La comparación del ingeniero es benchmark; no es entrada del modelo.
- La cobertura se resume en lenguaje directo: la producción real permanece en la base; la curva es una referencia directa cuando representa todas las edades del plano, y la producción reciente puede respaldar los casos admisibles restantes. No equivale a producción faltante ni a un cruce fallido.
- Se regenerará el Word desde el Markdown actualizado y se publicarán los documentos y notebooks de esta revisión.


### Plataforma: cierre de carga e histórico separado (26/10/2026)

Se activó en SQL Server `Proyectos`, esquema `EP`, la carga consolidada con WebFlor: 6.543.848 registros reales y último corte 24/10/2026. Se generó un borrador Sin_clima para S44, con 565 líneas y 113 series, sin publicarlo. La comprobación de las cinco fuentes, conservación de tallos y versiones quedó aprobada en `plataforma_gaitana/storage/verification_operational.json`.

Para estudiar errores, abrir **Histórico y desempeño → Qué resultados revisar**: entrenamiento (sólo diagnóstico H1), validación 2025, prueba 2026 o seguimiento de nuevas semanas. Cada opción muestra semanas, WAPE y sesgo comparables del modelo y del ingeniero. Entrenamiento no demuestra anticipación. El seguimiento se amplía al llegar producción real de semanas terminadas y publicaciones previas al origen; no incorpora borradores ni simulaciones retrospectivas como si fueran nuevas pruebas. Consultar [estado y límites](plataforma_gaitana/ESTADO_PROTOTIPO.md).


### Comparador de errores separado del panorama general (26/10/2026)

La plataforma ahora tiene cuatro secciones: Histórico y desempeño, Comparador de errores, Generar y ajustar, Metodología y guía. Para revisar un problema: abrir **Comparador de errores**, escoger evaluación y horizonte, elegir una semana o un grupo, filtrar producto/color/variedad y revisar los mayores aportes al error del modelo o del ingeniero. Pulsar un grupo lleva al siguiente detalle; por variedad se puede bajar a sus semanas. El botón **Explorar errores** del histórico conserva la evaluación y el horizonte elegidos.

El comparador muestra WAPE, sesgo, tallos reales/estimados, error absoluto y aporte de cada grupo; mantiene los mismos casos para ambos métodos. Los errores se calculan por caso antes de agrupar, sin cancelar diferencias opuestas ni promediar porcentajes. Se verificó que el desglose reproduce el panel original. La búsqueda afecta sólo la tabla; los filtros superiores sí actualizan toda la vista. La primera sección queda como resumen. Comprobación: 27 pruebas aprobadas y revisión de filtros/navegación en escritorio y móvil; evidencia local `plataforma_gaitana/storage/verification_comparison.json`.


### Recepción ágil y selección múltiple de planos (26/10/2026)

Se corrigió un bloqueo al abrir Excel grandes durante la recepción: la inspección inicial ahora lee sólo el índice XML y se ejecuta fuera del bucle HTTP, conservando la limpieza completa en el trabajador ETL. La ventana muestra porcentaje de envío, confirmación por archivo, errores y reintento; Planos permite seleccionar varios archivos del mismo año. Un error individual no detiene los demás. Guardar confirma recepción; **Procesar archivos** incorpora y activa los datos después de las validaciones.

El clima hasta S42 y el plano S42 del usuario ya estaban recibidos, pendientes del ETL: no deben subirse otra vez. Prueba de recepción/reconocimiento de archivos existentes sin duplicarlos: dos planos 4,927 s; estimado 3,097 s; clima de 196 MB 5,625 s. Estos tiempos no son los de la limpieza completa. La API siguió respondiendo. Se aprobaron 29 pruebas y se verificaron carga múltiple, error individual y navegación móvil. Evidencia privada: `plataforma_gaitana/storage/verification_upload_fix.json`.


### Revisión académica de la tesis según el profesor — 28/10/2026

Nueva versión: `Trabajo escrito/Documento_LaGaitana_v7_revision_profesor_20261028.docx`, con PDF y Markdown propios. Se conserva la versión 6 y su texto base. La revisión transcribe OG y los cuatro objetivos específicos del Plan de proyecto original y los vincula con conclusiones e implicaciones para La Gaitana; distingue logros, avances parciales y validaciones pendientes. Hace explícitos supuestos, decisiones y limitaciones dentro de cada etapa y mejora transiciones entre contexto, método, resultados e implicaciones.

Las métricas se recalcularon desde predicciones archivadas, sin reentrenar: MAE, RMSE, WAPE, sesgo medio y porcentual, con saldo neto en el archivo de auditoría. Se preservan panel histórico de 15.838, anual nominal de 16.325 y reciente de 1.226 casos. El EDA textual por producto/color/variedad se sincronizó con el anual corregido. Se incorporan MAPE y porcentaje dentro de ±8 % en evaluaciones con predicciones individuales; su ausencia en algunos agregados train queda marcada. Se identifican límites antes poco visibles: ingeniero emitido el jueves frente a variables del lunes, muestra máxima de 5.000 filas por ajuste reciente, H1 reciente evaluado en una sola semana y LSTM de un día adelante frente a emisión de siete días. No se atribuyen beneficios económicos ni validaciones prospectivas no realizados.

La revisión conserva 19 figuras numeradas y registra 122 resúmenes de métricas, 14 pendientes y huellas de sus fuentes en `Trabajo escrito/Revision_v7/`. El Word se abrió en una instancia oculta e independiente para paginar y exportar PDF: 74 páginas y 47 tablas. La guía para esta versión y los scripts de reconstrucción están en `Trabajo escrito/LEEME.md`.


### 28/10/2026 — Comparador por semanas y selección de H1 en la plataforma

Se revisó el benchmark de los notebooks `03_benchmark_estimado_ingeniero.ipynb` y `3_Benchmark estimado ingeniero.ipynb`, en `Notebooks/Limpieza data, Notebooks y Scripts/coso para generar el html antes`. Se recuperó su exploración con filtros compartidos por semana, producto, color y variedad y la descarga de tablas; se mantiene la identidad visual corporativa. El comparador permite semanas sueltas no consecutivas, rangos, todas y últimas 1/4/8; navegación de regreso por niveles; cantidades, WAPE, sesgo, contribución al error y vista de diferencias netas. La exportación CSV incluye todas las filas de la tabla filtrada, no sólo la página visible.

El histórico distingue mediante botones y texto entrenamiento, validación, prueba y seguimiento. Entrenamiento es un diagnóstico dentro de muestra H1, no una nueva validación. La prueba archivada no crece al cargar nuevos archivos; las publicaciones nuevas se evalúan en seguimiento cuando cumplen el corte temporal.

En Generar y ajustar se elige H1. La consulta de fuentes y el POST de generación usan exactamente ese origen; se verifica la presencia de la edición de plano/ingeniero de esa semana. Elegir una semana sin variables preparadas no desplaza automáticamente variables ni permite pronosticar: hay que actualizar y procesar insumos. Los orígenes pasados se señalan como simulaciones retrospectivas. La ausencia de plano mantiene la ruta de memoria validada; clima e ingeniero siguen siendo opcionales para Sin_clima. Los pendientes obligatorios de procesamiento conservan su bloqueo.

Verificación: compilación del frontend, pruebas del backend y recorrido real en Edge, sin errores JavaScript y sin desbordamiento móvil. H1 de prueba conserva 3.512 casos, WAPE 15,52646 % y sesgo −1,34110 % del modelo. Se comprobó selección de dos semanas no consecutivas, filtros por color/variedad, rangos, CSV y bloqueo de H1 futura. Evidencia local ignorada por Git: `plataforma_gaitana/storage/verification_comparator_weeks_h1.json`. No se reentrenaron modelos, procesaron nuevas cargas ni publicaron pronósticos durante esta mejora de interfaz.


### 28/10/2026 — WebFlor con ventana de reemplazo y carga múltiple

Se reemplazó la regla de sólo añadir fechas posteriores por una reconsulta de la ventana retenida (45 días hasta ayer) y sustitución versionada del rango. Las diferencias en días ya guardados se auditan y se incorporan; el histórico anterior se conserva. No se deduplican movimientos por valores. La precedencia entre archivos se aplica antes de la limpieza 05 y se conserva en el manifiesto para reproducir el ETL. Un fallo de validación no activa cambios; las versiones SQL anteriores permanecen consultables. Se comprobaron el contrato temporal real de WebFlor y disponibilidad de datos hasta el 27/10/2026 mediante lectura, sin declarar activada esa descarga de comprobación.

Se retiró el bloqueo del botón por pendientes de clima/planos/estimados. Se mantiene el control de trabajos concurrentes y de un completo de producción pendiente. La carga múltiple se extendió a estimados, estadísticas de distintas familias y adicionales de clima/producción; permite agregar archivos en varias selecciones y quitar pendientes. No se admiten varios completos del mismo alcance ni adicionales con fechas cruzadas.

La revisión semanal solapa las ventanas y protege el empalme con nuestra base persistida. La retención de la fuente no borra el histórico guardado. Sólo una interrupción que deje un tramo fuera de retención exige recuperarlo por Excel. Estos cambios son de ingestión y operación; no alteran las variables ni parámetros estadísticos del modelo 19.

Verificación final de esta mejora: 41 pruebas del backend aprobadas, compilación del frontend y recorrido en Edge sin errores JavaScript ni desbordamiento móvil. Se verificaron selección múltiple en las cinco fuentes según modalidad, agregado en selecciones sucesivas, retiro de pendientes y botón WebFlor habilitado pese a clima y plano pendientes. Evidencia: `plataforma_gaitana/storage/verification_multi_upload_webflor_ui.json`. La descarga de comprobación fue de sólo lectura; no creó un trabajo ni activó una nueva base operativa.

## Actualización del 28/10/2026: evaluación temporal y operación

Lectura corta: informe v8, 4.2.8 (train/validación/test y reentrenamiento), 5.1.3 (datos y resultados nuevos), 5.5 (train/test del mismo ajuste) y conclusiones por objetivo. Los demás modelos y el diario conservan sus resultados históricos, identificados como tales.

Reproducción de esta actualización:
1. Conservar la copia versionada `plataforma_gaitana/storage/datasets/evaluacion_local_20261028` y su manifiesto; no cambiar originales para repetir resultados.
2. Ejecutar `26_validacion_temporal_actualizada_y_operacion.ipynb` de arriba abajo con el entorno de `plataforma_gaitana/.venv`. Reutiliza las funciones del 19 y no requiere consultar SQL ni WebFlor para calcular los errores.
3. Revisar `fuentes_validadas.csv`, `cortes_entrenamiento.csv`, `particiones_por_corte.csv`, `train_test_por_ajuste.csv`, `auditoria_semanas.csv` y `verificacion_final.json`.
4. Para regenerar el informe: `actualizar_documento_v8.py`, `generar_documento_v8.py`, `verificar_revision_v8.py` y `exportar_revision_v8_pdf.py`, en ese orden. Los tres últimos usan `entorno_tesis` (Word se abre oculto para exportar PDF).

En el visualizador, «Evaluación actualizada · cuaderno 26» conserva las predicciones y recalcula errores contra la última versión validada de real/ingeniero. «Prueba 2026 · cuadernillo 19» mantiene el archivo de referencia. «Entrenamiento» muestra H1 dentro de muestra y «Seguimiento» exige publicaciones anticipadas. Cargar más datos no inventa predicciones para orígenes no evaluados: para ampliarlos se vuelve a ejecutar la evaluación o se conservan nuevas publicaciones.

El comparador identifica con color quién tuvo menor WAPE y permite regresar de variedad a color y producto. La revisión manual de una propuesta conserva por separado el error original y ajustado; no modifica el benchmark nominal del ingeniero.

En «Generar y ajustar», producto → color → variedades permite comparar varias selecciones, cambiar semanas y ocultar curvas. El checklist se guarda en la propuesta: seleccionar no confirma revisión. Marcar revisada registra aceptación o ajuste de las cinco semanas; cambiar cantidades vuelve a dejar pendientes las variedades afectadas. El avance por producto/color sólo se completa al revisar todas sus variedades. La curva por edad utiliza el resultado normalizado existente; el suavizado de la proyección absoluta es únicamente visual.
