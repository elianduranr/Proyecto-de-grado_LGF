# Guía paso a paso: calidad, proyecciones y pronóstico

## Qué estudiar primero

Lee el [trabajo escrito desarrollado](Trabajo%20escrito/Estructura_actualizada_con_resultados.docx), especialmente el capítulo 3 (entendimiento y EDA), el 4 (decisiones de modelado) y el 5 (resultados). El [texto editable](Trabajo%20escrito/Desarrollo_del_documento.md) contiene la misma redacción. Después revisa los notebooks en el orden siguiente. Conservan tablas y figuras ejecutadas; no es necesario reentrenarlos para estudiarlos.

## Resultado vigente de la revisión del 6 de octubre

Se corrigieron dos pérdidas de información: copias equivalentes de pilotos tratadas como candidatas distintas y múltiples IDs del maestro que ocultaban una identidad comercial única. En la edición 2026 las observaciones utilizables pasaron de 370.172 a **444.476**; 13.963 de las recuperadas entran en alguna ventana de los planos de ese año. No sumar recuperaciones de ediciones distintas: comparten historia.

Las plantas se conservan por plano/finca/horizonte. La cobertura ponderada por exposiciones de plantas de 2026 pasó de 72,21 % a 78,80 %. La teoría completa del panel de casos pasó de **17,96 % a 21,25 %** (44.848 de 211.001 casos observados). Son denominadores distintos. Todavía faltan curvas o edades para parte del inventario; no se rellenaron con cero ni con rendimientos inventados.

El catálogo común contiene 2.915 identidades comerciales, 53 con múltiples IDs SQL. En 33 hay códigos de obtentor diferentes: quedan para revisión agronómica. La identidad comercial no certifica equivalencia genética. Se conservan colores diferentes, nombres originales y todos los códigos.

## Orden de ejecución y pregunta de cada notebook

Usa el kernel `entorno_tesis`. Los notebooks son autocontenidos: no importan módulos propios ni necesitan variables de otro kernel. Sus archivos de entrada/salida son explícitos.

