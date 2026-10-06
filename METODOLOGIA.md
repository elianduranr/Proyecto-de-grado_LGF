# Metodología vigente

El diseño completo está en la [guía paso a paso](GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md), catálogo 00, auditoría de curvas, notebooks 10–17 y la cadena diaria. Este documento resume sus decisiones:

- Un catálogo común conserva IDs oficiales y define identidad comercial cuando producto/color/variedad son inequívocos. Múltiples IDs y códigos de obtentor quedan expuestos; no se certifica equivalencia biológica.
- Las copias de pilotos equivalentes en los atributos utilizados se consultan como una referencia, conservando fuentes y movimientos. Se verifica recuperación y conservación por plano/finca/horizonte antes de reentrenar.
- El experimento 15 separa calidad de datos de arquitectura, memoria de doce semanas e historia de proyecciones. La combinación fija pesos con validación temporal de noviembre–diciembre de 2025, sin elegirlos con 2026. La selección final de candidato sigue siendo retrospectiva.

- Panel semanal conservado por finca/producto/color/variedad; casos predictivos por origen y horizonte, H1–H5.
- Proyecciones ya calculadas como baseline; no reutilizar plantas, edades o potencial retrospectivo como predictores adicionales.
- Rezagos de calendario, clima pasado, teoría disponible e historia de pronósticos de la misma semana objetivo. No usar información futura observada.
- Ajuste aditivo de real menos teoría, con respaldo explícito de media4 corregida cuando falta teoría completa.
- Cortes temporales, parámetros fijos, codificación e imputación ajustadas sólo en train; ablaciones y métricas sobre idénticos casos.
- En 13, reentrenamiento mensual para 2026 y benchmark emparejado. Principal: unión comercial estricta y entrega no posterior. Recuperación por variedad sólo 1:1 entre pendientes; evaluar separadamente.
- MAE, RMSE, WAPE, sesgo y ±8% para real positivo; desglose por horizonte, periodo, producto, color, variedad y cobertura. Remuestreo semanal exploratorio, sin certificar independencia temporal.
- Mantener limitaciones de disponibilidad y unidades; no interpretar asociaciones como causalidad ni retrospectiva como aprobación operativa.

Los notebooks originales del benchmark se conservan como referencia de extracción y unión. La implementación vigente mejora el control de ambigüedad y no convierte faltantes en cero.

La extensión diaria 04 mantiene fijos los pesos de reparto y sustituye únicamente el total semanal por Memoria_larga; incluye sensibilidad en semanas con siete reportes, panel estricto y piloto SARIMA. El notebook 16 explica el modelo final mediante permutaciones de variables/bloques, midiendo aumento del WAPE de la predicción completa; no usa SHAP ni atribuye causalidad. El 17 reconstruye los últimos ajustes para train/test con predicciones verificadas contra los originales y separa esos cortes de los resultados acumulados. El error de train es dentro de muestra, no un backtest.
