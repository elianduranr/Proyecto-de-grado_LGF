# Metodología vigente

El recorrido reproducible está en la [guía paso a paso](GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md). El escrito desarrolla el razonamiento y las limitaciones.

- Alcance: GAITANA, tallos reportados, H1–H5 y reparto diario de H1. No se amplía a ARABELLA.
- Identidad comercial central, conservación de cantidades, ambigüedades y variedades/edades sin curva explícitas. La atribución de finca de los pilotos es inferida por coincidencia exacta; se exige evidencia disponible al construir cada curva.
- Proyecciones ya calculadas como referencia del ajuste. Respaldo explícito con media de cuatro semanas cuando falta teoría completa. No introducir otra vez plantas o edades como predictores adicionales.
- Clima previo al origen: temperatura, humedad, radiación y lluvia. Cobertura y unidades auditadas. EDA con objetivos anteriores a julio de 2025; desplazamiento relativo en cinco semanas, sin interpretarlo como causalidad o retraso fisiológico demostrado.
- Experimento 19: mismo boosting y parámetros; sin clima, clima básico actualizado, clima ampliado y curva atribuida a GAITANA. Selección con noviembre–diciembre de 2025, objetivos cerrados antes de 2026. Se mantiene el candidato durante la evaluación retrospectiva de 2026.
- Reentrenamiento mensual con objetivos cerrados antes del corte; imputación y codificación ajustadas sólo en train. Mismos casos al comparar modelos e ingeniero; test principal con emparejamiento estricto y entrega nominal no posterior.
- WAPE, MAE, RMSE y sesgo por horizonte y periodo. En 19, sesgo = predicción menos real; el porcentaje divide la suma de errores firmados por el volumen real. Positivo indica sobreestimar. No confundir compensación de errores con precisión. Los cuadernos históricos pueden usar el signo opuesto y lo indican.
- Diario 05: conservar pesos de 02, distribuir el total seleccionado en 19 y verificar la suma semanal. Comparar con el diario autónomo sobre los mismos reportes. La lluvia adicional no entra directamente en los pesos. SARIMA/SARIMAX es un piloto de tres series, con población propia.
- Interpretación por permutación en 16; no SHAP ni causalidad. Train/test del mismo ajuste en 19 y diario 05; inventario de referencias en 17. Train es dentro de muestra, no un backtest histórico.

Los periodos ya examinados constituyen desarrollo retrospectivo. Permanecen pendientes disponibilidad histórica de fuentes, microclima representado, unidades de lluvia, pilotos desconocidos y significado de días sin reporte. No imputar producción objetivo, usar clima futuro observado ni afirmar utilidad económica o aprobación operativa sin evidencia.

El EDA final 20 descompone exactamente WAPE y sesgo en el panel común, sin cambiar las predicciones. Producto, producto/color y producto/color/variedad son niveles separados. Los aportes de error absoluto divididos por el real total sí son aditivos; los WAPE locales no. Se explicitan soporte, volumen, sobre/subestimaciones, concentración temporal y diagnósticos dentro de producto. Los cambios respecto a media4 que utilizan y son ex post y nunca predictores. Las explicaciones son hipótesis a contrastar y no autorizan recalibrar usando el test.