0. [Catálogo común de variedades](Notebooks/Proyecciones%20Teoricas%20Propias/00_catalogo_variedades.ipynb). Construye identidades y equivalencias desde los CSV SQL, sin modificarlos. Salida central: [Catalogo_analitico](Notebooks/Extracci%C3%B3n%20SQL/Datos/01_maestros_y_geografia/Catalogo_analitico/README.md). Los cambios de regla se definen aquí; no editar distintos Parquet a mano.
1. [Auditoría de calidad](Notebooks/Proyecciones%20Teoricas%20Propias/Auditoria_calidad_curvas.ipynb). Sigue estadísticas/pilotos y planos de todas las ediciones; documenta recuperaciones, exclusiones, soporte y cobertura antes/después. Reconstruye los años afectados desde las tablas con procedencia. Conserva referencias previas para medir el efecto de calidad y comprueba que las plantas no cambien.
2. [Proyecciones de todos los años](Notebooks/Proyecciones%20Teoricas%20Propias/Proyecciones_teoricas_todos_los_anios.ipynb). Integra resultados 2021–2026, expone variedades sin curva y edades faltantes, compara cinco planos y 32–33, y exporta el insumo del modelo. `RECALCULAR_DESDE_EXCEL=False` recupera resultados auditados; usar `True` cuando cambien las fuentes. Leer la cobertura junto con cada cantidad parcial.
3. [10: base analítica](Notebooks/Analisis/10_base_analitica_proyecciones.ipynb). Integra proyecciones, producción y clima; conserva cantidades por llave; usa el catálogo compartido sin fusionar colores reportados. Define origen, objetivo, H1–H5 y disponibilidad supuesta. No recalcula curvas dentro del modelo.
4. [11: EDA](Notebooks/Analisis/11_EDA_proyecciones.ipynb). Estudia composición, cobertura, error de teoría, memoria, clima y revisiones. Las asociaciones principales usan objetivos cerrados antes del 7 de julio de 2025. No sumar producción desde la base de casos porque repite objetivos en diferentes orígenes.
5. [12: modelos de ajuste](Notebooks/Analisis/12_modelo_ajuste_proyecciones.ipynb). Compara referencias y bloques con cortes temporales. La teoría completa se corrige; en otros casos hay respaldo explícito de media4. Incluye simulación desde el último origen local.
6. [13: benchmark 2026](Notebooks/Analisis/13_comparacion_ingeniero_modelo_2026.ipynb). Reentrena mensualmente y empareja al ingeniero sobre mismas llaves, origen, objetivo y horizonte. Separa archivos posteriores, recuperaciones por color y casos sin pareja. H2–H5 son pronósticos propios del ingeniero para esas semanas, no H1 repetido.
7. [Diario 01: base y EDA](Notebooks/Modelo_de_series_diario/01_base_diaria_EDA.ipynb). Concilia 327.991.200 tallos y 44.053 llaves semanales, construye calendario diario y ventanas de corte/clima. Mantiene ausencias como faltantes y prueba que modificar el futuro no altere variables pasadas. Esta base depende de producción/clima, no de la curva; la revisión de curvas no cambia esas cantidades.
8. [14: tendencias diarias](Notebooks/Analisis/14_tendencias_diarias_modelo_semanal.ipynb). Añade 28 variables diarias y evalúa la arquitectura de referencia con datos corregidos. Su sección 6 verifica los H1–H5 del ingeniero contra la fuente limpia. Es la referencia fija del experimento diario.
9. [15: calidad y mejora por horizonte](Notebooks/Analisis/15_calidad_y_mejora_por_horizonte.ipynb). Es el análisis nuevo principal. Diagnostica dónde perdemos, separa calidad de modelado y compara: grupos H1–H2/H3–H5, memoria más larga, revisiones y combinación sencilla. Los pesos de combinación se fijan con noviembre–diciembre de 2025. Incluye sensibilidad con cinco horizontes completos, intervalos exploratorios y explicación de resultados.
10. [Diario 02: distribución semanal a diaria](Notebooks/Modelo_de_series_diario/02_distribucion_semanal_a_diaria.ipynb). Contrasta reparto uniforme, perfil histórico, boosting autónomo y reconciliado. Los repartos suman exactamente al sistema semanal de 14, actualizado por calidad. Conserva ese experimento como referencia; diario 04 mide separadamente el cambio al candidato de 15.
11. [Diario 03: SARIMA/SARIMAX](Notebooks/Modelo_de_series_diario/03_SARIMA_SARIMAX_y_boosting.ipynb). Piloto de tres series seleccionadas por volumen de 2025, clima lag7 conocido al origen, convergencia explícita y evaluación en días comunes. No generalizar su resultado a toda la finca. Dependencia instalada: `statsmodels==0.15.0`.

12. [Diario 04: nuevo total semanal](Notebooks/Modelo_de_series_diario/04_diario_con_memoria_semanal.ipynb). Mantiene los pesos diarios de 02, cambia sólo el total por Memoria_larga de 15 y compara días comunes, semanas completas, panel estricto e intervalos; actualiza también la reconciliación del piloto 03.
13. [16: interpretación semanal](Notebooks/Analisis/16_interpretacion_modelo_semanal.ipynb). Reconstruye el ajuste de agosto, verifica sus predicciones y grafica importancia por permutación de bloques y variables. No es SHAP ni causalidad.
14. [17: inventario y train/test](Notebooks/Analisis/17_inventario_modelos_train_test.ipynb). Reconstruye los últimos ajustes, contrasta sus predicciones con las guardadas y mide train y test del mismo corte. Mantiene aparte la evaluación acumulada de cada experimento.

Si se parte de fuentes Excel nuevas, ejecutar 00 → todos los años con recálculo → auditoría → todos los años con recuperación → cadena analítica. Con los resultados actuales, seguir el orden anterior. Los históricos de auditoría describen esta revisión; antes de iniciar otra revisión metodológica conservar su referencia de manera explícita.

## Qué aportó cada experimento

