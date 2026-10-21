# Metodología vigente

El recorrido reproducible está en la [guía paso a paso](GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md). El escrito desarrolla el razonamiento y las limitaciones.

- Alcance: GAITANA, tallos reportados, H1–H5 y reparto diario de H1. No se amplía a ARABELLA.
- Identidad comercial central, conservación de cantidades y auditoría separada de correspondencias de camas piloto. La curva empírica resume rendimientos observados por variedad y edad dentro de la ventana disponible; se verifica qué edades representa antes de usarla como referencia de un plano. La atribución de finca de los pilotos es inferida por coincidencia exacta; se exige evidencia disponible al construir cada curva.
- Proyecciones ya calculadas como referencia del ajuste. Cuando la curva representa todas las edades de las cohortes del plano, el modelo ajusta esa referencia. Cuando no, mantiene el caso y usa la ruta basada en producción reciente. No introduce otra vez plantas o edades como predictores adicionales.
- Clima previo al origen: temperatura, humedad, radiación y lluvia. Cobertura y unidades auditadas. EDA con objetivos anteriores a julio de 2025; desplazamiento relativo en cinco semanas, sin interpretarlo como causalidad o retraso fisiológico demostrado.
- Experimento 19: mismo boosting y parámetros; sin clima, clima básico actualizado, clima ampliado y curva atribuida a GAITANA. Selección con noviembre–diciembre de 2025, objetivos cerrados antes de 2026. Se mantiene el candidato durante la evaluación retrospectiva de 2026.
- Reentrenamiento mensual con objetivos cerrados antes del corte; imputación y codificación ajustadas sólo en train. Mismos casos al comparar modelos e ingeniero; test principal con emparejamiento estricto y entrega nominal no posterior.
- WAPE, MAE, RMSE y sesgo por horizonte y periodo. En 19, sesgo = predicción menos real; el porcentaje divide la suma de errores firmados por el volumen real. Positivo indica sobreestimar. No confundir compensación de errores con precisión. Los cuadernos históricos pueden usar el signo opuesto y lo indican.
- Diario 05: conservar pesos de 02, distribuir el total seleccionado en 19 y verificar la suma semanal. Comparar con el diario autónomo sobre los mismos reportes. La lluvia adicional no entra directamente en los pesos. SARIMA/SARIMAX es un piloto de tres series, con población propia.
- Interpretación por permutación en 16; no SHAP ni causalidad. Train/test del mismo ajuste en 19 y diario 05; inventario de referencias en 17. Train es dentro de muestra, no un backtest histórico.

Los periodos ya examinados constituyen desarrollo retrospectivo. Permanecen pendientes disponibilidad histórica de fuentes, microclima representado, unidades de lluvia, pilotos desconocidos y significado de días sin reporte. No imputar producción objetivo, usar clima futuro observado ni afirmar utilidad económica o aprobación operativa sin evidencia.

El EDA final 20 descompone exactamente WAPE y sesgo en el panel común, sin cambiar las predicciones. Producto, producto/color y producto/color/variedad son niveles separados. Los aportes de error absoluto divididos por el real total sí son aditivos; los WAPE locales no. Se explicitan soporte, volumen, sobre/subestimaciones, concentración temporal y diagnósticos dentro de producto. Los cambios respecto a media4 que utilizan y son ex post y nunca predictores. Las explicaciones son hipótesis a contrastar y no autorizan recalibrar usando el test.

## Lectura metodológica detallada

El escrito desarrolla: homologación de nombres y rendimiento por planta (3.2), cobertura y ejemplo DINO (3.3), evidencia de memoria semanal/diaria (3.6.1), correspondencia entre las 26 entradas climáticas y los modelos (3.7), base y diccionario (4.1 y anexo), catálogo de modelos/variables y evaluación temporal (4.2), evolución de resultados y errores por producto (5). La evidencia del EDA motiva hipótesis; las comparaciones predictivas prueban bloques, no cada variable individualmente.

(Pronóstico diario en revisión: desarrollo preliminar y siguientes pasos.) Se conservan notebooks y resultados. Esto no excluye las señales diarias de corte que ya alimentan el modelo semanal. Los siguientes experimentos y la presentación de cuatro bloques se registran en BITACORA_REVISION_CONVERSADA.md.


## Auditoría de correspondencias, 19 de octubre de 2026

En cortes fechados en 2026 se identificaron 32.986 de 33.039 estadísticas (99,84 %). Se corrigieron diferencias de escritura que duplicaban candidatas. Las 53 filas restantes se listan por referencia. La edad coincide con las fechas en 477.426 estadísticas utilizables y 1.064.620 proyecciones de 2026.

La producción observada permanece en la base analítica. La curva es referencia directa cuando representa las edades de todas las cohortes del plano; si no aplica directamente, el modelo puede usar producción reciente cuando existe historia suficiente. La cobertura indica cuál referencia puede usarse, no cuántos datos reales se conservaron ni si falló el cruce de camas. Una edad no representada en la curva no se convierte automáticamente en producción cero. El cruce piloto–estadística se auditó por separado: `Datos_analiticos_proyecto/revision_cruces_20261019/`.

## Evaluación reciente por horizonte, cuadernos 21–25

La prueba reciente usa 1.226 casos emparejados de GAITANA en tres semanas objetivo y se presenta separada del test anual. Se comparan WAPE y sesgo en los mismos casos; el ingeniero sólo es benchmark. El candidato conserva el boosting agrupado H1–H2 para H1 y usa modelos específicos para horizontes posteriores. En H1 obtiene 12,28 % WAPE frente a 15,23 % del ingeniero, una mejora clara de 2,95 puntos. En H2 obtiene 14,96 % frente a 14,98 %, diferencia marginal que se interpreta como empate práctico hasta contar con más semanas. En el total reciente obtiene 17,53 % frente a 16,34 % del ingeniero; éste mantiene ventaja en H3–H5.

El cuaderno 25 prueba especialistas por producto y horizonte junto con una combinación de predicciones de modelos propios. No usa el pronóstico del ingeniero como variable. Reduce el WAPE del candidato reciente de 17,80 % a 17,53 %, pero no revierte el resultado conjunto. El experimento n−1 tampoco produjo una mejora general. Los cuadernos 21–25 completan la exploración de modelos por horizonte y productos; el siguiente paso es conservar la mejora de H1 y confirmarla en semanas futuras, a la vez que se investiga H3–H5 sin mezclar ventanas de evaluación.
