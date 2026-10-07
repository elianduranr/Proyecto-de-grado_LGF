# Guía vigente: clima, proyecciones y pronóstico de GAITANA

## Qué leer primero

El [trabajo escrito](Trabajo%20escrito/Estructura_actualizada_con_resultados.docx) contiene contexto, calidad, EDA, método, resultados y límites; su [Markdown editable](Trabajo%20escrito/Desarrollo_del_documento.md) contiene la misma redacción. Para esta revisión, estudiar procedencia de pilotos, 18 (EDA climático), 19 (comparación semanal), diario 05 (resultado diario) y 16 (interpretación). Los notebooks conservan salidas ejecutadas.

## Resultado actual

Clima válido de GAITANA hasta **21 de septiembre de 2026**. Sólo se modela GAITANA: no se amplía el benchmark ni las conclusiones a ARABELLA. La lluvia se incorpora en unidades de fuente, con cobertura explícita. Los intervalos del EDA de desplazamiento incluyen cero: no se demuestra una regla general de retraso/adelanto por clima.

Elección fijada con validación anterior a 2026: **Boosting sin clima**. WAPE conjunto 19,46 %, ingeniero 19,74 %, mismos 15.838 casos. Una ventaja positiva de WAPE favorece al modelo; el sesgo tiene signo propio:

