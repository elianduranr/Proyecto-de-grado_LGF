# Guía vigente: clima, proyecciones y pronóstico de GAITANA

## Revisar el primer prototipo web

La carpeta [plataforma_gaitana](plataforma_gaitana/README.md) contiene frontend, backend, trabajador, migraciones y configuración Docker. Desde esa carpeta: `instalar.cmd` una vez y `iniciar.cmd` para levantarlo; abrir `http://localhost:5173`. `detener.cmd` conserva datos y versiones al detener los servicios.

Para actualizar la aplicación, abre **Generar y ajustar**, revisa los pendientes y pulsa **Procesar archivos**. El trabajador ejecuta la cadena de notebooks de referencia sobre los originales congelados, valida los resultados, guarda las fuentes limpias en SQL Server `Proyectos`, esquema `EP`, y activa la nueva base completa. No hay que volver a subir archivos que ya estén disponibles en las carpetas. Las cargas nuevas no alteran los datos vigentes hasta terminar correctamente. Ver [ETL y SQL](plataforma_gaitana/ETL_Y_SQL.md) y el [estado del prototipo](plataforma_gaitana/ESTADO_PROTOTIPO.md) para distinguir resultados validados, carga inicial y comprobación operativa.

Para nuevos cortes, **Actualizar desde WebFlor** descarga días cerrados, comprueba el empalme con el histórico y ejecuta la actualización analítica. Para las otras fuentes, la tabla indica el último período cargado y qué subir después respecto a H1. Clima y estadísticas históricas pueden seguir utilizándose sin una actualización semanal; si el clima no alcanza el corte se conserva la variante Sin clima. Véanse [las reglas de WebFlor](plataforma_gaitana/WEBFLOR.md). La aplicación mantiene sus versiones operativas en `plataforma_gaitana/storage`; la evaluación archivada de los notebooks se conserva separada.

## Evaluación más reciente

El cuaderno 26 amplía la comprobación temporal hasta 2026-10-19. Ver la sección final de esta guía para resultados, train/test y orden de reproducción. Las cifras de la sección de referencia siguiente pertenecen al panel original.

## Qué leer primero

El [trabajo escrito](Trabajo%20escrito/Documento_LaGaitana_v8_validacion_temporal_actualizada_20261028.docx) y su [Markdown editable](Trabajo%20escrito/Documento_LaGaitana_v8_validacion_temporal_actualizada_20261028.md) conservan el recorrido metodológico y sus diagramas. Para entender, leer en este orden:

1. **Antes del modelo:** capítulos 2–3, fuentes, homologación comercial, tallos por planta, curvas y cobertura. Distinguir cero de dato ausente.
2. **Qué es una fila:** 4.1, anexo de 47 columnas y [lectura.ipynb](lectura.ipynb). Separar origen, objetivo y versiones previas.
3. **Por qué esas variables:** 3.6.1 y 3.7; asociaciones de 11, tendencias de diario 01 y puente climático de 18. Una asociación propone una hipótesis; no demuestra mejora predictiva.
4. **Qué hace cada modelo:** 4.2 y Diagrama A; referencias → Ridge/HistGradientBoosting → ruta teórica o respaldo Media4 → señales diarias y memoria → selección pre-2026 → pruebas por horizonte/producto.
5. **Qué evidencia respalda las decisiones:** recorrido de resultados del capítulo 5, selección temporal, benchmark, WAPE y sesgo, y errores por producto/color/variedad en 5.6 y notebook 20.
6. **Pasos siguientes:** capítulo 7. Pronóstico diario y SARIMA/SARIMAX se conservan como desarrollo preliminar en revisión; no son un requisito para entender primero el sistema semanal.

La [bitácora](BITACORA_REVISION_CONVERSADA.md) registra decisiones, límites y el esquema de presentación en cuatro bloques. El orden de lectura anterior explica la metodología; el orden de corrida de abajo respeta dependencias de archivos.

## Resultado de referencia conservado · hasta S36

La evaluación anual actualizada reúne 16.325 comparaciones estrictas: 19,36 % WAPE para el boosting seleccionado y 19,71 % para el ingeniero. El modelo queda mejor en H1 (15,53 % frente a 16,93 %) y H2 (17,49 % frente a 19,16 %); el ingeniero conserva menor WAPE en H3–H5. La ventana reciente de los cuadernos 21–25 es otra evaluación y no se mezcla con la anual. El detalle y sesgo están en el [resumen de modelos](resumen_modelos_pronostico.md).

(Pronóstico diario en revisión: desarrollo preliminar y siguientes pasos.) El Diagrama B distingue los objetivos: el diario reconciliado obtiene 27,26 % y conserva el total semanal; el autónomo obtiene 26,72 % y estima cada día, sobre 22.973 días reportados.

