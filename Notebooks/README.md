# Notebooks vigentes

## Limpieza de los cinco Excel

En `Limpieza data, Notebooks y Scripts/`, ejecutar independientemente:

1. `01_limpieza_curvas_variedad.ipynb`.
2. `02_limpieza_clima.ipynb`.
3. `03_limpieza_estimados_semanales.ipynb`.
4. `04_limpieza_planos_siembra.ipynb`.
5. `05_limpieza_produccion_real.ipynb`.

Cada uno contiene sus imports, rutas, limpieza, controles y una exportación Parquet. Las funciones necesarias están visibles en el cuadernillo.

03 conserva la recuperación exacta/siguiente archivo del mismo año y H1–H5 desde la solicitud. 05 conserva la imputación de Tipo Corte con su marca retrospectiva. No hay pérdida de movimientos por desduplicación indiscriminada.

## WebFlor

`Extracción SQL/02_webflor_complemento_necesario.ipynb`: usa originales locales y genera proyecciones/coeficientes limpios. La conexión está desactivada por defecto. Sólo exporta las dos tablas finales.

## Análisis

En `Analisis/`: 06 construye la base única y el enlace de benchmark; 07 hace EDA orientado a actualización; 08 prepara features y prueba fuga; 09 entrena y compara primeros modelos. Sólo 06 exporta un dataset. Todos consumen datos de `Datos_analiticos_proyecto/`.

## Referencias conservadas

Los originales recuperados `1. Extracción de estimados.ipynb`, `2_ procesamiento de producción real.ipynb` y `3_Benchmark estimado ingeniero.ipynb`, y el resumen 2026 `03_benchmark_estimado_ingeniero.ipynb`, sirven para consultar las reglas de partida. No ejecutar su antigua cadena de exports; usar las limpiezas y el análisis vigentes.

`00_entendimiento del estimado.ipynb` conserva notas/fotos de campo y `Extracción SQL/01_exploracion_bases_produccion.ipynb` conserva el estudio SQL; su código está comentado para lectura documental.

Recorrido completo: guía de la raíz. Diseño analítico: `METODOLOGIA.md`.

## Revisión en GitHub

Las cinco limpiezas oficiales, el complemento WebFlor local y 06–09 conservan ejecución completa sin errores y salidas visibles. `Lectura.ipynb` muestra la base vigente. Se publican código, documentación, tablas de revisión y gráficas dentro de los notebooks; no se publican los archivos de datos Excel/CSV/Parquet.

Los notebooks originales de referencia conservan su código y el estado histórico disponible, que puede ser parcial o contener errores antiguos. No se han reejecutado sus exportaciones retiradas ni sus conexiones SQL. No confundirlos con los notebooks oficiales ejecutados. Para reproducir el flujo se necesitan las fuentes locales autorizadas; GitHub permite revisar los resultados ya guardados.
