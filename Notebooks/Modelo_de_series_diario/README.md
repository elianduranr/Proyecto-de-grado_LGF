# Cadena diaria vigente

01 construye el calendario y el EDA con producción y clima actualizados. 02 aprende el diario autónomo y los pesos de reparto usando el total de Analisis/14. 03 contrasta SARIMA y SARIMAX en tres series. 04 evalúa el total Memoria_larga de Analisis/15. 05 distribuye la elección anterior a 2026 de Analisis/19 y conserva los mismos días para comparar.

Antes de 05, ejecutar Analisis/17, que exporta los componentes de entrenamiento del último ajuste diario; Analisis/19 exporta sus predicciones de entrenamiento H1. El diario 05 construye train/test del mismo ajuste, separados del resultado acumulado. Analisis/16 explica el modelo semanal elegido. Consultar la [guía](../../GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md) para el orden completo.

Sólo GAITANA, H1 e información congelada al lunes. Los faltantes no son ceros. Reconciliar conserva el total, pero no garantiza mejorar el WAPE. La lluvia de Analisis/19 entra en el total si el candidato seleccionado la incluye; no se añadió directamente a los pesos diarios.