## Qué verifican los cruces y cuándo aplica la curva

En cortes fechados en 2026 hay 32.986 de 33.039 estadísticas con correspondencia única de cama, identidad comercial y ciclo (99,84 %). Se normalizaron las diferencias de mayúsculas que estaban creando candidatas duplicadas. Las 52 estadísticas ambiguas y la identidad incompleta se conservan para revisar por referencia en `Datos_analiticos_proyecto/revision_cruces_20261019/referencias_pendientes_cortes_2026.csv`.

El cruce de camas piloto con sus estadísticas se audita por identidad de cama, variedad y ciclo. En cortes fechados en 2026, 32.986 de 33.039 registros quedaron vinculados de forma única (99,84 %); las pocas referencias pendientes se mantienen identificadas para revisión. La edad también se verificó: coincide con las fechas fuente en 477.426 estadísticas utilizables y 1.064.620 filas de proyección.

En la base analítica se conserva la producción real observada. La curva teórica se usa como referencia directa cuando representa todas las edades del plano; si no aplica directamente, el modelo puede usar la producción reciente cuando hay historia suficiente. Así, la cobertura indica cuándo sirve la curva como punto de partida; no significa que falten datos reales ni que haya fallado el cruce de camas.

## Orden exacto de corrida

Usar el intérprete `entorno_tesis`. Abrir cada notebook, reiniciar su kernel y ejecutar todas sus celdas de arriba abajo; esperar a que termine sin errores antes del siguiente. Las dependencias son archivos explícitos, no variables de otro kernel. Las bases limpias locales de producción y estimados deben existir; no hace falta consultar SQL de nuevo para esta actualización climática.

Para reproducir la corrección de los estimados y sus resultados: ejecutar primero [limpieza de estimados semanales 03](Notebooks/Limpieza%20data,%20Notebooks%20y%20Scripts/03_limpieza_estimados_semanales.ipynb), que aplica la regla nominal de H1; después actualizar la base semanal 10 y correr 13 → 19 → 20. El 13 fija la comparación contra el ingeniero, el 19 mide las alternativas climáticas en los mismos casos y el 20 desglosa el origen del error. El cuaderno 20 no vuelve a entrenar. Para cambios de curvas, planos o producción hay que reconstruir desde los pasos anteriores de la lista.

