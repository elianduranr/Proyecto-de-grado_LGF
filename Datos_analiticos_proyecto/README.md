# Datos y resultados vigentes

Entradas limpias: produccion_real_limpio.parquet, clima_limpio.parquet y estimados_semanales_limpio.parquet. El modelo usa proyecciones ya calculadas. Los planos y pilotos intervienen sólo en la etapa anterior de construcción y auditoría de las curvas.

- revision_clima_finca/: procedencia de pilotos, curva alternativa GAITANA, clima ampliado, EDA, validación y comparación semanal vigente. resultados_clima_curvas.xlsx incluye WAPE y sesgo de todos los candidatos y del ingeniero por horizonte. Las referencias predicciones_antes_clima.parquet y diario_antes_clima.parquet se conservan y no se sobrescriben.
- modelo_con_proyecciones_teoricas/: base analítica, referencias de 12–15, inventario train/test de 17 e interpretación del candidato de 19 en importancias_modelo_clima.parquet e interpretacion_modelo_semanal.xlsx.
- modelo_diario/: calendario, pesos, referencias autónomas y piloto SARIMA/SARIMAX. predicciones_diarias_clima_2026.parquet y resultados_diarios_clima.xlsx son la comparación diaria vigente de 05.

La [guía](../GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md) explica las dependencias. No sumar objetivos repetidos entre orígenes, convertir faltantes en cero ni publicar datasets. El error de entrenamiento es dentro de muestra, separado del test temporal del mismo corte.

eda_origen_error/ contiene diagnostico_origen_error.xlsx (descomposición completa, comparación de grupos y casos), casos_error_comparables.parquet y hallazgos_origen_error.md. Son salidas descriptivas de 20; no otra versión de los pronósticos.
