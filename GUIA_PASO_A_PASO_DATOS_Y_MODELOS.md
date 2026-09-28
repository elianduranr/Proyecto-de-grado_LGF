# Guía paso a paso de datos, limpieza, benchmark y modelos

Esta es la guía del flujo vigente. Todo se trabaja localmente en este proyecto. Las fuentes Excel no se modifican; los notebooks contienen su código y sus controles. No hay un framework propio ni múltiples versiones de los datasets.

## 1. Objetivo del proyecto

Entender por qué la producción observada se aparta del estimado y preparar formas de mejorar el pronóstico por producto, color y variedad.

El mecanismo agronómico es: siembras y población → edad del cultivo → curva/rendimiento esperado → producción, con posibles variaciones por clima y condiciones productivas. La producción reciente puede aportar información para actualizar una estimación. Una asociación estadística no demuestra causalidad.

Primero aseguramos fuentes, limpieza, uniones y cobertura. Ahora están ejecutados el EDA y una primera comparación temporal de modelos. No se declara un algoritmo ganador para operación.

La hipótesis central es **usar la producción real reciente para actualizar lo esperado en las semanas siguientes**. Es información sobre el estado productivo, no una afirmación de que producir hoy cause biológicamente la producción futura.

## 2. Dónde está cada cosa

Todas las rutas siguientes son relativas a la raíz del proyecto.

| Elemento | Ruta |
|---|---|
| Originales Excel | `Datos/` |
| Cinco limpiezas oficiales | `Notebooks/Limpieza data, Notebooks y Scripts/` |
| Complemento WebFlor | `Notebooks/Extracción SQL/02_webflor_complemento_necesario.ipynb` |
| Construcción de base, EDA, features y comparación | `Notebooks/Analisis/` |
| Única carpeta de procesados | `Datos_analiticos_proyecto/` |
| Metodología resumida | `METODOLOGIA.md` |

```text
Originales Excel ──→ limpiezas 01–05 ──→ cinco Parquet limpios
Originales SQL  ──→ complemento SQL ──→ dos Parquet limpios
                              ↓
                     06: base_analitica.parquet
                              ↓
                        07: EDA/benchmark
                              ↓
                  08: variables conocidas al origen
                              ↓
                  09: modelos y comparación temporal
```

Sólo existen ocho datasets procesados oficiales. Al reejecutar se reemplaza la misma salida. EDA, features y modelos trabajan en memoria, sin crear otra base_modelos ni un CSV por cada resultado. Sus tablas y gráficas quedan visibles en los notebooks ejecutados.

## 3. Qué fuentes se utilizan

| Familia | Originales | Qué aporta |
|---|---|---|
| Curvas por variedad | 24 Excel en `Datos/Curvas por variedad/2021` … `2026` | Observaciones de pilotos, plantas, edad y rendimiento empírico |
| Clima | 6 Excel en `Datos/Clima/` | Mediciones de finca; las entregas repiten parte del histórico |
| Estimados | 184 Excel en `Datos/Estimados semanales/2023` … `2026` | Estimados del ingeniero, con entregas faltantes y archivos ajustados |
| Planos | 294 Excel en `Datos/Plano de Siembras/2021` … `2026` | Estado semanal de camas, plantas, área, variedad y edad |
| Producción real | 6 Excel en `Datos/Producción real/` | Movimientos reportados, fuente oficial de cantidades reales |
| WebFlor | Descargas originales seleccionadas en `Notebooks/Extracción SQL/` | Proyecciones almacenadas y coeficientes internos, distintos de los Excel |

Cada limpio conserva procedencia. El inventario de archivos concreto se muestra en el notebook correspondiente. No se asume que la carpeta indique siempre el año correcto: en estimados se prioriza el año del nombre, como en la extracción original.

Las entregas del ingeniero no cubren emisiones nominales desde 2021: empiezan en 2023. Eso no elimina la producción de 2021–2022.