| Etapa | WAPE conjunto | Lectura |
| --- | ---: | --- |
| Sistema diario antes de calidad | 20,04 % | Referencia preservada |
| Misma arquitectura, calidad corregida | 20,06 % | Recuperar datos no mejoró automáticamente el error |
| Modelos separados por grupos de horizonte | 19,68 % | Principal mejora de arquitectura |
| Separación y memoria más larga | **19,59 %** | Menor WAPE retrospectivo entre candidatos corregidos |
| Añadir revisiones | 19,65 % | No supera a memoria larga |
| Combinación sencilla | 19,65 % | Validación previa eligió 100 % modelo; no aporta mezcla |
| Ingeniero | **19,74 %** | Referencia sobre los mismos casos |

Las medias de 4/8 semanas y producción de un año antes ya existían. La extensión añade media12, dispersión8/12, tendencia4/12 y conteos de observaciones. No se presentan variables existentes como novedades.

## Comparación H1–H5 del candidato con memoria larga

| Horizonte | Casos | Ingeniero | Modelo con memoria larga |
| --- | ---: | ---: | ---: |
| H1 | 3,413 | 17,09 % | 15,68 % |
| H2 | 3,289 | 19,28 % | 17,56 % |
| H3 | 3,166 | 20,32 % | 20,39 % |
| H4 | 3,045 | 20,91 % | 22,14 % |
| H5 | 2,925 | 21,40 % | 22,77 % |
| Conjunto | 15.838 | 19,74 % | 19,59 % |

El candidato tiene **0,15 puntos menos WAPE** y menor MAE que el ingeniero en esta muestra. H1/H2 mejoran, H3 está cerca y H4/H5 siguen por detrás. El RMSE todavía favorece al ingeniero: aproximadamente 4.404 frente a 4.507 tallos. No afirmar superioridad en todas las métricas ni todos los horizontes.

El intervalo exploratorio de la ventaja de memoria larga frente al experto va de −1,16 a +1,48 puntos: incluye cero. Frente al sistema anterior a calidad, la mejora es 0,45 puntos, con intervalo +0,17 a +0,67. Al exigir cinco horizontes completos quedan 14.585 casos: 19,88 % frente a 20,02 % del ingeniero. Son verificaciones retrospectivas, no una prueba prospectiva intacta ni una autorización de reemplazo operativo.

En el diagnóstico de la arquitectura corregida, clavel/miniclavel y variedades como LORENZO y EPSILON concentran dificultades largas. La mayor parte de la desventaja está en el respaldo. Sólo 9,10 % de los casos principales de 2026 utiliza teoría completa; el 21,25 % global incluye otros años. Revisar ambos denominadores antes de sacar conclusiones.

## Salidas para estudiar y actualizar el escrito

- [Auditoría de calidad](Notebooks/Proyecciones%20Teoricas%20Propias/resultados_todos_los_anios/auditoria_calidad/auditoria_calidad_curvas.xlsx): recuperación, exclusiones, soporte, nombres y prioridades. El Parquet `cobertura_por_plano_variedad_horizonte` conserva el detalle completo.
- [Experimentos y diagnóstico](Datos_analiticos_proyecto/modelo_con_proyecciones_teoricas/resultados_experimentos_horizontes.xlsx): métricas por horizonte, ruta, producto, variedad y mes; pesos previos a 2026; cortes temporales e incertidumbre. `experimentos_horizontes_2026.parquet` conserva cada caso.
- [Verificación de origen del ingeniero](Datos_analiticos_proyecto/modelo_con_proyecciones_teoricas/comparacion_H1_H5_verificada.xlsx): cantidades y archivos de la referencia 14, no del nuevo candidato 15.
- [Trabajo escrito](Trabajo%20escrito/LEEME.md): contexto, curvas, EDA, calidad, decisiones, resultados y discusión. `actualizar_word.py` reconstruye el Word desde su Markdown; no recalcula modelos. Los gráficos y cifras deben actualizarse desde los resultados al cambiar datos.

