# Datasets oficiales

Ocho Parquet, sin subcarpetas por ejecución ni formatos duplicados. Cada proceso reemplaza su propia salida. Los originales no se modifican.

| Archivo | Grano y función |
|---|---|
| produccion_real_limpio.parquet | Movimiento Excel por archivo/hoja/fila; tallos, dimensiones y limpieza original de Tipo Corte identificada |
| planos_siembra_limpio.parquet | Línea de un plano original, edición seleccionada y banderas de calidad |
| curvas_variedad_limpio.parquet | Observación piloto desduplicada entre entregas, con trazabilidad y validez |
| clima_limpio.parquet | Medición por finca/instante o registro inválido identificado; sin mezclar copias |
| estimados_semanales_limpio.parquet | Línea de estimado por archivo/fila_cache/origen solicitado; H1–H5, archivo exacto o posterior |
| proyecciones_webflor_limpio.parquet | Registro actual/archivado/captura previa, con periodicidad e identidad; no sumar categorías |
| coeficientes_webflor_limpio.parquet | Coeficiente interno curva/edad/ciclo, con dimensiones y unidad |
| base_analitica.parquet | Gaitana/producto/color/variedad/semana con producción observada y variables auxiliares |

## Base analítica

Llave: `finca, producto, color, variedad, semana_inicio`. 44.053 filas, 108 columnas, 663 series comerciales, semanas 2021-01-04 a 2026-08-31 y 327.991.200 tallos reportados. No denominarlos exportables sin confirmar equivalencia.

La producción es la tabla izquierda. Los estimados de distintos horizontes son columnas, no copias para sumar. Las fuentes auxiliares sin producción siguen en sus limpios.

## Columnas importantes

- `tallos_reales, registros_corte, dias_con_reporte`: producción observada agregada.
- `temperatura_*, humedad_semana, radiacion_semana, dias_clima`: contexto climático observado; rezagar para modelar.
- `plantas_plano, area_plano, camas_plano, edad_media_plano`: estado del plano coincidente y edad ponderada.
- `fecha_referencia_edad_plano`: referencia AL1 para validar la fórmula de edad, no publicación. La edad media representa semanas completas al lunes nominal, no la edad redondeada en AL1.
- `cobertura_curva, plantas_ambiguas, potencial_descriptivo`: soporte y proxy empírico, no WebFlor exacto.
- `estimado_ingeniero_h1…h5`: cantidad agregada de la solicitud.
- `origen_ingeniero_h*`: origen solicitado; `origen_archivo_ingeniero_h*`: origen nominal del archivo realmente usado.
- `archivo_posterior_ingeniero_h*, desfase_archivo_ingeniero_h*`: recuperación por entrega faltante.
- `metodo_union_ingeniero_h*, color_estimado_ingeniero_h*`: coincidencia estricta o recuperación por variedad y color fuente.
- `desviacion_ingeniero_h*`: real menos estimado; no error WebFlor.
- `webflor_estado_descargado`: referencia actual, sin sumar histórico/diario.
- Banderas de confirmación: no atribuyen fechas o equivalencias no acreditadas.

Los conteos, coberturas y uniones se muestran en los notebooks y en la guía. Faltante no equivale a cero. Edad válida: 42.818 filas (97,20%); potencial descriptivo: 9.058 (20,56%). La cobertura del potencial y las fechas de disponibilidad siguen siendo limitaciones.

07, 08 y 09 consumen esta base sin crear otra tabla de modelos. Sus resultados están en memoria y en los notebooks ejecutados. Sólo las columnas temporalmente admisibles definidas en 08/09 entran como predictores; no usar indiscriminadamente las 108 columnas.