## 4. Qué notebook se ejecuta

En `Notebooks/Limpieza data, Notebooks y Scripts/`:

1. `01_limpieza_curvas_variedad.ipynb` → `curvas_variedad_limpio.parquet`.
2. `02_limpieza_clima.ipynb` → `clima_limpio.parquet`.
3. `03_limpieza_estimados_semanales.ipynb` → `estimados_semanales_limpio.parquet`.
4. `04_limpieza_planos_siembra.ipynb` → `planos_siembra_limpio.parquet`.
5. `05_limpieza_produccion_real.ipynb` → `produccion_real_limpio.parquet`.

Son independientes. Seleccionar el Python de `entorno_tesis` y ejecutar de arriba abajo. La lectura XML de los 184 Excel de estimados puede tardar decenas de minutos: sus cachés internas suman aproximadamente 9,76 GB descomprimidos. No es una consulta SQL.

Después ejecutar el complemento SQL en modo local y, en `Notebooks/Analisis/`, 06 → 07 → 08 → 09. Los ocho datasets oficiales se guardan en `Datos_analiticos_proyecto/`. 09 contiene explícitamente la preparación necesaria para ejecutarse desde la base, sin importar scripts propios ni necesitar variables de otro kernel.

Los notebooks originales recuperados —extracción 1, producción 2, benchmark 3 y `Notebooks/03_benchmark_estimado_ingeniero.ipynb`— se conservan para consultar y contrastar la lógica. **No forman una segunda cadena de ejecución:** sus exportaciones antiguas no deben regenerarse. Las reglas vigentes están trasladadas a 03/05/06/07.

## 5. Producción real: limpieza y conservación

05 lee todas las hojas de detalle configuradas, incluidas las particiones de 2023, 2024 y 2025. No suma hojas resumen.

Se conservan las 15 columnas productivas de la lógica original. Se eliminan únicamente filas sin información en todas esas columnas; no se desduplican movimientos porque parezcan iguales. Se normalizan nombres, fechas, enteros y horas, conservando libro, hoja y fila Excel.

### Tipo Corte

Se mantiene la regla del benchmark original: completar faltantes con la moda de producto/color/variedad en la semana anterior, actual y siguiente, por libro. Se aplica el desempate estable de la limpieza multianual.

Se conservan `tipo_corte_original` y `tipo_corte_imputado`. No se modifica cantidad de tallos. Esta imputación puede mirar una semana posterior y **no se usa como predictor conocido al origen**.

Lote queda entero nullable y Hora Corte se normaliza a HH:MM:SS; ambos conservan su valor original.

### Cantidades verificadas

La fuente limpia contiene **6.389.201 movimientos**. Gaitana conserva **4.654.552 movimientos y 327.991.200 tallos**.

La comparación semanal por finca/producto/color/variedad/semana conserva **44.053 llaves**, sin diferencias en cantidades. Se controla cada hoja y cada unión, no sólo el total general.

El alias documentado `¡ → GAITANA` se mantiene. `GAITANA PPTO` no se confunde con `GAITANA`. Otras fincas permanecen en el limpio; el panel principal del proyecto filtra Gaitana.

La unidad es **tallos reportados**. Su equivalencia con producción exportable requiere confirmación.

## 6. Estimados: extracción y recuperación de entregas faltantes

Esta parte conserva la lógica del notebook de benchmark indicado por el usuario.

### 6.1 Leer el contenido de los Excel

Los registros están en las cachés internas de sus tablas dinámicas. Se leen desde el Excel original, vinculando la definición y los registros por la relación XML y reconociendo los campos del estimado. No se trata de crear cachés externos.

Se extrae TIPO=ESTIMADO y se conservan finca, producto, color, variedad, cantidad, año y semana objetivo y procedencia. El campo de cantidad es ESTI. EXPORTABLE.

### 6.2 Elegir un archivo principal

Se excluyen los archivos identificados como ajustados de la selección principal. Los originales permanecen intactos.