1. [Limpieza clima](Notebooks/Limpieza%20data,%20Notebooks%20y%20Scripts/02_limpieza_clima.ipynb): Actualizar fuente climática y verificar fechas/conflictos.
2. [Catálogo](Notebooks/Proyecciones%20Teoricas%20Propias/00_catalogo_variedades.ipynb): Reglas comunes de variedad.
3. [Auditoría](Notebooks/Proyecciones%20Teoricas%20Propias/Auditoria_calidad_curvas.ipynb): Recuperación y conservación.
4. [Proyecciones](Notebooks/Proyecciones%20Teoricas%20Propias/Proyecciones_teoricas_todos_los_anios.ipynb): Recuperar proyecciones compartidas auditadas.
5. [Procedencia](Notebooks/Proyecciones%20Teoricas%20Propias/01_procedencia_pilotos_y_curvas_gaitana.ipynb): Probar curva atribuible a GAITANA.
6. [Base semanal](Notebooks/Analisis/10_base_analitica_proyecciones.ipynb): Integración de producción, teoría y clima.
7. [EDA de edades](Notebooks/Proyecciones%20Teoricas%20Propias/02_EDA_edades_sin_cobertura.ipynb): Revisar edades tempranas, huecos y ceros registrados. Es diagnóstico, no modifica curvas.
8. [EDA general](Notebooks/Analisis/11_EDA_proyecciones.ipynb): Composición y señales históricas.
9. [Modelos iniciales](Notebooks/Analisis/12_modelo_ajuste_proyecciones.ipynb): Referencias, Ridge y boosting.
10. [Benchmark](Notebooks/Analisis/13_comparacion_ingeniero_modelo_2026.ipynb): Mismos casos del ingeniero; prioriza el archivo semanal cuyo nombre define H1.
11. [Base diaria](Notebooks/Modelo_de_series_diario/01_base_diaria_EDA.ipynb): Calendario y señales conocidas al origen. Este paso construye entradas del SEMANAL; no exige entrenar pronósticos diarios.
12. [Tendencias](Notebooks/Analisis/14_tendencias_diarias_modelo_semanal.ipynb): Señales diarias en el pronóstico semanal.
13. [Memoria](Notebooks/Analisis/15_calidad_y_mejora_por_horizonte.ipynb): Arquitectura de referencia con memoria larga.
14. [EDA climático](Notebooks/Analisis/18_EDA_clima_y_desfase.ipynb): Relacionar las 26 variables climáticas originales/diarias/ampliadas con los modelos; cobertura, error y desplazamiento. Requiere base semanal y señales de diario 01.
15. [Comparación climática](Notebooks/Analisis/19_modelos_clima_y_curvas_gaitana.ipynb): Ablaciones y selección pre2026.
16. [Interpretación](Notebooks/Analisis/16_interpretacion_modelo_semanal.ipynb): Importancia del candidato seleccionado.
17. [EDA del origen del error](Notebooks/Analisis/20_EDA_origen_error_modelo_ingeniero.ipynb): Producto → color → variedad; H1 y H1–H5, aportes al WAPE, sesgo y semanas críticas. Usa el emparejamiento estricto actualizado; no reentrena.
18. [Distribución diaria](Notebooks/Modelo_de_series_diario/02_distribucion_semanal_a_diaria.ipynb): Autónomo y pesos de reparto. **(En revisión: desarrollo preliminar y siguientes pasos.)**
19. [Piloto temporal](Notebooks/Modelo_de_series_diario/03_SARIMA_SARIMAX_y_boosting.ipynb): Tres series, convergencia y clima lag7. **(En revisión: desarrollo preliminar y siguientes pasos.)**
20. [Reparto con memoria](Notebooks/Modelo_de_series_diario/04_diario_con_memoria_semanal.ipynb): Referencia actualizada. **(En revisión: desarrollo preliminar y siguientes pasos.)**
21. [Inventario train/test](Notebooks/Analisis/17_inventario_modelos_train_test.ipynb): Errores por corte y componentes train del diario.
22. [Diario vigente](Notebooks/Modelo_de_series_diario/05_diario_clima_actualizado.ipynb): Propagar selección y medir train/test compuesto. **(En revisión: desarrollo preliminar y siguientes pasos.)**
23. [Semanas recientes frente al ingeniero](Notebooks/Analisis/21_validacion_semanas_nuevas_ingeniero.ipynb): Comparación en el periodo reciente.
24. [Modelos por horizonte](Notebooks/Analisis/22_modelos_separados_horizonte.ipynb): Contrastar agrupación y especialistas H1–H5.
25. [Experimento n−1](Notebooks/Analisis/23_experimento_n_menos_1_productos.ipynb): Diagnóstico de interferencia entre productos.
26. [Mejora y validación temporal](Notebooks/Analisis/24_experimento_mejora_semanal_y_validacion_temporal.ipynb): Selección del candidato reciente en mismos casos.
27. [Especialistas H3–H5](Notebooks/Analisis/25_modelos_propios_h3_h5.ipynb): Ajuste por producto y combinación sin usar estimados del ingeniero como predictor.

En proyecciones de todos los años, `RECALCULAR_DESDE_EXCEL=False` recupera la auditoría vigente. Si cambian fuentes de planos/pilotos: catálogo → todos los años con `True` → auditoría → todos los años con `False` → procedencia y resto de la cadena. Conservar referencias históricas de calidad y clima: no sustituir el “antes” por el resultado actualizado.

Para sólo estudiar no hace falta reentrenar. Para reproducir solo la extensión semanal con entradas ya actualizadas: procedencia → 18 → 19 → 16 → 20. Para estudiar o ejecutar el diario en revisión, continuar por diario 02/03/04 → 17 → diario 05 según las dependencias existentes. Los resultados de 10, diario 01, 14, 15 y diario 02/03/04 deben corresponder al mismo clima vigente; no mezclar archivos de revisiones anteriores.

## Experimentos semanales recientes

Con producción real, estimados y base analítica actualizados, la secuencia de experimentos recientes es: 21 (benchmark) → 22 (horizontes) → 23 (n−1) → 24 (selección en los mismos casos) → 25 (especialistas para H3–H5). La evaluación reciente favorece claramente H1 y deja H2 prácticamente empatado; el ingeniero todavía gana en el conjunto y en H3–H5. Confirmar en semanas futuras completas antes de adoptar el candidato.

## Cómo se evalúa

No hay división aleatoria. Cada ajuste mensual entrena sólo con semanas objetivo terminadas antes del primer origen de ese mes. Los pesos/preparación se ajustan en train y los predictores usan datos anteriores al lunes. El notebook 12 usa tres cortes (2025-07-07, 2026-01-05 y 2026-05-04), con ocho semanas de orígenes por evaluación; 13–19 pasan al reentrenamiento mensual. El experimento 19 selecciona entre cuatro alternativas con noviembre–diciembre de 2025, objetivos cerrados antes de 2026, y mantiene esa elección durante la evaluación. Todo el proyecto sigue siendo desarrollo retrospectivo porque esos periodos ya se examinaron.