La producción real, clima y estimados limpios siguen siendo fuentes oficiales. GAITANA y GAITANA PPTO no se mezclan. Las proyecciones parciales, los objetivos ausentes y los días sin reporte no se convierten en cero. No se consulta SQL ni se modifican Excel/CSV originales. El notebook original de proyecciones queda como referencia pedagógica anterior; la ejecución vigente es la de todos los años con auditoría. Las extracciones originales y la investigación SQL no son otra cadena que debas estudiar para reproducir estos modelos.

## Siguiente validación

Memoria_larga queda como candidato, no como ganador operativo certificado. Fijar sus parámetros antes de un periodo nuevo, archivar la emisión real y evaluar H1–H5 sobre casos comunes. Los periodos de 2026 ya se examinaron: no llamarlos test intacto. Confirmar tallos reportados frente a exportables, latencia de producción/clima y publicación de archivos. Revisar identidades con obtentor discrepante y edades con poco soporte antes de proponer nuevas equivalencias o interpolaciones. Literatura académica verificada, PCA/MCA/PDN y validación empresarial permanecen pendientes según su utilidad para el proyecto.

## Orden exacto para correr y reproducir los resultados actuales

Trabajar desde esta carpeta de proyecto, con el entorno `entorno_tesis` y las fuentes locales que ya acompañan al proyecto. Abrir cada notebook, seleccionar ese intérprete, reiniciar su kernel y ejecutar **todas las celdas de arriba abajo**. Esperar a que termine sin celdas de error antes de pasar al siguiente; no basta ejecutar sólo la celda del gráfico. Se leen archivos entre etapas, no variables de otro notebook.

1. `Notebooks/Proyecciones Teoricas Propias/00_catalogo_variedades.ipynb` → catálogo común.
2. `Notebooks/Proyecciones Teoricas Propias/Auditoria_calidad_curvas.ipynb` → calidad, recuperación y conservación.
3. `Notebooks/Proyecciones Teoricas Propias/Proyecciones_teoricas_todos_los_anios.ipynb`, con `RECALCULAR_DESDE_EXCEL=False` → proyecciones auditadas y exportación integrada.
4. `Notebooks/Analisis/10_base_analitica_proyecciones.ipynb` → base semanal con producción/clima.
5. `Notebooks/Analisis/11_EDA_proyecciones.ipynb` → EDA.
6. `Notebooks/Analisis/12_modelo_ajuste_proyecciones.ipynb` → modelos iniciales y ablaciones.
7. `Notebooks/Analisis/13_comparacion_ingeniero_modelo_2026.ipynb` → casos emparejados del ingeniero.
8. `Notebooks/Modelo_de_series_diario/01_base_diaria_EDA.ipynb` → calendario, EDA y variables diarias.
9. `Notebooks/Analisis/14_tendencias_diarias_modelo_semanal.ipynb` → sistema semanal con señales diarias y variantes.
10. `Notebooks/Analisis/15_calidad_y_mejora_por_horizonte.ipynb` → candidato Memoria_larga y comparaciones H1–H5.
11. `Notebooks/Modelo_de_series_diario/02_distribucion_semanal_a_diaria.ipynb` → reparto de referencia y boosting autónomo.
12. `Notebooks/Modelo_de_series_diario/03_SARIMA_SARIMAX_y_boosting.ipynb` → piloto de tres series y convergencia.
13. `Notebooks/Modelo_de_series_diario/04_diario_con_memoria_semanal.ipynb` → nuevo reparto y sensibilidad del piloto.
14. `Notebooks/Analisis/16_interpretacion_modelo_semanal.ipynb` → gráficos de importancia del candidato semanal.
15. `Notebooks/Analisis/17_inventario_modelos_train_test.ipynb` → inventario completo y comparación train/test por corte.

Esta secuencia reproduce la revisión usando las tablas y fuentes conservadas. **Desde Excel nuevos**, después de 00 se debe ejecutar primero el notebook de todos los años con `RECALCULAR_DESDE_EXCEL=True`, luego auditoría, luego todos los años con `False`, y continuar desde 10. Las referencias anteriores a la corrección de calidad son evidencia preservada; no se recrean borrándolas ni se sustituyen por los resultados nuevos. Las bases limpias de producción, clima y estimados deben existir antes de 10; esta secuencia no consulta SQL ni vuelve a descargar fuentes.