Para un mismo año/semana, se aplica la prioridad del proceso original: preferir marca ENVIO, penalizar sello de descarga y desempatar por nombre. No se suman dos entregas para crear un estimado mayor.

El año se toma del nombre del archivo y, sólo si no aparece, de la carpeta. Por ejemplo, `Estimado Sem 01-09 2024 Gaitana-Arabella.xlsx` corresponde a 2024 aunque esté guardado bajo 2023.

### 6.3 Recuperar una semana no enviada

Para cada año se solicitan las semanas desde 1 hasta la última semana disponible:

1. Si existe archivo de esa semana, se utiliza.
2. Si no existe, se utiliza el siguiente disponible del mismo año.
3. Si tampoco existe uno posterior, no se inventa una entrega.
4. Se extraen del archivo elegido las semanas objetivo de la solicitud; no se desplaza el objetivo para ocultar el faltante.

Ejemplo comprobado:

| Semana solicitada | Archivo disponible utilizado | Objetivos |
|---|---|---|
| 2026-S02 | Archivo de 2026-S03 | S02, S03, S04, S05, S06 |

La extracción de ese caso recupera **970 líneas H1–H5**, con cantidades contrastadas contra las funciones originales. Que el archivo se llame S03 no obliga a extraer desde S03: su caché también contiene S02.

Si el archivo posterior no contiene alguno de los objetivos, ese horizonte queda sin datos. Se muestra en los controles; no se inventa una cantidad ni se reemplaza con cero.

### 6.4 Mantener separados solicitud y procedencia

- `origen_solicitado`: semana que se intenta reconstruir.
- `origen_nominal`: semana del archivo realmente utilizado.
- `semana_inicio`: semana objetivo.
- `horizonte`: H1–H5 respecto a la solicitud.
- `horizonte_nominal`: distancia respecto al archivo, que puede diferir.
- `archivo_es_posterior` y `diferencia_semanas_archivo`: recuperación y desfase.
- `archivo_origen, fila_cache`: ubicación del registro fuente.

Una línea fuente puede servir a varias solicitudes. La llave del limpio es archivo/fila_cache/origen_solicitado. Son casos de estimación distintos, **no volúmenes de producción para sumar entre horizontes**.

La recuperación sirve para reconstrucción y benchmark descriptivo. No prueba que ese archivo estuviera disponible cuando se habría pronosticado la semana solicitada. Esos casos deben distinguirse en la evaluación temporal.

## 7. Planos, curvas y clima

### Planos

Se reconocen encabezados de la hoja Datos y se normalizan dimensiones, plantas, área, siembra y edad. Un plano es una observación semanal del estado de camas, no nuevas siembras para sumar entre semanas.

Una bandera selecciona la edición identificada como actualizada. Se señalan segmentos ambiguos y discrepancias de edad. El libro 2022-S02 no trae la hoja Datos: 293 de los 294 libros aportan registros; no se inventan los faltantes.

Salida: **3.252.152 líneas**. La base descriptiva relaciona el plano de la misma semana. Para pronosticar, 08/09 seleccionan un plano anterior bajo una regla de disponibilidad separada, descrita en la sección 11.

Se encontró y corrigió una diferencia importante: la fórmula de edad del Excel es `ROUND((AL1 − fecha_siembra)/7, 0)`. Está reconocida en los **293 libros con hoja Datos**. AL1 puede ser posterior al lunes del nombre del archivo; comparar directamente la edad reportada contra ese lunes marcaba falsos errores.

Se conservan `fecha_referencia_edad`, `edad_esperada_referencia`, `edad_calculada` al lunes y las banderas de discrepancia. La inconsistencia se valida contra la fórmula fuente; el panel usa edad en semanas completas al lunes. En las ediciones elegidas de Gaitana, las discrepancias frente al lunes eran 1.089.090; las inconsistencias contra la referencia correcta son 23.835. No se borraron filas ni se relajaron los requisitos de soporte de las curvas. **AL1 no acredita fecha de publicación.**

