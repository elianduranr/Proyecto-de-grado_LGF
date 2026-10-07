# Contexto vigente: clima y curvas de GAITANA

Alcance exclusivo de modelos: GAITANA, tallos reportados. No ampliar a ARABELLA por instrucción del usuario. GAITANA PPTO permanece separada. Guía única: GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md.

Clima limpio actualizado hasta el 21 de septiembre de 2026 para GAITANA. El notebook 18 audita lluvia, cobertura y asociaciones con volumen y desplazamiento, usando objetivos cerrados antes del 7 de julio de 2025. El centro real menos el teórico sobre cinco semanas no prueba retraso fisiológico. Se analizan 40 ventanas meteorológicas y 28 de lluvia sin superposición; sus intervalos incluyen cero.

Los pilotos no tienen finca explícita. El notebook de procedencia 01 exige bloque, cama, clave comercial y fecha de siembra coincidentes, y registra la primera evidencia disponible. La cama 64A es distinta de 64. En la edición 2026 hay 241.564 observaciones atribuibles a GAITANA, 202.912 desconocidas y ninguna identificada inequívocamente como ARABELLA. La curva compartida no implica mezcla comprobada de fincas. Cobertura de plantas de GAITANA en 2026: 79,12 % compartida y 74,78 % local. Se conservan las cantidades originales.

El notebook 19 compara Sin_clima, Clima_basico, Clima_ampliado y Curva_Gaitana_clima con los mismos parámetros y cortes. Selección anterior a 2026: Sin_clima. WAPE principal: 19,46 %, frente a 19,74 % del ingeniero. Es una evaluación retrospectiva. El diario 05 distribuye ese total con los pesos diarios actualizados: WAPE reconciliado 27,27 % y autónomo 26,72 %. El notebook 16 explica el candidato de 19; el 17 conserva el inventario de referencias. Los notebooks 19 y diario 05 incluyen train/test de la selección actual. El sesgo se expresa como predicción menos real: positivo significa sobreestimar.

No inventar curvas, IDs ni fincas. Conservar el catálogo central de variedades y la auditoría inicial de calidad. Las diferencias actuales frente a Antes_calidad también incluyen el clima nuevo. No imputar objetivos ni convertir faltantes diarios en ausencia de corte. No usar clima futuro observado. Quedan pendientes disponibilidad histórica de fuentes, unidades de lluvia, equivalencia exportable y utilidad operativa.

El Markdown contiene el escrito; actualizar_word.py genera el Word. Los notebooks generan las figuras y las conclusiones requieren revisión cuando cambian los datos. No modificar fuentes originales ni publicar datasets. No se ha solicitado push de esta revisión.

El notebook final 20 descompone el error del mismo panel estricto de 19 por producto, color y variedad. Mantiene H1 separado y los horizontes individuales, aportes aditivos al WAPE y sesgo, variabilidad, cambios ex post y estabilidad temporal. No reentrena ni selecciona modelos por segmento. MINICARNATION domina el error por volumen; CARNATION concentra una desventaja importante en H3–H5. El detalle queda en eda_origen_error y en la sección 5.6 del escrito.
