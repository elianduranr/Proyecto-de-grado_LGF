# Preparación para la próxima revisión del proyecto

## Material vigente

- Recorrido de fuentes a resultados: `GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md`.
- Diseño analítico: `METODOLOGIA.md`.
- Limpiezas: cinco notebooks autocontenidos en `Notebooks/Limpieza data, Notebooks y Scripts/`.
- Base/EDA/features/modelos: 06–09 en `Notebooks/Analisis/`, ejecutados.
- Datos procesados oficiales: `Datos_analiticos_proyecto/`.

## Qué revisar con el tutor

1. Conservación íntegra de producción real y controles de uniones.
2. Recuperación de estimados no enviados mediante el siguiente archivo disponible, con procedencia y desfase.
3. Diferencia entre reconstrucción retrospectiva y predictor disponible al origen.
4. Correspondencia de color/variedad, primero estricta y luego recuperación 1:1 del remanente.
5. Cobertura de plantas, edades y curvas; no extrapolar un proxy sin soporte.
6. Coherencia de unidades: tallos reportados frente a exportables.
7. Estabilidad de asociaciones climáticas y productivas por serie y periodo.
8. Disponibilidad y vigencia real de las proyecciones WebFlor archivadas.
9. Cohortes comparables por horizonte antes de comparar métricas.
10. Comparación temporal ejecutada: la memoria productiva ayuda, pero el menor WAPE global no garantiza precisión en variedades pequeñas. Revisar cobertura y sensibilidad a demora.

## Preguntas agronómicas

- ¿Qué factores aplica el ingeniero después del potencial por plantas y curva?
- La edad reportada del plano usa AL1 y redondeo Excel; la edad al lunes se conserva aparte. ¿La edad de la curva piloto usa la misma convención agronómica y cuándo se recibió cada plano?
- ¿Qué representan los índices internos, aprovechamiento, mortalidad y porcentaje exportable?
- ¿Cómo distinguir cero productivo, inactividad y registro ausente?
- ¿Cuándo se conoció realmente cada entrega y qué revisiones posteriores contiene?

No se presentan métricas de pipelines anteriores como evidencia de la base vigente. Los resultados que se discuten son los visibles en los notebooks actuales, con sus coberturas y limitaciones.
