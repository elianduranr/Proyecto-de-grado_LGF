# Trabajo escrito actualizado

Edición académica vigente: **[Documento_LaGaitana_v9_revision_asesor_20261104_final.docx](Documento_LaGaitana_v9_revision_asesor_20261104_final.docx)**, con [PDF de comprobación](Documento_LaGaitana_v9_revision_asesor_20261104_final.pdf) y Markdown del mismo nombre. Implementa las indicaciones consolidadas del asesor Rafael Amaya Gomez; mantiene las cifras de la evaluación ampliada y delimita su alcance. Consultar el [registro de cumplimiento](Revision_v9/REGISTRO_CUMPLIMIENTO.md), los [pendientes concretos](Revision_v9/PENDIENTES_EQUIPO.md) y la [reproducción desde fuentes](Revision_v9/README.md).

La **versión 8** conserva la evaluación temporal ampliada previa y permanece intacta; hay además copia de su Word, PDF y Markdown en `Revision_v9/Version_inicial`. Las instrucciones de las ediciones anteriores que siguen son históricas: para regenerar la entrega vigente se utiliza `ejecutar_revision_v9.py`.

La edición anterior para revisión del profesor es **[Documento_LaGaitana_v7_revision_profesor_20261028.docx](Documento_LaGaitana_v7_revision_profesor_20261028.docx)**, con [copia PDF](Documento_LaGaitana_v7_revision_profesor_20261028.pdf) y [texto editable propio](Documento_LaGaitana_v7_revision_profesor_20261028.md). Conserva intactos el Word v6 y `Desarrollo_del_documento.md` como base de esa edición.

La v7 retoma literalmente el objetivo general y los cuatro objetivos específicos de `Plan de Proyecto/Plan de proyecto_final.docx`. Vincula cada uno con su conclusión, distinguiendo logros, avances parciales y validaciones pendientes. Explicita decisiones y limitaciones por etapa, completa MAE/RMSE/MAPE/WAPE, banda ±8 % y sesgos donde existen predicciones guardadas, y ordena las implicaciones para la organización. Distingue jueves frente al lunes, muestreo reciente y LSTM de un día adelante. No reentrena modelos. El semáforo operativo y la validación empresarial no se presentan como cumplidos; lo faltante se marca `[PENDIENTE: ...]`.

Consultar [cambios](Revision_v7/CAMBIOS_v7.md), [14 pendientes](Revision_v7/PENDIENTES_v7.md), [auditoría de métricas](Revision_v7/auditoria_metricas_v7.csv) y [fuentes/verificaciones](Revision_v7/fuentes_y_verificaciones.json). Para reconstruir sólo esta revisión desde las salidas existentes:

```powershell
.\entorno_tesis\Scripts\python.exe "Trabajo escrito/revisar_tesis_v7.py"
.\entorno_tesis\Scripts\python.exe "Trabajo escrito/generar_documento_v7.py"
# Opcional, requiere Microsoft Word instalado: comprobación de paginado y PDF.
.\entorno_tesis\Scripts\python.exe "Trabajo escrito/exportar_revision_v7_pdf.py"
```

## Referencia conservada de la versión 6

`Desarrollo_del_documento.md` es el texto de referencia de la v6, cuyo Word disponible es `Documento_LaGaitana_v6.docx`. Esa versión separa metodología semanal y diaria, explica los candidatos propios por producto y horizonte y presenta aparte el seleccionado. Los comandos siguientes son de la edición anterior; no regeneran la v7. Las tablas y diagramas son monocromos; las gráficas conservan color para distinguir series.

Seguir la guía de la raíz para ejecutar las etapas afectadas. Después, actualizar los resultados desde los archivos ejecutados y generar el Word desde la raíz:

```powershell
.\entorno_tesis\Scripts\python.exe "Trabajo escrito/actualizar_word.py"
```

Para esta revisión, la limpieza semanal ya prioriza el archivo cuyo nombre define H1; los cuadernos 13 y 20 se ejecutaron con el cruce actualizado, y las comparaciones/figuras de clima se calcularon sobre el mismo panel estricto de 16.325 casos. El script `actualizar_resultados.py` conserva supuestos de una copia anterior y no se debe usar para reconstruir esta edición. Para regenerar el resumen y el Word desde las salidas vigentes:

```powershell
.\entorno_tesis\Scripts\python.exe "Trabajo escrito/actualizar_resumen_octubre.py"
.\entorno_tesis\Scripts\python.exe "Trabajo escrito/actualizar_word.py"
```

Los gráficos del panel corregido se regeneran con `regenerar_figuras_benchmark_corregido.py`; los dos diagramas se generan con `generar_diagramas_metodologia.py`. Estos pasos no entrenan modelos. Los resultados son retrospectivos y requieren validación empresarial y revisión bibliográfica.

La sección 5.6 y la evidencia E18 añaden el origen del error por producto, color y variedad, con concentración temporal y ejemplos de H1. Son diagnósticos del test ya observado, no cambios al modelo.

El benchmark anual vigente usa 16.325 emparejamientos estrictos: WAPE 19,36 % para el modelo y 19,71 % para el ingeniero. H1–H2 favorecen al modelo; H3–H5 al ingeniero. Los cuadros anteriores de los experimentos iniciales conservan sus poblaciones originales y se identifican como historia del proceso.

Los diagramas A y B, insertados en las secciones 4.2 y 4.4, muestran en secuencia el nombre del modelo o referencia, la información añadida y la decisión tomada. No llevan título dentro de la imagen; el pie de figura los identifica. El diagrama diario está marcado en revisión.

La sección 5.1.1 presenta aparte el ensayo reciente del cuaderno 25: un modelo propio aprende sólo del historial de un producto y horizonte (por ejemplo, Minicarnation en H3), y se compara o combina con el modelo general del mismo horizonte. Para Minicarnation y Carnation, la sección da los pesos y parámetros de la combinación en H3–H5. El experimento conserva ventaja clara en H1, empate práctico en H2 y ventaja global todavía del ingeniero. No se mezclan estos resultados con la evaluación anual.

La revisión metodológica explica cómo se normalizan rendimientos, qué representa una cohorte, por qué se proponen rezagos y ventanas, qué recibe cada modelo y qué comparación sustenta una decisión. El anexo incluye el diccionario de las 47 columnas. El EDA 18 incorpora una comparación ejecutada entre clima original, diario y ampliado. Pronóstico diario y piloto SARIMA/SARIMAX se conservan con la marca «En revisión: desarrollo preliminar y siguientes pasos». La bitácora de la raíz registra la presentación prevista y los experimentos futuros.