| Horizonte | Casos | WAPE anterior | WAPE actual | WAPE ingeniero | Ventaja actual vs. ingeniero (pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| H1 | 3.413 | 15,68 % | 15,66 % | 17,09 % | 1,43 |
| H2 | 3.289 | 17,56 % | 17,37 % | 19,28 % | 1,91 |
| H3 | 3.166 | 20,39 % | 20,39 % | 20,32 % | -0,07 |
| H4 | 3.045 | 22,14 % | 21,96 % | 20,91 % | -1,04 |
| H5 | 2.925 | 22,77 % | 22,50 % | 21,40 % | -1,10 |
| Conjunto | 15.838 | 19,59 % | 19,46 % | 19,74 % | 0,28 |

| Horizonte | Sesgo anterior | Sesgo actual | Sesgo ingeniero |
| --- | ---: | ---: | ---: |
| H1 | -1,71 % | -1,23 % | -7,56 % |
| H2 | -3,41 % | -2,40 % | -8,17 % |
| H3 | -3,89 % | -2,70 % | -9,46 % |
| H4 | -4,63 % | -3,27 % | -11,32 % |
| H5 | -4,23 % | -2,63 % | -12,63 % |
| Conjunto | -3,54 % | -2,42 % | -9,75 % |

Sesgo = 100 × suma(predicción − real) / suma(real). Positivo: sobreestimación; negativo: subestimación. Cero no implica poco error: errores opuestos pueden compensarse. WAPE y sesgo se calculan sobre los mismos casos por horizonte.

Diario reconciliado al candidato: **27,27 %**; autónomo: **26,72 %**, mismos 22.973 días. No confundir precisión libre con conservar el total semanal. Leer sensibilidad de semanas con siete reportes, que no puede usarse para escoger método al origen.

## Lo que sabemos de las curvas

La auditoría inicial recuperó 74.304 observaciones utilizables en la edición 2026; la teoría completa global pasó de 17,96 % a 21,25 %. No sumar recuperaciones entre ediciones que repiten historia. El catálogo comercial central conserva IDs y ambigüedades; 33 combinaciones con obtentor discrepante siguen pendientes de revisión agronómica.

La atribución por bloque+cama+variedad+fecha de siembra identifica 241.564 observaciones de 2026 como GAITANA y deja 202.912 sin pareja. No se encontró atribución inequívoca a ARABELLA. No afirmar que la curva original mezclaba comprobablemente fincas. Al restringir a pilotos atribuibles, la cobertura de plantas de GAITANA pasa de 79,12 % a 74,78 %: son exposiciones por plano/horizonte, no plantas físicas únicas ni cobertura del panel de casos. El experimento 19 compara la alternativa sin inventar curvas ni ocultar el cambio al respaldo.

## Orden exacto de corrida

Usar el intérprete `entorno_tesis`. Abrir cada notebook, reiniciar su kernel y ejecutar todas sus celdas de arriba abajo; esperar a que termine sin errores antes del siguiente. Las dependencias son archivos explícitos, no variables de otro kernel. Las bases limpias locales de producción y estimados deben existir; no hace falta consultar SQL de nuevo para esta actualización climática.

1. [Limpieza clima](Notebooks/Limpieza%20data,%20Notebooks%20y%20Scripts/02_limpieza_clima.ipynb): Actualizar fuente climática y verificar fechas/conflictos.
2. [Catálogo](Notebooks/Proyecciones%20Teoricas%20Propias/00_catalogo_variedades.ipynb): Reglas comunes de variedad.
3. [Auditoría](Notebooks/Proyecciones%20Teoricas%20Propias/Auditoria_calidad_curvas.ipynb): Recuperación y conservación.
4. [Proyecciones](Notebooks/Proyecciones%20Teoricas%20Propias/Proyecciones_teoricas_todos_los_anios.ipynb): Recuperar proyecciones compartidas auditadas.
5. [Procedencia](Notebooks/Proyecciones%20Teoricas%20Propias/01_procedencia_pilotos_y_curvas_gaitana.ipynb): Probar curva atribuible a GAITANA.
6. [Base semanal](Notebooks/Analisis/10_base_analitica_proyecciones.ipynb): Integración de producción, teoría y clima.
7. [EDA climático](Notebooks/Analisis/18_EDA_clima_y_desfase.ipynb): Cobertura, lluvia, error y desplazamiento.
8. [EDA general](Notebooks/Analisis/11_EDA_proyecciones.ipynb): Composición y señales históricas.
9. [Modelos iniciales](Notebooks/Analisis/12_modelo_ajuste_proyecciones.ipynb): Referencias, Ridge y boosting.
10. [Benchmark](Notebooks/Analisis/13_comparacion_ingeniero_modelo_2026.ipynb): Mismos casos del ingeniero.
11. [Base diaria](Notebooks/Modelo_de_series_diario/01_base_diaria_EDA.ipynb): Calendario y señales conocidas al origen.
12. [Tendencias](Notebooks/Analisis/14_tendencias_diarias_modelo_semanal.ipynb): Señales diarias en el pronóstico semanal.
13. [Memoria](Notebooks/Analisis/15_calidad_y_mejora_por_horizonte.ipynb): Arquitectura de referencia con memoria larga.
14. [Comparación climática](Notebooks/Analisis/19_modelos_clima_y_curvas_gaitana.ipynb): Ablaciones y selección pre2026.
15. [Distribución diaria](Notebooks/Modelo_de_series_diario/02_distribucion_semanal_a_diaria.ipynb): Autónomo y pesos de reparto.
16. [Piloto temporal](Notebooks/Modelo_de_series_diario/03_SARIMA_SARIMAX_y_boosting.ipynb): Tres series, convergencia y clima lag7.
17. [Reparto con memoria](Notebooks/Modelo_de_series_diario/04_diario_con_memoria_semanal.ipynb): Referencia actualizada.
18. [Inventario train/test](Notebooks/Analisis/17_inventario_modelos_train_test.ipynb): Errores por corte y componentes train del diario.
19. [Diario vigente](Notebooks/Modelo_de_series_diario/05_diario_clima_actualizado.ipynb): Propagar selección y medir train/test compuesto.
20. [Interpretación](Notebooks/Analisis/16_interpretacion_modelo_semanal.ipynb): Importancia del candidato seleccionado.
21. [EDA del origen del error](Notebooks/Analisis/20_EDA_origen_error_modelo_ingeniero.ipynb): Producto → color → variedad; H1 y H1–H5, aportes al WAPE, sesgo y semanas críticas. Usa salidas de 10 y 19; no reentrena.

En proyecciones de todos los años, `RECALCULAR_DESDE_EXCEL=False` recupera la auditoría vigente. Si cambian fuentes de planos/pilotos: catálogo → todos los años con `True` → auditoría → todos los años con `False` → procedencia y resto de la cadena. Conservar referencias históricas de calidad y clima: no sustituir el “antes” por el resultado actualizado.

Para sólo estudiar no hace falta reentrenar. Para reproducir sólo la extensión con entradas ya actualizadas: procedencia → 18 → 19 → 17 (si faltan componentes train diarios) → diario 05 → 16 → 20. Los resultados de 10, diario 01, 14, 15 y diario 02/03/04 deben corresponder al mismo clima vigente; no mezclar archivos de revisiones anteriores.

## Cómo se evalúa

No hay división aleatoria. Cada ajuste mensual entrena sólo con semanas objetivo terminadas antes del primer origen de ese mes. Los pesos/preparación se ajustan en train y los predictores usan datos anteriores al lunes. El experimento 19 selecciona entre cuatro alternativas con noviembre–diciembre de 2025, objetivos cerrados antes de 2026, y mantiene esa elección durante la evaluación. Todo el proyecto sigue siendo desarrollo retrospectivo porque esos periodos ya se examinaron.

Las tablas train/test de 19 y diario 05 corresponden al mismo corte. El test principal semanal usa el emparejamiento estricto del ingeniero; `test` sin sufijo en los controles de 19 incluye todos los casos elegibles, mientras `test_principal` conserva sólo la comparación estricta. No restar train del último ajuste al test acumulado de todo el año como si fueran la misma población. El inventario 17 mantiene referencias iniciales con sus propios periodos.

## Archivos de resultados

- `Datos_analiticos_proyecto/revision_clima_finca/auditoria_finca_curvas.xlsx`: atribuciones, ambigüedades y cobertura.
- `eda_clima_y_desfase.xlsx`, en esa carpeta: cobertura, asociaciones dentro de serie, ventanas sin superposición e incertidumbre.
- `resultados_clima_curvas.xlsx`: validación, modelos, horizontes, movimiento del estimado, rutas y train/test por corte.
- `Datos_analiticos_proyecto/modelo_diario/resultados_diarios_clima.xlsx`: precisión diaria, siete reportes, panel estricto, piloto y train/test compuesto.
- `Datos_analiticos_proyecto/modelo_con_proyecciones_teoricas/interpretacion_modelo_semanal.xlsx`: importancia por permutación del candidato. No es SHAP ni causalidad.
- [Resumen de modelos](resumen_modelos_pronostico.md): tablas separadas semanal y diaria, con nombres comprensibles.

## Actualizar el Word

Tras ejecutar y revisar cifras e interpretación en `Trabajo escrito/Desarrollo_del_documento.md`, correr desde la raíz:

```powershell
.\entorno_tesis\Scripts\python.exe "Trabajo escrito/actualizar_word.py"
```

El script genera el Word desde el Markdown y las figuras; no reentrena ni reescribe automáticamente conclusiones. No subir datasets. Las fuentes originales permanecen intactas. Los notebooks antiguos del benchmark se conservan como evidencia, no constituyen otro recorrido obligatorio.

## Pendientes concretos

Confirmar unidades de lluvia, microclima representado por la estación, latencia de reportes y finca de pilotos sin pareja. Aclarar días sin reporte antes de interpretarlos como ausencia de corte. Validar el candidato en nuevas fechas con emisiones archivadas y configuración fijada. Mantener GAITANA PPTO separada y no afirmar equivalencia exportable ni ahorros empresariales sin evidencia.

## Estudiar el origen del error

En 20 empezar por aportes por producto y después por color/variedad. Separar WAPE local, participación en el error y aporte al WAPE total. Leer las sobre/subestimaciones antes de concluir por sesgo. Revisar estabilidad mensual, curvas disponibles y variabilidad previa; los cambios del real frente a media4 son diagnóstico ex post, no predictores.

Las salidas están en `Datos_analiticos_proyecto/eda_origen_error/`: Excel con todos los grupos, horizontes y casos; Parquet de casos comparables; Markdown de hallazgos calculados. El foco de tres variedades es exploratorio, elegido mirando test. No modifica ni mejora artificialmente las predicciones. Para reproducir sólo este EDA, ejecutar 20 con las salidas vigentes de 10 y 19. Si cambian esas fuentes, revisar la interpretación escrita tras ejecutar y regenerar el Word. Mantener el Word cerrado al guardarlo.
