# Decisiones analíticas pendientes

## Reglas vigentes

- Semana 53 → semana 1 siguiente, preservando la fuente.
- Recuperar estimado faltante del siguiente archivo disponible del mismo año; mantener origen solicitado y archivo real.
- Conservar la imputación original de Tipo Corte, identificada como retrospectiva.
- Benchmark: unión estricta y recuperación 1:1 por variedad, sin perder producción ni inventar ceros.
- Precisión por producto/color/variedad y horizonte, no sólo total.
- WebFlor puede mantener una referencia vigente sin recalcularla semanalmente.
- Código autocontenido y ocho datasets oficiales en una sola carpeta.
- Edad del plano validada contra su fórmula AL1; edad al lunes conservada por separado.
- Producción reciente como hipótesis de actualización: evaluada en 07/08/09, sin atribuir causalidad.

## Confirmar antes de validación operativa

1. Equivalencia de tallos reportados y ESTI. EXPORTABLE; filtros productivos aplicables.
2. Fechas efectivas de emisión, publicación y correcciones posteriores.
3. Semana sin reporte: cero, inactividad o ausencia de registro.
4. Correspondencias comerciales de color/variedad y ambigüedades que no admite la unión 1:1.
5. Soporte de curvas piloto, segmentos ambiguos y disponibilidad real de planos. La referencia AL1 de la fórmula ya está comprobada; no equivale a publicación.
6. Unidades, estación, zona horaria y latencia del clima.
7. WebFlor: disponibilidad, ámbito, integridad de la referencia y eventos que la reemplazan o retiran.
8. Costes de sobre/subestimación por color/variedad, incluyendo bajo volumen.
9. Protocolo temporal y evaluación prospectiva; los periodos ya inspeccionados son desarrollo, no test intacto.
10. Sesgo y escala en variedades pequeñas: Ridge tiene menor WAPE global, pero resulta peor que el último valor en el segmento de bajo volumen. No aprobar por el agregado.

## Qué ya se probó

09 compara baselines, Ridge y boosting con cortes temporales y mismos casos. La memoria productiva mejora el boosting comparable; el bloque climático no aporta mejora conjunta en este experimento. Una semana adicional de demora deteriora el resultado. La corrección implementada es sobre media4, no WebFlor; la guía detalla cifras y cobertura.

La guía de la raíz describe el flujo; `METODOLOGIA.md` define el diseño analítico vigente.
