# Análisis vigente

1. [10 — Base analítica](10_base_analitica_proyecciones.ipynb).
2. [11 — EDA](11_EDA_proyecciones.ipynb).
3. [12 — Ajuste de proyecciones](12_modelo_ajuste_proyecciones.ipynb).
4. [13 — Comparación con el ingeniero en 2026](13_comparacion_ingeniero_modelo_2026.ipynb).
5. [14 — Tendencias diarias en el pronóstico semanal](14_tendencias_diarias_modelo_semanal.ipynb), después de ejecutar [diario 01](../Modelo_de_series_diario/01_base_diaria_EDA.ipynb).
6. [15 — Calidad y mejora por horizonte](15_calidad_y_mejora_por_horizonte.ipynb): diagnóstico del error, comparación antes/después de calidad, separación de horizontes, memoria larga, revisiones y combinación con pesos anteriores a 2026.

El nivel diario continúa en [su guía breve](../Modelo_de_series_diario/README.md): reparto coherente H1 y comparación SARIMA/SARIMAX frente a boosting.

Prerrequisitos y explicación completa en la [guía única](../../GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md). Cada notebook contiene su código y lee entradas explícitas, sin variables de otro kernel ni módulos propios.


La revisión actual añade `16_interpretacion_modelo_semanal.ipynb` (importancia por permutación y reproducción de agosto) y `17_inventario_modelos_train_test.ipynb` (inventario de algoritmos, errores train/test por corte y resultados completos separados). Diario 04 aplica el candidato de 15 a la distribución diaria. Ejecutar según la guía principal; 17 requiere también diario 04.
