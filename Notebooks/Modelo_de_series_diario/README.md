# Producción diaria: flujo vigente

Este bloque usa las bases oficiales del proyecto, sin CSV auxiliares ni variables de otro kernel.

1. [01 — Base diaria y EDA](01_base_diaria_EDA.ipynb): agrega movimientos, concilia con la semana, integra clima, construye ventanas de 3/5/7/14 días y explora tendencias. Ejecutar después de la base semanal 10.
2. [14 — Mejora semanal con tendencias diarias](../Analisis/14_tendencias_diarias_modelo_semanal.ipynb): compara candidatos contra el sistema anterior y el ingeniero en los mismos casos de 2026. Requiere 13 y diario 01.
3. [02 — Del pronóstico semanal al diario](02_distribucion_semanal_a_diaria.ipynb): compara un modelo diario autónomo con repartos uniforme, histórico y boosting, reconciliados al total semanal de 14. Evalúa H1, los siete días desde el lunes, con información congelada al origen.
4. [03 — SARIMA/SARIMAX y boosting](03_SARIMA_SARIMAX_y_boosting.ipynb): ensayo controlado de tres series elegidas por volumen anterior a 2026. Compara métodos en idénticos días y audita convergencia. No extrapolar sus métricas al conjunto de la finca.

El candidato aditivo `Sistema_diario` alimenta el reparto como decisión fijada antes de conocer resultados; no se elige automáticamente el ganador del mismo test. El clima SARIMAX se rezaga siete días, de modo que es conocido al emitir los siete días futuros.

Las ausencias diarias siguen siendo faltantes. La frecuencia de reporte sólo ayuda a estimar el patrón del volumen registrado; no certifica ceros de producción. Los repartos coherentes suman al total semanal, pero pueden empeorar frente a un modelo diario autónomo si ese total es impreciso.

Salidas fijas en `Datos_analiticos_proyecto/modelo_diario/`: panel diario, features, predicciones diarias y comparación SARIMA; dos Excel con métricas, cobertura y convergencia. Cada notebook conserva EDA, tablas y gráficos ejecutados.

Usar `entorno_tesis`. Se añadió `statsmodels==0.15.0` para SARIMA/SARIMAX; puede instalarse desde la raíz con `.\entorno_tesis\Scripts\python.exe -m pip install statsmodels==0.15.0`. No se requiere ejecutar scripts propios.

La [guía principal](../../GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md) contiene el recorrido completo y los resultados verificados. El escrito actualizado está en `Trabajo escrito/Estructura_actualizada_con_resultados.docx`; el original se conserva.


## Extensión vigente con memoria semanal

Después de 15 y de diario 02/03 ejecutar `04_diario_con_memoria_semanal.ipynb`. Conserva los repartos anteriores y añade la comparación al total Memoria_larga, incluyendo el piloto SARIMA. El experimento 02 sigue siendo la referencia fijada; 04 es una extensión retrospectiva explícita. Resultado principal: reconciliado 28,29 % → 27,45 % WAPE; autónomo 26,76 %. En semanas con siete reportes gana el uniforme: leer esa sensibilidad antes de concluir.

Para errores de entrenamiento y evaluación de los mismos ajustes ejecutar `../Analisis/17_inventario_modelos_train_test.ipynb`. La guía principal contiene el orden exacto completo.
