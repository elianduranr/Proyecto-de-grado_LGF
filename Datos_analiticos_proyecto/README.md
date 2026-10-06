# Datos procesados

La revisión de calidad alimenta `modelo_con_proyecciones_teoricas/experimentos_horizontes_2026.parquet` y `resultados_experimentos_horizontes.xlsx`. El notebook 15 compara las mismas observaciones antes/después de calidad y por candidato. La referencia previa se conserva sólo como evidencia en la carpeta `auditoria_calidad` de las proyecciones; no es otra base activa.

`modelo_diario/` contiene el calendario diario conciliado, las variables de corte y clima calculadas con información pasada, los pronósticos diarios y las comparaciones con SARIMA/SARIMAX. La comparación semanal ampliada permanece en `modelo_con_proyecciones_teoricas/comparacion_features_diarias_2026.parquet` y `resultados_features_diarias_2026.xlsx`. La ausencia de reporte diario se conserva como dato faltante.

Flujo y salidas vigentes: [guía paso a paso](../GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md).

Las entradas limpias del flujo son `produccion_real_limpio.parquet`, `clima_limpio.parquet` y, para comparar al ingeniero, `estimados_semanales_limpio.parquet`. `planos_siembra_limpio.parquet` aporta la referencia AL1 a la etapa previa de proyecciones. Los datos de curvas y SQL se conservan como fuentes auxiliares de investigación; no entran al nuevo modelo.

Las salidas activas están en `modelo_con_proyecciones_teoricas/`: panel semanal, base de casos, evaluaciones, simulación y comparación con el ingeniero. Tienen nombres fijos, sin versiones por ejecución. La base antigua de 108 columnas fue retirada.

No sumar targets repetidos desde distintos orígenes ni confundir ausencia con cero. Los originales permanecen intactos; los Parquet no se publican en Git.


Revisión diaria/memoria: `modelo_diario/predicciones_diarias_memoria_2026.parquet`, `resultados_diarios_memoria.xlsx` y `piloto_sarima_memoria.parquet`. Interpretación: `modelo_con_proyecciones_teoricas/importancias_memoria_larga.parquet` e `interpretacion_modelo_semanal.xlsx`. Inventario: `diagnostico_train_test.parquet` e `inventario_modelos_train_test.xlsx`; los errores de train son del ajuste indicado, no un backtest histórico.
