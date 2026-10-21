# Guía vigente: clima, proyecciones y pronóstico de GAITANA

## Qué leer primero

El [trabajo escrito](Trabajo%20escrito/Estructura_documento_v4_oct192026.docx) y su [Markdown editable](Trabajo%20escrito/Desarrollo_del_documento.md) conservan resultados y desarrollan ahora el recorrido metodológico. Para entender, leer en este orden:

1. **Antes del modelo:** capítulos 2–3, fuentes, homologación comercial, tallos por planta, curvas y cobertura. Distinguir cero de dato ausente.
2. **Qué es una fila:** 4.1, anexo de 47 columnas y [lectura.ipynb](lectura.ipynb). Separar origen, objetivo y versiones previas.
3. **Por qué esas variables:** 3.6.1 y 3.7; asociaciones de 11, tendencias de diario 01 y puente climático de 18. Una asociación propone una hipótesis; no demuestra mejora predictiva.
4. **Qué hace cada modelo:** 4.2 y diccionario del notebook 12; referencias → correcciones Ridge/boosting → dos rutas → información diaria para semanas → grupos de horizonte y memoria larga → comparación climática de 19.
5. **Qué evidencia respalda las decisiones:** recorrido de resultados del capítulo 5, selección temporal, benchmark, WAPE y sesgo, y errores por producto/color/variedad en 5.6 y notebook 20.
6. **Pasos siguientes:** capítulo 7. Pronóstico diario y SARIMA/SARIMAX se conservan como desarrollo preliminar en revisión; no son un requisito para entender primero el sistema semanal.

La [bitácora](BITACORA_REVISION_CONVERSADA.md) registra decisiones, límites y el esquema de presentación en cuatro bloques. El orden de lectura anterior explica la metodología; el orden de corrida de abajo respeta dependencias de archivos.

## Resultado actual

La evaluación anual de 15.838 casos da 19,33 % de WAPE al boosting seleccionado y 19,74 % al ingeniero. En una evaluación reciente separada, **H1 mejora con claridad: 12,28 % frente a 15,23 %**; **H2 queda prácticamente empatado: 14,96 % frente a 14,98 %**. El ingeniero aún gana en H3–H5 y en el total reciente. No se deben mezclar las ventanas: resultados completos, sesgo y límites en [resumen de modelos](resumen_modelos_pronostico.md).

(Pronóstico diario en revisión: desarrollo preliminar y siguientes pasos.) El diario reconciliado obtiene 27,26 %; el autónomo, 26,72 %, sobre 22.973 días reportados. El primero conserva el total semanal; el autónomo estima cada día.

## Qué verifican los cruces y cuándo aplica la curva

En cortes fechados en 2026 hay 32.986 de 33.039 estadísticas con correspondencia única de cama, identidad comercial y ciclo (99,84 %). Se normalizaron las diferencias de mayúsculas que estaban creando candidatas duplicadas. Las 52 estadísticas ambiguas y la identidad incompleta se conservan para revisar por referencia en `Datos_analiticos_proyecto/revision_cruces_20261019/referencias_pendientes_cortes_2026.csv`.

El cruce de camas piloto con sus estadísticas se audita por identidad de cama, variedad y ciclo. En cortes fechados en 2026, 32.986 de 33.039 registros quedaron vinculados de forma única (99,84 %); las pocas referencias pendientes se mantienen identificadas para revisión. La edad también se verificó: coincide con las fechas fuente en 477.426 estadísticas utilizables y 1.064.620 filas de proyección.

En la base analítica se conserva la producción real observada. La curva teórica se usa como referencia directa cuando representa todas las edades del plano; si no aplica directamente, el modelo puede usar la producción reciente cuando hay historia suficiente. Así, la cobertura indica cuándo sirve la curva como punto de partida; no significa que falten datos reales ni que haya fallado el cruce de camas.

## Orden exacto de corrida

Usar el intérprete `entorno_tesis`. Abrir cada notebook, reiniciar su kernel y ejecutar todas sus celdas de arriba abajo; esperar a que termine sin errores antes del siguiente. Las dependencias son archivos explícitos, no variables de otro kernel. Las bases limpias locales de producción y estimados deben existir; no hace falta consultar SQL de nuevo para esta actualización climática.

1. [Limpieza clima](Notebooks/Limpieza%20data,%20Notebooks%20y%20Scripts/02_limpieza_clima.ipynb): Actualizar fuente climática y verificar fechas/conflictos.
2. [Catálogo](Notebooks/Proyecciones%20Teoricas%20Propias/00_catalogo_variedades.ipynb): Reglas comunes de variedad.
3. [Auditoría](Notebooks/Proyecciones%20Teoricas%20Propias/Auditoria_calidad_curvas.ipynb): Recuperación y conservación.
4. [Proyecciones](Notebooks/Proyecciones%20Teoricas%20Propias/Proyecciones_teoricas_todos_los_anios.ipynb): Recuperar proyecciones compartidas auditadas.
5. [Procedencia](Notebooks/Proyecciones%20Teoricas%20Propias/01_procedencia_pilotos_y_curvas_gaitana.ipynb): Probar curva atribuible a GAITANA.
6. [Base semanal](Notebooks/Analisis/10_base_analitica_proyecciones.ipynb): Integración de producción, teoría y clima.
7. [EDA de edades](Notebooks/Proyecciones%20Teoricas%20Propias/02_EDA_edades_sin_cobertura.ipynb): Revisar edades tempranas, huecos y ceros registrados. Es diagnóstico, no modifica curvas.
8. [EDA general](Notebooks/Analisis/11_EDA_proyecciones.ipynb): Composición y señales históricas.
9. [Modelos iniciales](Notebooks/Analisis/12_modelo_ajuste_proyecciones.ipynb): Referencias, Ridge y boosting.
10. [Benchmark](Notebooks/Analisis/13_comparacion_ingeniero_modelo_2026.ipynb): Mismos casos del ingeniero.
11. [Base diaria](Notebooks/Modelo_de_series_diario/01_base_diaria_EDA.ipynb): Calendario y señales conocidas al origen. Este paso construye entradas del SEMANAL; no exige entrenar pronósticos diarios.
12. [Tendencias](Notebooks/Analisis/14_tendencias_diarias_modelo_semanal.ipynb): Señales diarias en el pronóstico semanal.
13. [Memoria](Notebooks/Analisis/15_calidad_y_mejora_por_horizonte.ipynb): Arquitectura de referencia con memoria larga.
14. [EDA climático](Notebooks/Analisis/18_EDA_clima_y_desfase.ipynb): Relacionar las 26 variables climáticas originales/diarias/ampliadas con los modelos; cobertura, error y desplazamiento. Requiere base semanal y señales de diario 01.
15. [Comparación climática](Notebooks/Analisis/19_modelos_clima_y_curvas_gaitana.ipynb): Ablaciones y selección pre2026.
16. [Interpretación](Notebooks/Analisis/16_interpretacion_modelo_semanal.ipynb): Importancia del candidato seleccionado.
17. [EDA del origen del error](Notebooks/Analisis/20_EDA_origen_error_modelo_ingeniero.ipynb): Producto → color → variedad; H1 y H1–H5, aportes al WAPE, sesgo y semanas críticas. Usa salidas de 10 y 19; no reentrena.
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