### Curvas

Los libros acumulativos repiten observaciones. Se desduplican por identidad de evento/piloto/siembra/semana, conservando procedencia y conflictos. Las plantas del piloto sólo se vinculan cuando la relación es inequívoca.

Salida: **549.870 observaciones**, con bandera de validez. Son curvas empíricas, no parámetros internos WebFlor.

En 06 se calcula un potencial descriptivo: plantas por edad × mediana del rendimiento correspondiente. Se exige soporte ≥10 observaciones y cobertura ≥90% de las plantas, sin segmentos ambiguos. No se extrapola el resto.

Ese potencial usa el histórico completo de curvas: **no es un pronóstico fuera de muestra ni una feature histórica admisible**. Su cobertura es limitada y debe mejorarse antes de considerarlo un baseline general.

### Clima

Se identifican mediciones por finca/instante y repeticiones entre entregas. Los conflictos y horas inválidas se marcan dentro del mismo limpio. No se mezclan copias como si fueran mediciones adicionales.

Salida: **187.134 registros**. Para unir al panel se agregan mediciones → medias diarias → medias semanales. Así no pesa más un día sólo por tener más muestras.

Se conservan controles de cobertura. Gaitana tiene clima hasta 2026-07-28; la producción llega más adelante. Unidades, estación y algunos sufijos horarios necesitan confirmación. Para pronosticar se usa clima pasado, nunca clima real futuro.

## 8. SQL: únicamente los complementos necesarios

El notebook SQL usa `ACTUALIZAR_SQL=False` por defecto. Esta ejecución trabaja con archivos locales y **no consulta el servidor ni genera proyecciones**.

Se conservan 16 objetos como entradas: proyecciones semanal actual, histórica semanal e histórica diaria; coeficientes y curvas/ciclos; siembra actual/histórico/log para identidad; y maestros de finca, ubicación y clasificación de variedades.

Los joins y dependencias se procesan en memoria. Sólo salen:

- `proyecciones_webflor_limpio.parquet`: **1.686.034 registros**.
- `coeficientes_webflor_limpio.parquet`: **128.567 coeficientes**.

Siembras e historial SQL no se exportan como otro plano: aportan identidad a proyecciones archivadas. Los planos Excel son la fuente principal de plantas/edad del panel.

### Qué contiene el archivo de proyecciones

308.449 filas actuales semanales, 1.354.556 archivadas semanales, 22.985 archivadas diarias y 44 observaciones originales adicionales de GAITANA PPTO/2020. Se distinguen estado y periodicidad. **No se suman esas categorías entre sí.**

Sí existe histórico SQL. Lo que no está certificado es que cada archivo sea una corrida completa con fecha de origen conocida. La auditoría puede describir una erradicación o archivo, no una generación.

Una proyección puede permanecer vigente varias semanas sin recalcularse. Para evaluar una corrección histórica debemos conocer cuándo era conocida, su ámbito y cuándo fue sustituida o retirada; no exigir generaciones semanales ni inventarlas.

**Decisión concreta:** no hacer una unión histórica «última auditoría anterior al origen». No es una fecha de emisión acreditada. En Gaitana, la auditoría resulta posterior al cierre de la semana objetivo en aproximadamente 27,66% del estado semanal, 78,53% del archivo semanal y 100% del archivo diario. Tampoco las auditorías anteriores prueban por sí solas disponibilidad. La columna de generación confirmada no tiene valores certificados.

Cuando exista esa evidencia, se podrá usar la última referencia conocida antes del origen, para la misma entidad/objetivo, hasta su reemplazo o retiro. Hoy no se rellena artificialmente esa historia. La lógica SQL documentada de erradicación archiva con una auditoría nueva y la de ajuste puede modificar el final sin cambiarla.

Los coeficientes internos tienen semántica SQL: SemanaDia es edad; el ciclo define días/semanas y base área/plantas. No se les atribuye vigencia histórica desde 2021 sin evidencia.

