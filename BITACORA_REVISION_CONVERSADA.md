# Bitácora de la revisión conversada de la metodología

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
4. **Pasos siguientes.** Comparar cinco modelos por horizonte con los dos grupos actuales. Evaluar especialización por producto y n−1: retirar un producto del entrenamiento y comparar sobre los mismos casos de los productos restantes, no obtener una mejora artificial borrando sus errores del denominador. Fijar reglas en validación y comprobar en datos nuevos. Verificar edades tempranas sin soporte antes de asignar cero. Pronóstico diario: profundizar EDA del calendario y faltantes, ajustar ventanas/parámetros y contrastar autonomía frente a coherencia semanal; presentarlo como desarrollo en revisión, conservando lo existente.

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
