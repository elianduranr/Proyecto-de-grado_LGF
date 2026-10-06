# Notebooks vigentes

La revisión de calidad comienza en `Proyecciones Teoricas Propias/00_catalogo_variedades.ipynb` y `Auditoria_calidad_curvas.ipynb`, antes de las proyecciones. [15: calidad y mejora por horizonte](Analisis/15_calidad_y_mejora_por_horizonte.ipynb) identifica el candidato semanal. La extensión continúa con [diario 04](Modelo_de_series_diario/04_diario_con_memoria_semanal.ipynb), [16: interpretación](Analisis/16_interpretacion_modelo_semanal.ipynb) y [17: inventario train/test](Analisis/17_inventario_modelos_train_test.ipynb). Consultar la guía única para el orden exacto de corrida y las cifras vigentes.

La extensión ejecutada continúa con [base diaria y EDA](Modelo_de_series_diario/01_base_diaria_EDA.ipynb), [14 tendencias diarias en el modelo semanal](Analisis/14_tendencias_diarias_modelo_semanal.ipynb), [distribución semanal a diaria](Modelo_de_series_diario/02_distribucion_semanal_a_diaria.ipynb) y [SARIMA/SARIMAX](Modelo_de_series_diario/03_SARIMA_SARIMAX_y_boosting.ipynb). El [índice diario](Modelo_de_series_diario/README.md) explica dependencias y alcance.

El único recorrido de lectura es la [guía paso a paso](../GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md): proyecciones de todos los años → [10 base](Analisis/10_base_analitica_proyecciones.ipynb) → [11 EDA](Analisis/11_EDA_proyecciones.ipynb) → [12 modelo](Analisis/12_modelo_ajuste_proyecciones.ipynb) → [13 ingeniero 2026](Analisis/13_comparacion_ingeniero_modelo_2026.ipynb).

Las limpiezas en `Limpieza data, Notebooks y Scripts/` son procesos de actualización de fuentes, no lectura adicional obligatoria. Para el nuevo flujo se utilizan producción, clima, estimados y los metadatos AL1 indicados en la guía. No se requiere ejecutar WebFlor ni los benchmarks originales.

La carpeta `coso para generar el html antes` conserva las referencias originales señaladas por el usuario. La investigación SQL y notas de campo se mantienen como evidencia documental; no forman otra cadena de ejecución. Los notebooks 06–09 sustituidos y el visor Lectura se retiraron.

La exportación opcional a CSV convierte los Parquet actuales para consulta, sin alimentar EDA/modelos. No publicar datos fuente. Los notebooks activos conservan las tablas y gráficas ejecutadas.