Los planos no aportan una identificación validada de curva/ciclo SQL y algunas variedades tienen varias curvas. Se conserva el complemento, pero no se elige una arbitrariamente ni se usa como predictor histórico sin vigencia. El catálogo de decisiones de 06 revisa las siete fuentes limpias; aprovecharlas no significa convertirlas todas en columnas predictoras.

Cortes, clasificación e inventario SQL no forman parte del pipeline. La producción oficial es Excel, sin sumar otra representación del mismo proceso.

## 9. Construcción de la base y benchmark

06 lee sólo bases limpias. Una fila principal representa:

`finca × producto × color × variedad × semana objetivo con producción observada`.

La producción de Gaitana es la tabla izquierda. Se agregan clima y planos antes de unir. Se valida N:1 o 1:1 y se rechazan multiplicaciones N:N.

### Estimado frente a real: dos intentos de unión

1. Se agregan las líneas de la solicitud por las dimensiones comerciales y horizonte, como en el benchmark original. Se verifica que corresponden al archivo principal elegido.
2. Unión estricta por finca/producto/color/variedad/semana.
3. Sólo para los pendientes, unión por finca/producto/variedad/semana con unicidad 1:1 en ambos lados.
4. Si hay varios colores candidatos, no se elige uno arbitrariamente: el caso queda pendiente.
5. Se conservan el color real y el color del estimado, junto con `metodo_union_ingeniero_h*`.
6. La marca `archivo_posterior_ingeniero_h*` acompaña la cantidad recuperada.

Los cinco horizontes son columnas; no multiplican las filas ni los tallos reales. Los objetivos sin producción y las referencias no emparejadas permanecen en el limpio de estimados.

El estado actual WebFlor se agrega y relaciona por llave semanal, sin sumar su archivo histórico. Los coeficientes y archivos históricos conservan su propia tabla auxiliar.

La única salida es `Datos_analiticos_proyecto/base_analitica.parquet`. Tiene **44.053 filas, 108 columnas y 327.991.200 tallos**. Cada unión demuestra conservación por llave, no sólo por suma. Muchas columnas describen H1–H5 y su procedencia: no son 108 predictores autorizados ni cinco copias de la producción.

## 10. EDA y métricas

07 lee la base consolidada. Analiza coberturas, producción por dimensiones, plantas/edad/potencial, clima, persistencia productiva y diferencias frente al ingeniero.

Las diferencias se definen como real − estimado: positivo significa que el estimado quedó por debajo de lo reportado. Se muestran error absoluto, sesgo, MAE y WAPE en los casos comparables. El porcentaje individual se restringe a denominadores suficientemente grandes.

Se separan referencias del archivo nominal y reconstrucciones con archivo posterior, y coincidencias estrictas frente a recuperaciones por variedad. No llamar a estas métricas error histórico certificado de WebFlor.

Se excluyen de las métricas los estimados cuya suma está incompleta por cantidades fuente faltantes. Esas líneas permanecen identificadas en la base; no se convierten en cero ni en un estimado completo.

Un faltante no es cero. Un WAPE agregado no basta para evaluar color/variedad. Tampoco se comparan horizontes como si siempre tuvieran la misma población.

### Evidencia para la hipótesis de actualización

07 compara las relaciones dentro de las series, con rezagos distintos para cada horizonte. Medianas de correlación de Spearman entre series con soporte:

| Relación retrospectiva | H1 | H2 | H3 | H4 | H5 |
|---|---:|---:|---:|---:|---:|
| Producción reciente frente a producción futura | 0,855 | 0,734 | 0,617 | 0,524 | 0,455 |
| Tendencia reciente frente a desviación de media4 | 0,457 | 0,322 | 0,211 | 0,120 | 0,056 |
| Desviación reciente del ingeniero frente a desviación futura | 0,460 | 0,356 | 0,233 | 0,183 | 0,121 |

