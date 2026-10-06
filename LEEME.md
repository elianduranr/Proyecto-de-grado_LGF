# Proyecto de grado 2

Empezar por la [guía paso a paso](GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md). Es la única lectura necesaria para conocer el orden y las decisiones del flujo vigente:

**Catálogo común 00 → auditoría de curvas → proyecciones propias → 10 base → 11 EDA → 12 ajuste → 13 comparación con el ingeniero.**

Extensión ejecutada: **diario 01 (base/EDA) → 14 (tendencias diarias para mejorar la semana) → diario 02 (reparto de H1) → diario 03 (SARIMA/SARIMAX)**. El [trabajo escrito revisado](Trabajo%20escrito/Estructura_actualizada_con_resultados.docx) integra estructura, métodos y resultados; el original se conserva.

La revisión continúa con [15: calidad y mejora por horizonte](Notebooks/Analisis/15_calidad_y_mejora_por_horizonte.ipynb). Memoria larga obtiene 19,59 % WAPE frente a 19,74 % del ingeniero en los casos retrospectivos comunes; la ventaja es pequeña y no está confirmada prospectivamente. La guía explica cobertura recuperada, intervalos y diferencias entre horizontes y métricas.

Usar el kernel `entorno_tesis`. Los notebooks conservan resultados; los Excel originales no se modifican. La guía distingue datos ya limpios, cálculos que deben repetirse y límites de las conclusiones.

La extensión actual añade diario 04 (reparto con Memoria_larga), semanal 16 (importancia por permutación) y semanal 17 (inventario de modelos y errores train/test por corte). La guía incluye una lista exacta para ejecutar todos los notebooks y reproducir las salidas. El WAPE diario reconciliado baja de 28,29 % a 27,45 %; el autónomo mantiene 26,76 %. Consultar también la sensibilidad por días reportados.
