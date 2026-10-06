# Contexto vigente del proyecto — revisión del 6 de octubre de 2026

Objetivo: anticipar producción por producto/color/variedad en GAITANA mediante proyecciones propias, producción reciente y clima. Unidad observada: tallos reportados; equivalencia exportable pendiente. GAITANA PPTO es distinta.

La guía única de estudio y ejecución es GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md. Flujo: catálogo 00 → auditoría → proyecciones de todos los años → 10/11/12/13 → diario 01 → 14 → 15 y diario 02/03. No regenerar 06–09 ni bases antiguas. Los notebooks activos son autocontenidos y las salidas tienen nombres fijos.

Catálogo central: Notebooks/Extracción SQL/Datos/01_maestros_y_geografia/Catalogo_analitico, generado desde CSV originales intactos. Identidad comercial única no exige ID SQL único; se mantienen todos los códigos. Son 2.915 identidades, 53 con múltiples IDs y 33 con códigos de obtentor diferentes para revisar. La agrupación comercial no certifica identidad genética. No forzar equivalencias ni fusionar colores distintos.

La auditoría corrige copias equivalentes de pilotos y pérdidas por IDs. En edición 2026 recupera 74.304 observaciones utilizables, 13.963 con efecto en alguna ventana. Mantiene ciclos estrictos y cantidades. Teoría completa global: 21,25 % de 211.001 casos observados, antes 17,96 %. No equivale a cobertura de plantas ni a todas las variedades cubiertas. Planos/curvas alimentan únicamente las proyecciones previas, no directamente los modelos.

Se propagaron las correcciones a la cadena semanal. El experimento 15 compara calidad separadamente de arquitectura, memoria, revisiones y mezcla. Memoria_larga obtiene 19,59 % WAPE frente a 19,74 % del ingeniero sobre 15.838 casos. Gana H1/H2; H4/H5 siguen peor y RMSE favorece al ingeniero. Intervalo exploratorio de ventaja: −1,16 a +1,48 puntos; no demuestra superioridad estable. Antes_calidad 20,04 %; misma arquitectura corregida 20,06 %. Revisiones y combinación 19,65 %; pesos elegidos con datos previos a 2026, iguales a 1 del modelo.

El diario distingue predicción autónoma y reparto coherente a H1, con variables congeladas al lunes. Conserva como entrada el sistema 14 corregido, sin escoger retrospectivamente el ganador 15. SARIMA/SARIMAX es un piloto de tres series con clima pasado lag7; no extrapolar a toda la finca. Ausencias no son ceros.

Conservar movimientos legítimos, procedencia y cantidades por llave. No sumar targets repetidos como producción física. Separar archivos posteriores del ingeniero y uniones recuperadas por color. Entrenar sólo con objetivos cerrados y ajustar imputación en train. La disponibilidad de fuentes es nominal/supuesta; 2026 se examinó iterativamente y no es test prospectivo intacto.

Trabajo escrito: Desarrollo_del_documento.md y Estructura_actualizada_con_resultados.docx sincronizados mediante actualizar_word.py. Integra contexto, curvas, EDA, auditoría, modelos y discusión. Conservar el esquema original del usuario. Literatura verificada, PCA/MCA/PDN y validación empresarial siguen pendientes; no inventar resultados o beneficios económicos.


## Revisión diaria e interpretación del 6 de octubre

Diario 04 cambia sólo el total semanal por Memoria_larga. Boosting reconciliado: WAPE 27,45 % frente a 28,29 % anterior; autónomo 26,76 %. Sobre 274 semanas con siete reportes se invierte el ranking: uniforme 24,52 %, reconciliado 33,77 %. Se mantienen faltantes y límites de registro. El piloto conserva SARIMAX autónomo 24,49 % en 135 días; con nuevo total, 30,97 %.

Semanal 16 reproduce agosto y genera importancia por permutación, no SHAP ni causalidad. Semanal 17 reconstruye ajustes para train/test: no confundir train del último ajuste con test acumulado. El escrito, sus figuras y la guía incluyen estos análisis y el orden exacto de ejecución. No se alteró el candidato semanal ni se cambió su benchmark previo.