El número de series varía por horizonte: no son poblaciones idénticas ni efectos causales. En la tercera relación se excluyen archivos posteriores, emparejamientos no estrictos y cantidades incompletas; aun así, la emisión real del archivo no está certificada. **La señal es compatible con actualizar pronósticos, pero su utilidad se comprueba fuera del entrenamiento en 09.**

## 11. Features y modelos: qué está funcionando

08 lee la misma base y genera casos origen/horizonte en memoria. Calcula rezagos de calendario 1–3, medias pasadas de 4/8 semanas, desviación de cuatro semanas, tendencia, cambio reciente y producción 52 semanas antes del objetivo cuando existe. Regulariza semanas sin rellenar producción desconocida con cero. Incluye un catálogo de features y una prueba que altera cantidades futuras: las features de orígenes anteriores no cambian.

El origen es el lunes: H1 es la semana que comienza; H5, cuatro semanas después. Son +1…+5 desde la última semana cerrada. Los objetivos futuros se conservan exclusivamente como etiquetas para evaluar después, nunca como X.

Los planos se unen **as-of hacia atrás** con disponibilidad supuesta `max(lunes nominal + 7 días, AL1 + 1 día)`, tolerancia de cuatro semanas desde esa disponibilidad y sin usar observaciones posteriores al origen. Se proyecta la edad desde el lunes del plano; no se inventan nuevas siembras ni erradicaciones. Este dato procede de los planos presentes en el panel con producción, no de un registro exhaustivo de todas las siembras futuras.

El clima usa medias semanales con al menos cinco días y, después, lag1 y medias de cuatro semanas anteriores. Radiación sigue siendo el promedio de la magnitud fuente, no energía acumulada. Lluvia y otras mediciones permanecen en el limpio hasta validar unidades e intervalos. La fecha de cierre es un supuesto de disponibilidad, no una fecha de recepción demostrada.

No utiliza como X: producción objetivo, clima futuro, potencial construido con todo el histórico, Tipo Corte imputado con semana posterior, estimados recuperados como si fueran conocidos antes, ni WebFlor sin origen/vigencia certificados.

### Comparación ejecutada en 09

Se fijan tres cortes: **2025-07-07, 2026-01-05 y 2026-05-04**, ocho orígenes semanales por corte y H1–H5. Entrenan sólo objetivos cerrados antes del corte. El modelo permanece fijo en cada bloque y se actualizan sus entradas al llegar nueva producción.

Requisito común: 26 observaciones históricas y cuatro semanas recientes completas. Todos los modelos principales se evalúan en los **mismos 14.108 casos**, correspondientes a 172 series comerciales. Esto cubre 66,59–78,04% de los casos observados de cada bloque y 97,47–98,83% de su volumen contado por caso. Un objetivo puede aparecer desde varios orígenes: ese volumen no es inventario físico para sumar.

| Modelo o referencia | WAPE desagregado |
|---|---:|
| Media de cuatro semanas | 22,39% |
| Última producción observada | 20,19% |
| Media4 con reacción fija del 50% al último valor | 20,43% |
| Ridge con variables disponibles | 19,60% |
| Boosting sin producción reciente | 25,06% |
| Boosting con memoria productiva | 20,55% |
| Boosting con memoria y siembras | 20,05% |
| Boosting completo, incluido clima | 20,30% |
| Boosting que corrige media4 | 20,44% |

WAPE = suma de errores absolutos / suma de reales en los casos evaluados. No significa porcentaje de aciertos. Son resultados retrospectivos condicionados a los supuestos de disponibilidad y a que exista reporte del objetivo.

**Interpretación, sin escoger ganador:**