Las tablas train/test de 19 y diario 05 corresponden al mismo corte. El test principal semanal usa el emparejamiento estricto del ingeniero; `test` sin sufijo en los controles de 19 incluye todos los casos elegibles, mientras `test_principal` conserva sólo la comparación estricta. No restar train del último ajuste al test acumulado de todo el año como si fueran la misma población. El inventario 17 mantiene referencias iniciales con sus propios periodos.

## Archivos de resultados

- `Datos_analiticos_proyecto/revision_clima_finca/auditoria_finca_curvas.xlsx`: atribuciones, ambigüedades y cobertura.
- `eda_clima_y_desfase.xlsx`, en esa carpeta: cobertura, asociaciones dentro de serie, ventanas sin superposición e incertidumbre.
- `eda_clima_variables_modelos.xlsx`: las 26 columnas climáticas, soporte por variable y común, correlaciones por serie/horizonte; figura `clima_variables_modelos.png` en el escrito.
- `resultados_clima_curvas.xlsx`: validación, modelos, horizontes, movimiento del estimado, rutas y train/test por corte.
- `Datos_analiticos_proyecto/modelo_diario/resultados_diarios_clima.xlsx`: precisión diaria, siete reportes, panel estricto, piloto y train/test compuesto.
- `Datos_analiticos_proyecto/modelo_con_proyecciones_teoricas/interpretacion_modelo_semanal.xlsx`: importancia por permutación del candidato. No es SHAP ni causalidad.
- [Resumen de modelos](resumen_modelos_pronostico.md): tablas separadas semanal y diaria, con nombres comprensibles.

## Actualizar el Word

Tras ejecutar y revisar cifras e interpretación en `Trabajo escrito/Desarrollo_del_documento.md`, correr desde la raíz:

```powershell
.\entorno_tesis\Scripts\python.exe "Trabajo escrito/actualizar_resultados.py"
.\entorno_tesis\Scripts\python.exe "Trabajo escrito/actualizar_word.py"
```

El script genera el Word desde el Markdown y las figuras; no reentrena ni reescribe automáticamente conclusiones. No subir datasets. Las fuentes originales permanecen intactas. Los notebooks antiguos del benchmark se conservan como evidencia, no constituyen otro recorrido obligatorio.

## Pendientes concretos

Confirmar unidades de lluvia, microclima representado por la estación, latencia de reportes y finca de pilotos sin pareja. Aclarar días sin reporte antes de interpretarlos como ausencia de corte. Validar el candidato en nuevas fechas con emisiones archivadas y configuración fijada. Mantener GAITANA PPTO separada y no afirmar equivalencia exportable ni ahorros empresariales sin evidencia.

## Estudiar el origen del error

En 20 empezar por aportes por producto y después por color/variedad. Separar WAPE local, participación en el error y aporte al WAPE total. Leer las sobre/subestimaciones antes de concluir por sesgo. Revisar estabilidad mensual, curvas disponibles y variabilidad previa; los cambios del real frente a media4 son diagnóstico ex post, no predictores.

Las salidas están en `Datos_analiticos_proyecto/eda_origen_error/`: Excel con todos los grupos, horizontes y casos; Parquet de casos comparables; Markdown de hallazgos calculados. El foco de tres variedades es exploratorio, elegido mirando test. No modifica ni mejora artificialmente las predicciones. Para reproducir sólo este EDA, ejecutar 20 con las salidas vigentes de 10 y 19. Si cambian esas fuentes, revisar la interpretación escrita tras ejecutar y regenerar el Word. Mantener el Word cerrado al guardarlo.

## Próximos experimentos, todavía sin ejecutar

Comparar cinco ajustes H1–H5 frente a los dos grupos actuales; especialización por producto y prueba n−1 retirando un producto del entrenamiento pero evaluando los productos restantes sobre los mismos casos; verificar si edades tempranas de DINO sin soporte corresponden a ceros documentados. Fijar decisiones en validación y comprobarlas en un período nuevo, sin prometer reducción de WAPE. El pronóstico diario requiere profundizar calendario, cobertura y ajuste de parámetros; sus resultados se conservan como avance.

## Diagnóstico puntual del alcance de las curvas por edad

[02_EDA_edades_sin_cobertura](Notebooks/Proyecciones%20Teoricas%20Propias/02_EDA_edades_sin_cobertura.ipynb) muestra qué edades están representadas por las curvas de pilotos: tempranas, intermedias y posteriores. Lee las curvas/proyecciones existentes de 2021–2026 y la base de 10, sin reconstruir modelos. Incluye DINO y exporta una tabla de diagnóstico. El nombre del archivo se conserva por trazabilidad; su lectura es de alcance empírico de las curvas, no de pérdida de producción. Una edad previa al primer corte observado no demuestra que el rendimiento sea cero; cualquier regla productiva requiere confirmación agronómica. Es un diagnóstico opcional, no una nueva dependencia de entrenamiento.


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
