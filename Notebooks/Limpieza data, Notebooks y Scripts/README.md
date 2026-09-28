# Limpiezas oficiales y lógica original

| Ejecutar | Fuente | Única salida en Datos_analiticos_proyecto |
|---|---|---|
| 01_limpieza_curvas_variedad.ipynb | Excel de curvas/pilotos | curvas_variedad_limpio.parquet |
| 02_limpieza_clima.ipynb | Excel de clima | clima_limpio.parquet |
| 03_limpieza_estimados_semanales.ipynb | Excel del ingeniero | estimados_semanales_limpio.parquet |
| 04_limpieza_planos_siembra.ipynb | Excel de planos | planos_siembra_limpio.parquet |
| 05_limpieza_produccion_real.ipynb | Excel de producción | produccion_real_limpio.parquet |

Ejecutar de arriba abajo con `entorno_tesis`. No importan módulos propios ni generan un archivo por semana, año, join o control.

## Reglas que se mantienen

Estimados: lectura de caché interna Excel; selección principal no ajustada; año del nombre antes que carpeta; exacta o siguiente entrega del mismo año; H1–H5 desde la semana solicitada; archivo y desfase identificados.

Producción: todas las hojas de detalle; sólo retirar filas completamente vacías; tipos explícitos; moda de Tipo Corte en semana anterior/actual/siguiente; valor original y marca de imputación conservados. No se modifican tallos.

Planos: la fórmula de edad reportada usa AL1, no el lunes del nombre del archivo. 04 reconoce `ROUND((AL1 − fecha_siembra)/7, 0)` en los 293 libros con Datos. Conserva la referencia, la edad esperada en esa fecha y la edad al lunes; valida inconsistencias contra la fórmula correcta. AL1 no prueba cuándo se recibió el archivo. No se relajan controles ni se eliminan filas por comparar dos relojes diferentes.

Una recuperación desde un archivo posterior y una imputación que usa la semana siguiente son reconstrucciones retrospectivas, no información automáticamente disponible al pronosticar.

## Originales recuperados

Los notebooks con nombres `1. Extracción de estimados`, `2_ procesamiento de producción real` y `3_Benchmark estimado ingeniero` se conservan como referencia. También está el resumen 2026 en `../03_benchmark_estimado_ingeniero.ipynb`.

No ejecutar esa antigua cadena de exportaciones: las reglas están incorporadas en 03/05 y en el benchmark de 06/07, con una sola salida por proceso.

El flujo completo y los ejemplos están en `GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md` de la raíz.