- Añadir producción reciente al boosting comparable reduce WAPE de 25,06% a 20,30%: evidencia predictiva inicial a favor de la hipótesis, no causalidad.
- Añadir siembras al modelo con memoria mejora aproximadamente 0,50 puntos; añadir este bloque climático no mejora el resultado conjunto. Esto no demuestra que el clima carezca de efecto agronómico.
- El último valor es mejor en H1 y H2; Ridge mejora la referencia en H3–H5, pero no gana en todos los periodos. H1: 13,97% frente a 17,00% de Ridge; H5: 25,91% frente a 22,54%.
- **Bajo volumen sigue siendo un problema:** en los 564 casos del segmento bajo/nuevo definido con datos de entrenamiento, el último valor tiene WAPE 43,32% y Ridge 131,15%. El menor error global de Ridge oculta fallos de composición. No se aprueba para operación.
- La mediana por serie de Ridge es 28,12%, frente a 25,24% del último valor. Sólo 20,93% de sus casos quedan dentro de ±8% del real. No se ha alcanzado la aspiración operacional del Plan de Proyecto.
- Con una semana adicional de demora, en los mismos 4.533 casos del último bloque, boosting completo pasa de 19,92% a 23,09% WAPE. La puntualidad de la información importa.

El notebook muestra además MAE, RMSE, sesgo, métricas por corte/horizonte/producto/color/variedad, referencia estacional sobre población común y coherencia al sumar variedades. No instala nuevos paquetes ni busca hiperparámetros masivamente.

### Qué significa «ajustar» en esta primera implementación

`media4 al origen + corrección aprendida con información anterior → pronóstico actualizado`

09 muestra cómo cambia el pronóstico de una misma semana al recibir nueva producción, y una **simulación** desde el último origen local, 2026-09-07, para 118 series y H1–H5. No fue emitida en esa fecha ni está actualizada al día de ejecución. La tabla `salida_operativa` vive en memoria y se muestra por variedad y en formato ancho por color; no crea otro dataset.

Esto es pronóstico directo y corrección de una referencia móvil. **No es una corrección WebFlor validada.** La corrección WebFlor necesita origen/vigencia acreditados. El híbrido con curvas necesita curvas estimadas sólo con entregas disponibles antes de cada origen; el potencial retrospectivo no se usó como X.

Siguiente paso razonable: resolver disponibilidad y ausencias/cero, revisar sesgo y escala en variedades pequeñas, y evaluar en un periodo nuevo. No aumentar algoritmos antes de resolver esos puntos. ARIMA/SARIMAX y otros boosting quedan como opciones posteriores, no como una lista que haya que ejecutar sin justificación.

## 12. Controles que hay que revisar

- Filas y cantidades de producción antes/después de limpiar.
- Unicidad física de libro/hoja/fila y de solicitud/registro de estimado.
- Archivos exactos y posteriores; ejemplos 2026-S02 y 2024-S01.
- Calendario: semana 53 pasa a semana 1 del siguiente año, conservando etiquetas originales.
- Horizonte solicitado separado del horizonte nominal del archivo.
- Uniones estrictas, recuperadas y pendientes; nunca N:N accidental.
- Totales por llave y por dimensión reconciliados.
- Cobertura por año de curvas, planos, clima, estimados y WebFlor.
- Variables retrospectivas separadas de predictores disponibles al origen.

La base conserva la producción completa del alcance. Eso no significa que todas las variables auxiliares estén completas ni que la corrección del forecast esté ya validada. Los notebooks muestran qué se conoce, qué se reconstruye y qué falta confirmar.

## 13. Resultado verificado de esta entrega

Las cinco limpiezas y el complemento WebFlor local conservan sus resultados ejecutados. En esta revisión se ejecutaron el control de referencia de edad de 04 sobre todas sus fuentes y su exportación, la reconstrucción 06, el EDA 07, las features 08 y los modelos 09. No se repitió innecesariamente la extracción multianual de producción/estimados ya contrastada. No se consultó SQL. Esta comprobación corresponde a las fuentes locales actuales; al incorporar nuevos archivos se deben repetir los controles.