Si sólo quieres reproducir lo añadido en esta revisión y no cambió ninguna fuente ni predicción anterior, basta **diario 04 → semanal 16 → semanal 17**. Las entradas 02, 03 y 15 ya deben estar ejecutadas. Los notebooks nuevos generan sus gráficos y Excel. No se instaló SHAP ni se requiere otra dependencia nueva.

Después de verificar cifras y actualizar su interpretación en `Trabajo escrito/Desarrollo_del_documento.md`, regenerar el Word desde la raíz con:

```powershell
.\entorno_tesis\Scripts\python.exe "Trabajo escrito/actualizar_word.py"
```

El comando sincroniza texto, tablas e imágenes con el Word; no recalcula modelos ni reescribe automáticamente conclusiones cuando cambian los datos. Los notebooks conservan las salidas ejecutadas para estudiar sin volver a entrenar.

## Resultado diario vigente e interpretación

Sobre 22.973 días observados, el WAPE del boosting reconciliado pasa de **28,29 % a 27,45 %** usando Memoria_larga semanal. El autónomo mantiene **26,76 %** y no conserva obligatoriamente el total semanal. El perfil con memoria obtiene **27,87 %** y el uniforme **29,03 %**. El intervalo exploratorio de la mejora reconciliada es 0,38–1,27 puntos.

No ocultar la sensibilidad: en sólo 274 semanas con siete reportes, uniforme obtiene **24,52 %**, autónomo **24,73 %** y boosting reconciliado **33,77 %**. La completitud futura no puede usarse para escoger método al emitir. En las tres series del piloto, SARIMAX autónomo conserva **24,49 %**, y reconciliado al nuevo total obtiene **30,97 %** sobre los mismos 135 días.

Los gráficos de 16 muestran dependencia predictiva, no tallos aportados ni causalidad. En respaldo domina media4 y su bloque de historia semanal; en teoría completa, la referencia teórica y su desvío. Las señales de corte diario aportan, especialmente en horizontes cercanos. La fotografía es agosto, con 1.560 casos principales, y no todo 2026. La ruta teórica sólo tiene 79/47 casos por grupo de horizontes.

## Cómo leer train y test sin mezclar periodos

En [17](Notebooks/Analisis/17_inventario_modelos_train_test.ipynb) y [el Excel del inventario](Datos_analiticos_proyecto/modelo_con_proyecciones_teoricas/inventario_modelos_train_test.xlsx), `Train_test_cortes` compara el mismo ajuste: semanal/diario de agosto, iniciales de mayo o último piloto SARIMA. Las hojas `Test_completo_*` contienen el acumulado de la evaluación original. No restar el train de agosto al test de todo 2026 como si fueran una misma comparación.

Se evalúan referencias históricas, Ridge, boosting aditivo, corrección relativa, pérdida MAE, ablaciones de clima/memoria, separación de horizontes, memoria larga, revisiones, combinación, modelos diarios autónomos/reconciliados y SARIMA/SARIMAX. El candidato semanal es boosting con memoria larga; para diario se distingue precisión autónoma de reparto coherente. El ingeniero no tiene un train de nuestro modelo. Las reglas de reparto tampoco constituyen otro estimador ajustado.

Salidas nuevas: `modelo_diario/resultados_diarios_memoria.xlsx`, `modelo_con_proyecciones_teoricas/interpretacion_modelo_semanal.xlsx` e `inventario_modelos_train_test.xlsx`. Cada uno tiene un Parquet de apoyo y está explicado en su notebook.

En el ajuste de agosto, Memoria_larga tiene **22,00 % train / 15,31 % test**; el ingeniero, **14,89 % test**. No se gana todos los meses. En diario, autónomo: **25,90 % / 26,98 %**; reconciliado con memoria: **26,40 % / 27,14 %**. Estos pares pertenecen al mismo ajuste, mientras 19,59 % semanal y 27,45 % diario son evaluaciones acumuladas con reentrenamiento. El piloto SARIMA tiene sólo 15 días de test en su último corte: leer sus conteos y no generalizar.