Revisión final: los diez notebooks activos (cinco limpiezas, complemento SQL local y 06–09) tienen resultados guardados, todas sus celdas de código ejecutadas y ninguna salida de error. `Lectura.ipynb` se reejecutó sobre la base de 108 columnas. Una reconciliación independiente volvió a comparar el limpio de producción contra la base por sus 44.053 llaves: **cero diferencias**. Se conservan los cuatro notebooks originales de referencia y siguen existiendo únicamente los ocho Parquet oficiales, sin scripts propios en Analisis.

### Las ocho salidas oficiales

| Archivo en `Datos_analiticos_proyecto/` | Filas |
|---|---:|
| `produccion_real_limpio.parquet` | 6.389.201 |
| `estimados_semanales_limpio.parquet` | 176.140 |
| `planos_siembra_limpio.parquet` | 3.252.152 |
| `curvas_variedad_limpio.parquet` | 549.870 |
| `clima_limpio.parquet` | 187.134 |
| `proyecciones_webflor_limpio.parquet` | 1.686.034 |
| `coeficientes_webflor_limpio.parquet` | 128.567 |
| `base_analitica.parquet` | 44.053 |

### Pruebas de conservación de la lógica original

- **Estimados:** 184 libros inspeccionados, 178 principales y 193 solicitudes; 15 solicitudes utilizan una entrega posterior. La salida conserva 162.827 líneas de entregas exactas y añade 13.313 líneas de recuperación. Las 162.827 líneas coinciden con la extracción anterior: al comparar sus 162.789 llaves comerciales agregadas, no hay llaves perdidas ni diferencias de cantidades.
- **Horizontes:** 190 solicitudes tienen H1–H5; tres tienen cuatro horizontes porque la caché del archivo elegido no contiene todos los objetivos. No se inventa el horizonte ausente. Los casos concretos se ven en `control_solicitudes` de 03.
- **Caso 2026-S02:** se recuperan 970 líneas desde el archivo S03, con 8.970.811 tallos estimados sumados entre sus cinco horizontes. Esa suma es sólo un control de extracción; no producción de una única semana.
- **Tipo Corte:** 45.906 imputaciones identificadas en el limpio multianual. En 2026, las 11.610 imputaciones coinciden con la función original contrastada. Ninguna modifica tallos.
- **Base analítica:** todas las uniones conservan las 44.053 llaves y sus cantidades individuales, además del total de 327.991.200 tallos.

### Cobertura: qué tiene pareja y qué no

| Variable del panel | Filas con cantidad o valor | Porcentaje aproximado |
|---|---:|---:|
| Producción real | 44.053 | 100,00 % |
| Temperatura semanal | 43.375 | 98,46 % |
| Plantas del plano | 43.152 | 97,95 % |
| Edad ponderada del plano | 42.818 | 97,20 % |
| Potencial empírico admisible | 9.058 | 20,56 % |
| Estimado del ingeniero H1 | 21.850 | 49,60 % |
| Estimado del ingeniero H5 | 21.485 | 48,77 % |
| Estado actual WebFlor coincidente | 4.056 | 9,21 % |

H5 tiene 21.471 pares con cantidad completa para las métricas: 14 sumas parciales se excluyen. La cobertura del ingeniero incluye recuperaciones identificadas; no certifica disponibilidad histórica al pronosticar. La producción de 2021–2022 permanece aunque los archivos del ingeniero comienzan en 2023.

Los Excel originales y los notebooks de referencia se conservan. Los CSV antiguos de extracción de estimados ya no forman parte del flujo: sus reglas están incorporadas y contrastadas en la salida única. Los formatos de solicitudes de calidad de datos de `Datos/` son documentos de trabajo, no bases que deban sumarse al panel.

**Para continuar:** abrir 06 para entender las uniones, 07 para revisar el EDA, 08 para estudiar las variables y 09 para ver los modelos ejecutados y sus limitaciones. No entrenar con todas las columnas indiscriminadamente ni llamar a este experimento una corrección WebFlor validada.
