# Del comportamiento productivo al pronóstico semanal y diario en La Gaitana Farms

**Borrador integrado para revisión académica — octubre de 2026**

Elián Durán · Julián Osorio · Anderson Gonzalez

Universidad de los Andes · Facultad de Ingeniería Industrial · Maestría en Inteligencia Analítica para la Toma de Decisiones

## Resumen

Este trabajo desarrolla un pronóstico semanal de tallos reportados para GAITANA y, como tarea aparte aún en revisión, explora la distribución diaria de H1. El modelo semanal seleccionado antes de evaluar 2026 es HistGradientBoosting sin clima: usa un ajuste para H1–H2 y otro para H3–H5, con los mismos parámetros, y corrige la teoría o la media de cuatro semanas según corresponda. En 16.325 comparaciones, obtiene 19,36 % de WAPE frente a 19,71 % del ingeniero; gana en H1–H2 y en el total, mientras el ingeniero gana en H3–H5. Los resultados son retrospectivos. El pronóstico diario tiene evaluaciones exploratorias y aún no cuenta con una comparación equivalente contra el ingeniero.

Palabras clave: producción florícola, curvas, calidad, clima, pronóstico semanal, distribución diaria, validación temporal.

## 1. Introducción: qué se necesita anticipar y por qué

La pregunta que organiza este trabajo es cuánto corte puede esperarse de cada combinación de producto, color y variedad, con qué anticipación y cómo podría distribuirse durante la semana. La combinación comercial importa porque dos estimaciones con el mismo total de tallos pueden describir disponibilidades muy diferentes. Un exceso en una variedad no compensa automáticamente una falta en otra. Por ello, evaluar únicamente el total de la finca sería insuficiente para el propósito de planeación planteado en el proyecto.

El punto de partida combina tres perspectivas. El plano informa las plantas y composiciones registradas en una fecha; las estadísticas de camas piloto describen rendimientos observados a distintas edades; y el estimado del ingeniero aporta una referencia experta con la cual contrastar el sistema. La producción real permite comprobar lo ocurrido. El clima y el comportamiento reciente del corte se incorporan para estudiar si ayudan a explicar las diferencias entre lo proyectado y lo registrado.

La contribución buscada es construir una secuencia comprensible desde esas fuentes hasta una predicción evaluable. Primero se examina si los registros se pueden unir sin mezclar ciclos ni duplicar cantidades. Después se reconstruyen curvas y proyecciones con cobertura explícita. Finalmente se evalúa si las señales recientes permiten corregirlas y si el pronóstico semanal ayuda a anticipar la distribución diaria. Cada paso responde a una dificultad encontrada en los datos.

### 1.1. Objetivo y preguntas de trabajo

El objetivo general es desarrollar y evaluar un sistema reproducible de pronóstico de producción por producto, color y variedad para GAITANA, que integre proyecciones propias, producción reciente y clima, y permita comparar su desempeño con el estimado del ingeniero.

Las preguntas específicas son: ¿qué parte de la producción puede representarse con las curvas disponibles?, ¿qué revelan las diferencias entre versiones de planos?, ¿qué información reciente ayuda a corregir la teoría?, ¿en qué horizontes funciona mejor el ajuste? y ¿cuánto aporta un modelo diario frente a repartir uniformemente el pronóstico semanal? Estas preguntas conectan la caracterización de datos con resultados verificables.

### 1.2. Alcance de la evidencia

El análisis principal se limita a la finca GAITANA; GAITANA PPTO se conserva como una categoría distinta. La variable efectivamente observada son tallos reportados. Aunque la motivación del proyecto y el estimado del ingeniero se refieren a producción exportable, su equivalencia con esa variable debe ser confirmada antes de presentar los resultados como un pronóstico certificado de tallos exportables.

Se estudian cinco horizontes semanales y los siete días de la primera semana pronosticada. Los periodos ya examinados corresponden a desarrollo retrospectivo. La información se ordena temporalmente para evitar usar producción o clima futuro observado, pero la fecha histórica de publicación o corrección de algunas fuentes no está acreditada. Por tanto, el ejercicio aproxima una situación de pronóstico bajo supuestos de disponibilidad que se hacen explícitos.

## 2. Entender las fuentes antes de construir el pronóstico

### 2.1. Tres cantidades que no deben confundirse

El inventario de plantas, el rendimiento de una cama piloto y los tallos cortados son cantidades distintas. El plano es una fotografía de existencias: si una cama con mil plantas aparece en dos planos consecutivos, no se han observado dos mil plantas nuevas. Las estadísticas piloto permiten relacionar un corte con las plantas de una cama y su edad. La producción real, por su parte, reúne movimientos de corte y se agrega para evaluar los pronósticos. Esta distinción determina los denominadores, las llaves de integración y las reglas para interpretar cambios. [E1–E3]

| Fuente | Qué representa | Papel en el trabajo | Precaución principal |
| --- | --- | --- | --- |
| Planos de siembra | Existencias y composición reportadas en una fecha | Ubicar plantas y edades para proyectar | No sumar fotografías como nuevas siembras |
| Estadísticas y camas piloto | Corte y plantas de observaciones identificadas por cama y ciclo | Estimar rendimiento por variedad y edad | No confundir pilotos con producción total |
| Producción real | Movimientos de tallos registrados | Historia reciente y variable de evaluación | Ausencia de registro no equivale a cero |
| Clima | Mediciones ambientales con frecuencia mayor que la producción | Señales históricas agregadas | Confirmar unidades y disponibilidad |
| Estimados del ingeniero | Pronóstico comercial por entrega | Referencia independiente | Comparar mismas llaves y entregas oportunas |

### 2.2. La edad y el ciclo dan sentido a una curva

Para relacionar un corte piloto con las plantas que lo originaron no basta con que coincida el nombre de la variedad. Una referencia de cama puede aparecer en distintos ciclos. La integración utiliza el archivo, la variedad homologada y la referencia completa de la cama; añade la fecha de siembra cuando existe y, en su defecto, año y semana. Una coincidencia ambigua permanece pendiente. Forzarla podría alterar el rendimiento aun cuando el total de filas pareciera razonable. [E1]

La edad se expresa en semanas completas entre la semana de siembra y la de corte. La curva describe el rendimiento observado para una variedad a cada edad disponible. Es una representación empírica construida con los pilotos utilizables, no una ley biológica validada para todas las camas. Diferencias de época, condiciones de cultivo y representatividad de los pilotos pueden afectar su traslado al inventario de plantas; aquí se reconocen como explicaciones por investigar, sin atribuirles efectos causales no medidos.

### 2.3. Qué cambia cuando cambia un plano

Una ubicación física se identifica mediante finca, invernadero y número de cama. Esa ubicación puede persistir mientras cambia su variedad o su fecha de siembra. Por eso el análisis original separa camas persistentes, apariciones, desapariciones y cambios de composición, e incluye la comparación directa de las semanas 32 y 33. Una aparición en el archivo se interpreta como un cambio reportado; por sí sola no prueba que se haya realizado una nueva siembra. [E1]

Esta lectura evita atribuir toda revisión del pronóstico a la curva. Entre dos planos pueden cambiar las plantas, las edades, la composición, la historia utilizada para estimar rendimientos o la cobertura. El estudio de versiones permite observar el resultado conjunto de esos cambios, aunque no constituye todavía una descomposición causal de sus aportes.

## 3. Análisis exploratorio: qué enseñan los datos sobre el problema

### 3.1. Calidad e historia utilizable de los pilotos

Las camas piloto identifican plantas y ciclos; sus estadísticas registran el corte de esas camas. Se normalizan nombres, espacios y mayúsculas, y se verifica referencia de cama, identidad comercial y ciclo de siembra. Esta correspondencia se mide antes de construir rendimientos por edad. No se utiliza el porcentaje de teoría completa de la base analítica como tasa de éxito de estas uniones. [E9]

La revisión del 19 de octubre conserva los 530.250 registros de estadísticas de la edición 2026 y sus cantidades originales. Hay 510.237 correspondencias únicas. Al restringir a cortes fechados en 2026, 32.986 de 33.039 tienen correspondencia única (99,84 %). El total de la edición incluye años anteriores; no representa exclusivamente la operación de 2026.

| Estado técnico | Historia de edición 2026 | Cortes fechados en 2026 |
| --- | --- | --- |
| ambigua | 4.710 | 52 |
| conflicto_ciclo | 3.383 | 0 |
| llave_incompleta | 10.894 | 1 |
| sin_pareja | 1.026 | 0 |
| unica | 510.237 | 32.986 |

Los estados restantes son controles de referencia, identidad o ciclo, no errores de pronóstico ni edades improductivas. Se mantienen trazables, sin convertirlos en un problema general de la fuente. En los 53 registros fechados en 2026 que siguen pendientes se reportan 13.508 tallos en conjunto (0,15 % de los tallos anotados en esas estadísticas); al ser filas semanales repetidas, no representan tallos físicos únicos. Las observaciones utilizables deben además tener plantas positivas, fecha y edad válidas y corte no negativo. Se conservan los ceros registrados: la vista actual contiene 477.426 observaciones, de las cuales 92.337 tienen corte cero.

### 3.1.1. Corrección verificada de nombres y referencias equivalentes

Se encontró una pérdida evitable: la comparación de candidatos incluía campos originales con diferencias de mayúsculas. Así, dos copias de la misma cama y ciclo podían tratarse como alternativas. En el Excel de clavel 2026, las filas 5908 y 5931 de Camas Piloto corresponden a CAROLINE GOLD-26-3, con igual fecha de siembra y 1.194 plantas; sólo cambia la escritura en mayúsculas/minúsculas. Ahora se compara la identidad normalizada y los atributos del ciclo. Se consulta una sola referencia equivalente, conservando las filas fuente y sin duplicar movimientos de corte.

Cuando falta el nombre de variedad en estadísticas, sólo se recupera si la referencia completa dentro del mismo archivo identifica una única combinación comercial compatible con el producto. En la edición 2026 se recuperan así 399 identidades. No se usa semejanza aproximada de nombres ni se mezclan colores o ciclos.

| Edición | Utilizables antes del 19/10 | Utilizables después | Adicionales |
| --- | --- | --- | --- |
| 2021 | 205.321 | 208.255 | 2.934 |
| 2022 | 257.545 | 262.015 | 4.470 |
| 2023 | 316.185 | 322.344 | 6.159 |
| 2024 | 379.560 | 386.340 | 6.780 |
| 2025 | 410.583 | 443.460 | 32.877 |
| 2026 | 444.476 | 477.426 | 32.950 |

Los libros anuales repiten historia: estas recuperaciones no se suman como observaciones únicas del cultivo. La corrección verifica conservación del corte y de todas las observaciones previamente utilizables, incluidas sus plantas, fechas y edades. Diferencias reales de denominador o fecha permanecen pendientes; no se elige un valor arbitrario. El catálogo común de 00 conserva identidad comercial y códigos de procedencia.

### 3.1.2. Procedencia de los pilotos

Las hojas de estadísticas no contienen la finca. La atribución a GAITANA requiere coincidencia de bloque, cama, identidad comercial y fecha de siembra con un plano. En la edición 2026, 271.872 observaciones utilizables tienen coincidencia atribuible a GAITANA y 205.554 no tienen esa evidencia. No hay coincidencia inequívoca con ARABELLA. Las cifras describen la procedencia comprobada; no permiten asignar los casos desconocidos a otra finca por descarte. [E14]

Las curvas compartidas del proyecto se mantienen para el alcance actual. La curva atribuida a GAITANA se evalúa como sensibilidad y su diferencia de cobertura o WAPE puede reflejar tanto qué pilotos entran como qué edades quedan representadas. No se interpreta esa comparación aislada como prueba de que una finca deba usar una curva propia.

Las curvas y proyecciones se recalculan antes de reconstruir la base y ajustar los modelos.

### 3.2. Cómo se obtiene y cómo se lee una curva

En cada fecha de plano se utilizan las 78 semanas anteriores de historia. Cada observación aporta el cociente entre corte y plantas. Dentro de cada grupo variedad–edad se calcula el promedio de esos rendimientos, después de limitar los extremos con el criterio de 1,5 rangos intercuartílicos cuando existen al menos cuatro observaciones. El dato original permanece disponible para auditoría; con menos observaciones no se aplica ese ajuste. No se extrapolan edades sin datos. [E1–E2]

La elección del promedio es relevante: la curva utilizada promedia rendimientos de observaciones, mientras que algunos resúmenes del EDA calculan suma de cortes dividida por suma de plantas observadas. Este último es un promedio ponderado por plantas y su denominador acumula exposiciones planta–semana; no cuenta plantas únicas. Ambos resúmenes describen aspectos relacionados, pero no son intercambiables.

Para leer una curva se deben mirar conjuntamente el rendimiento y su soporte. Una edad sostenida por muchas observaciones tiene una base empírica diferente de otra con una sola observación. Se conserva el ejemplo de Solomio–Ard elegido en la revisión inicial, ahora recalculado con las correcciones, para observar su soporte sin escogerlo por un buen error de predicción. Los huecos se mantienen y el número de observaciones se presenta en un panel separado. La figura ilustra la lectura del procedimiento; no representa por sí sola todas las variedades. La agrupación utiliza la identidad comercial y la edad; los IDs del maestro se conservan como trazabilidad.

![Figura 1. Curva empírica y soporte por edad; ejemplo inicial de Solomio–Ard recalculado tras la auditoría. Fuente: curvas de la edición 2026, último plano disponible, E2.](Figuras_resultados/curva_y_soporte.png)

En el ejemplo de Solomio–Ard, el soporte se concentra en las edades más tempranas del tramo observado y disminuye considerablemente después. Aparecen además puntos aislados por encima de doscientas semanas, respaldados por una sola observación por edad. Su presencia exige revisar fechas y ciclos con el equipo agronómico antes de interpretar esos rendimientos como un comportamiento representativo. No se eliminan ni se unen visualmente a través de las edades ausentes. La curva hace visible así una necesidad concreta de revisión de calidad que quedaría oculta si se mostrara únicamente la proyección agregada.

La producción teórica de una semana se obtiene multiplicando las plantas de cada cohorte por el rendimiento correspondiente a su variedad y edad proyectada, y sumando los aportes cubiertos. Si una cohorte no tiene rendimiento disponible, su aporte es desconocido. La suma calculada en ese caso es parcial, aunque pueda verse como un número perfectamente válido en una tabla. Esa distinción es central para interpretar las proyecciones y para decidir cuándo el modelo puede corregirlas.

Normalizar aquí tiene dos sentidos concretos. Homologar nombres permite unir la misma combinación de producto, color y variedad sin borrar diferencias comerciales; dividir corte entre plantas expresa rendimiento en tallos por planta y permite comparar observaciones con tamaños distintos. No se escala la curva para que su suma sea uno ni se ajusta su total usando la producción futura. El recorte de extremos limita rendimientos atípicos dentro de variedad–edad; no borra ceros reportados ni completa edades ausentes. Por ejemplo ilustrativo, 600 tallos de 1.000 plantas equivalen a 0,6 tallos por planta; una cohorte de 5.000 plantas con ese rendimiento aportaría 3.000 tallos teóricos.

Una cohorte reúne las plantas del mismo plano, finca, producto, color, variedad, clave de curva y fecha de siembra. Puede sumar varias camas; no es sinónimo de cama física. Si las fechas son distintas se conservan grupos distintos, incluso cuando su edad redondeada a semanas coincide. La agregación final suma sus aportes para obtener una serie comercial y una semana objetivo.

### 3.3. Cuándo aplica la curva empírica por edad

Se distinguen tres pasos: vincular cada observación piloto con su cama y ciclo, resumir el rendimiento observado por variedad y edad, y aplicar esos rendimientos a las cohortes del plano en una semana objetivo. La unión identifica correctamente el origen de las observaciones; la curva representa las edades que aparecen en la historia piloto usada para construirla. Son controles distintos y el segundo no indica que se hayan perdido registros reales.

El plano es una fotografía de inventario. La edad de cada grupo se calcula desde el lunes de su semana de siembra hasta el lunes de la semana que se quiere proyectar. Por ejemplo, un grupo de 10 semanas tendrá 15 semanas cinco semanas después; para esa fecha se consulta la curva a edad 15. La fecha del plano determina qué inventario e historia estaban disponibles, pero no sustituye la fecha de siembra al calcular la edad. Se recalculó esta diferencia en los 477.426 cortes utilizables de la edición 2026 y en las 1.064.620 filas de proyección con siembra fechada: todas coinciden con las fechas fuente.

Se procesan 292 versiones seleccionadas entre 2021 y 2026 y diez semanas por plano. El horizonte de construcción se distingue de H1–H5 del modelo, definido desde su fecha de emisión. Las curvas se construyen con las 78 semanas de cortes anteriores a cada plano. Para aplicar una curva a un inventario se consulta la edad de cada cohorte en la semana objetivo. El cálculo directo solo se habilita cuando todas esas edades están representadas en la curva; esto delimita el alcance empírico del método, no la presencia de la producción real ni la calidad del cruce. [E2, E9]

La producción real observada se conserva en los 211.001 casos analizados. En 46.051 casos (21,83 %) la curva representa todas las edades del plano y puede usarse como referencia teórica directa. En los demás, la producción real sigue disponible y, cuando el caso tiene historia suficiente, el modelo usa la producción reciente como referencia. El 21,83 % describe el uso directo de la curva, no la cantidad de datos conservados ni la calidad de los cruces. [E3–E4]

El cruce piloto–cama–estadística se revisó por separado: 99,84 % de los cortes fechados en 2026 tienen correspondencia única. Por ejemplo, si un plano tiene dos grupos de siembra y la curva representa la edad de uno, pero no del otro, no se presenta una suma teórica parcial como total del plano; se conserva la producción real y el modelo admisible puede usar producción reciente.

![Esquema metodológico. La curva define una ruta de referencia; la producción real permanece en la base y el respaldo mantiene el pronóstico. Fuente: E3–E4.](Figuras_resultados/flujo_uso_curva_y_ruta_modelo.png)

![Figura 2. Casos en que la curva representa las edades de todas las cohortes; describe el uso de la referencia directa, no pérdida de producción ni tasa de unión de registros. Fuente: E3–E4.](Figuras_resultados/cobertura_teoria_casos.png)

Que una edad no esté representada por un corte piloto no significa que falte el registro de producción del plano, ni permite asumir que la planta producía cero. El EDA distingue ceros registrados, edades anteriores al rango empírico, huecos entre edades representadas y edades posteriores. Son situaciones sobre el alcance de la curva; solo una regla agronómica confirmada permitiría asignar un cero teórico. El notebook 02 muestra estas situaciones y el ejemplo DINO. Un rendimiento cero que sí fue registrado se conserva como tal.

El ejemplo DINO amarillo de GAITANA muestra por qué la aplicación de la curva y el cruce de camas son preguntas distintas. El plano del 13 de julio de 2026 tiene 25 cohortes para el objetivo del 31 de agosto; la curva piloto usada representa 23 de esas edades. Esto no indica que falten las camas ni la producción real: indica que no se asigna una tasa teórica a las otras dos cohortes y el modelo usa su ruta de producción reciente. Primera edad con corte positivo en la ventana: 14 semanas. Existe un registro de 288 tallos a edad 14, referencia dino-16-175, fecha 2026-02-23. La edad original y calculada coinciden; esto no certifica el dato agronómicamente. A edades 20 y 21 hay ceros registrados en otro piloto. No es evidencia suficiente para imponer cero en 9 o 16. La edad 9 es anterior al rango observado; 16 es un hueco dentro del rango con producción. No se valida rellenar ambos grupos con cero. No se rellenan esos grupos con cero sin una regla de negocio confirmada.

La implicación para el modelo es concreta: se ajusta la referencia teórica cuando puede calcularse completa; en los demás casos se utiliza producción reciente como referencia. No se considera la falta de soporte por edad un error de pronóstico. El error sólo se calcula al comparar una predicción numérica válida con la producción observada.

### 3.4. Qué muestran los cinco últimos planos

Los cinco últimos planos seleccionados corresponden a las semanas 29 a 33 de 2026; en la semana 32 se utiliza la edición actualizada. Para compararlos se alinean las mismas semanas objetivo. Comparar únicamente el primer punto de cada proyección mezclaría fechas de producción diferentes y no mediría una revisión del mismo objetivo. [E2]

![Figura 3. Proyecciones de los planos 29–33 sobre semanas objetivo comunes. Los totales son parciales y corresponden al universo del resumen de planos, no exclusivamente al panel GAITANA del modelo. Fuente: comparación de cinco planos, E2.](Figuras_resultados/revisiones_cinco_planos.png)

Para el objetivo del 17/08/2026, el total teórico parcial pasa de 1.839.272 tallos en el plano 29 a 1.792.025 en el plano 33. Entre los planos 32 y 33 cambia -21.552 tallos (-1,19 %). Las cinco versiones se alinean por objetivo común; no se interpreta la última como más precisa sin contrastarla con producción real.

Esto justifica conservar versiones anteriores como posibles señales del modelo. Permite preguntar si las revisiones contienen información sobre el error futuro, en lugar de asumir que toda actualización constituye una mejora. También obliga a conservar la fecha de emisión: la misma cantidad teórica tiene un significado distinto si se obtuvo una o varias semanas antes del objetivo.

### 3.5. Escala, composición y evolución de la producción real

La base de GAITANA conserva 327.991.200 tallos en 44.053 combinaciones observadas de serie y semana. Miniclavel reúne el 62,87 % del volumen y clavel el 18,47 %; juntos representan 81,34 %. Solomio aporta 8,08 % y Raffine 5,61 %. Por tanto, una métrica agregada sensible al volumen refleja en gran medida el comportamiento de miniclavel. La evaluación debe acompañarse de cortes por producto, color y variedad para reconocer dónde se concentra una mejora o una dificultad. [E3–E4]

![Figura 4. Evolución semanal y composición de tallos registrados en GAITANA. Los totales provienen del panel de producción, sin repetir objetivos de pronóstico. Fuente: E3–E4.](Figuras_resultados/produccion_composicion.png)

Los totales agrupados por año del lunes semanal pasan de 48,70 millones en 2022 a 61,27 millones en 2025. El periodo de 2026 contiene 35 semanas reportadas y 47,62 millones de tallos, por lo que no debe compararse como si fuera otro año completo. Las diferencias anuales pueden combinar cambios de composición, cobertura y nivel productivo. La trayectoria observada describe la fuente; no permite atribuir por sí sola crecimiento a una práctica agrícola específica.

La variación entre series también es amplia: la mediana de producción semanal observada es 3.130 tallos, mientras que el percentil 90 supera 21.076. Esta heterogeneidad explica por qué se estudian modelos compartidos con identificación comercial y por qué el error debe leerse tanto en tallos como en proporción al volumen. El análisis disponible no identifica causalmente picos por festividades o eventos comerciales; incorporarlos exigiría un calendario validado y un contraste específico.

### 3.6. Dónde se separan la teoría y la producción registrada

El error se define como producción real menos teoría; un valor negativo significa que la teoría quedó por encima de lo registrado. El WAPE de abajo es descriptivo para casos completos y no debe equipararse al modelo: cambian período y población. [E4]

| Horizonte | Casos donde la curva representa todas las cohortes | Error medio real − teoría (tallos) | WAPE descriptivo |
| --- | --- | --- | --- |
| H1 | 9.030 | -2.667,70 | 42,07 % |
| H2 | 9.226 | -2.652,62 | 41,23 % |
| H3 | 9.291 | -2.573,83 | 40,17 % |
| H4 | 9.286 | -2.548,91 | 39,65 % |
| H5 | 9.218 | -2.502,81 | 38,79 % |

La diferencia orienta a corregir la referencia teórica donde puede calcularse y a utilizar producción reciente donde falte soporte. Contar producción observada en esas series es posible porque el panel se construye desde los registros reales; que exista esa semana para evaluar no garantiza que la curva empírica contenga todas las edades del inventario.

### 3.6.1. Por qué se probaron rezagos y tendencias

Antes de entrenar se midió si señales de producción conocidas al origen se asociaban con el error posterior de la teoría. Se calcula Spearman dentro de serie comercial y horizonte, para objetivos cerrados antes del 7 de julio de 2025 y al menos veinte pares; luego se toma la mediana entre series. [E4]

| Señal conocida al origen | Mediana H1 | Mediana H5 |
| --- | --- | --- |
| Producción de la semana anterior | 0,251 | -0,022 |
| Cambio entre las dos últimas semanas | 0,190 | 0,070 |
| Promedio de cuatro semanas | 0,123 | -0,032 |

La asociación mayor de la semana previa en H1 motivó probar memoria reciente. No indica cuánto mejorará el pronóstico ni establece causalidad. En 12 y 15 se comprueba su utilidad comparando predicciones en cortes temporales; las entradas diarias se agregan después como un bloque en 14. Las señales largas y conteos se comparan por bloques, porque el EDA no justifica individualmente cada variable.

### 3.7. Clima, error de volumen y desplazamiento del corte

La fuente climática contiene lecturas de GAITANA durante febrero–mayo de 2026; en esos meses predominan registros horarios (aproximadamente 24 al día), mientras que en otros periodos se observan cerca de 48 lecturas diarias. La auditoría adapta el umbral a la frecuencia observada: acepta el día con al menos 80 % de las lecturas esperadas y un rango de al menos 22 horas. Así se usan también los días con medición horaria completa. Temperatura, humedad y radiación quedan disponibles en esos meses; algunas ventanas de lluvia no se calculan cuando faltan registros o hay conflictos, y no se rellenan como lluvia cero. En la figura, rojo significa que una señal/ventana no cumple su regla de cálculo, no que falten datos climáticos de origen, variedades o producción. [E15]

![Figura 5. Señales climáticas disponibles al lunes de emisión con cobertura adaptada a la frecuencia registrada. Las lecturas horarias de febrero–mayo se aprovechan cuando cumplen el umbral; algunas ventanas de lluvia siguen parcialmente disponibles. Rojo indica una señal no calculable bajo su regla, no ausencia de datos fuente. Fuente: E15.](Figuras_resultados/clima_cobertura_origen.png)

El EDA usa objetivos cerrados antes del 7 de julio de 2025. Para error de volumen estudia (real − teoría)/media4 dentro de cada serie y horizonte, con al menos veinte pares donde la curva representa todas las edades de las cohortes. Las medianas de Spearman son pequeñas y hay diferencias entre series. Las variables meteorológicas son comunes a la finca; repetirlas en varias variedades no crea observaciones meteorológicas independientes. El clima de estación no equivale necesariamente al microclima de cada invernadero.

![Figura 6. Asociación del clima previo con el error de la teoría dentro de cada serie. Fuente: E15.](Figuras_resultados/clima_error_teoria.png)

La conexión con los modelos se hace explícita en la nueva sección 1.1 de 18. Se examinan las seis variables semanales originales de 12, las nueve medias climáticas diarias añadidas en 14 y las once columnas ampliadas construidas en 18 para 19. Las primeras resumen semana anterior y cuatro semanas; las diarias, 3/5/7 días; las ampliadas incluyen media14, cambio de 7 frente a 28 días, lluvia y cobertura. No tienen idénticos umbrales de datos válidos, por lo que no se interpreta cualquier diferencia como efecto exclusivo de la longitud de ventana.

Se conserva una lectura por pares disponibles y otra con casos comunes a las 26 columnas, informando casos, orígenes y series. La segunda restringe la historia por datos climáticos no disponibles; no sustituye silenciosamente la primera. El análisis se limita a casos donde la curva representa todas las edades de las cohortes y no demuestra qué sucede en la ruta de producción reciente. La correlación no selecciona automáticamente variables: 12 compara el clima original, 14 añade producción y clima diarios conjuntamente y 19 contrasta clima básico frente a ampliado.

La comparación común de las 26 entradas conserva entre 63,48 % y 65,29 % de casos según horizonte. H1 mantiene 5.078 casos de 142 orígenes; 95 series cumplen el requisito de pares para resumir asociaciones. Las medianas H1 incluyen temperatura semanal previa 0,028, humedad media4 -0,058 y días con lluvia7 0,127. Son asociaciones exploratorias entre producción real y error de teoría, no una medida de efecto causal ni una selección de variables por sí solas.

![Figura 6b. Variables climáticas efectivamente usadas en los modelos: asociación con el error relativo, con pares disponibles y casos comunes. Los blancos indican ausencia de asociación estimable; las cifras no son mejoras de WAPE. Fuente: E15.](Figuras_resultados/clima_variables_modelos.png)

Para desplazamiento se requieren cinco horizontes con teoría y real completos. El centro de producción es la posición de semana (0–4) ponderada por tallos; centro real menos teórico positivo indica corte relativamente más tardío dentro de la ventana. No mide el corte fuera de esas cinco semanas ni prueba un retraso fisiológico: la composición de cohortes y las decisiones de corte también pueden influir. Se agregan series por origen y se separan al menos cinco semanas los orígenes analizados, evitando ventanas objetivo superpuestas.

| Señal previa | Ventanas | Spearman con desplazamiento | Intervalo exploratorio 95 % |
| --- | ---: | ---: | --- |
| temperatura_media14_clima | 40 | -0,149 | [-0,439; 0,217] |
| humedad_media14_clima | 40 | -0,100 | [-0,409; 0,263] |
| radiacion_media14_clima | 40 | 0,202 | [-0,095; 0,479] |
| lluvia_suma28_clima | 28 | -0,093 | [-0,484; 0,279] |

![Figura 7. Clima y desplazamiento relativo del corte en ventanas sin superposición. Fuente: E15.](Figuras_resultados/clima_desfase_teoria.png)

Los intervalos incluyen cero. El resultado no respalda una regla universal de adelanto o retraso por clima, pero tampoco descarta un aporte no lineal o específico por variedad. El remuestreo es exploratorio y no elimina confusión por temporada y manejo. La prueba siguiente evalúa si usar esas señales reduce error fuera del entrenamiento, con información estrictamente anterior a cada origen.

### 3.8. El calendario diario plantea una pregunta adicional

(La distribución del pronóstico entre días está en revisión y corresponde a siguientes pasos; las señales de corte diario usadas como entradas semanales sí forman parte del análisis principal.)

Al desagregar la producción aparecen 227.623 días-serie observados dentro de un calendario de 1.374.399 filas para 663 series. La suma de los cortes diarios coincide exactamente con el panel semanal por cada llave. Las filas restantes mantienen un valor faltante: construir un calendario no prueba que todas las series estuvieran activas durante todo el intervalo. [E6]

![Figura 8. Volumen registrado y frecuencia de reporte por día de semana. Fuente: EDA diario, E6.](Figuras_resultados/perfil_diario.png)

En el agregado de la finca, los sábados reúnen 65,54 millones de tallos reportados y los domingos 3,65 millones. Además, hay reporte dominical en sólo treinta fechas del periodo, frente a varios centenares para los demás días. El patrón muestra que un reparto uniforme de una séptima parte por día desconoce la distribución registrada. No permite concluir que la producción física del domingo sea siempre nula: calendario de corte y calendario de registro pueden diferir y requieren validación operativa.

El total semanal también puede ocultar cambios recientes. Dos series con un total parecido en la semana anterior pueden llegar al lunes con trayectorias distintas en los últimos tres o cinco días. De ahí surge la extensión con medias, sumas, tendencia y antigüedad del último corte. Las ventanas siguen días de calendario y se acompañan de conteos observados; no toman simplemente las últimas filas disponibles ignorando huecos.

### 3.9. Del hallazgo a la decisión metodológica

| Hallazgo del EDA | Decisión que orienta | Qué debe comprobar el modelo |
| --- | --- | --- |
| Los planos son fotografías y cambian entre versiones | Conservar origen, objetivo y versión | Si la historia de revisiones aporta fuera del ajuste inicial |
| La curva empírica no representa todas las edades de algunas cohortes | Delimitar cuándo aplica la referencia de curva y conservar la ruta basada en producción reciente | Precisión del sistema completo y del respaldo |
| La teoría presenta diferencias sistemáticas con lo registrado | Aprender una corrección | Mejora frente a referencias sobre casos comunes |
| El volumen se concentra y las series tienen escalas diferentes | Desglosar métricas por segmento | Que el agregado no oculte deterioros relevantes |
| La memoria reciente se asocia más con el error cercano | Añadir rezagos y tendencias de corte | Aporte por horizonte, sin asumir causalidad |
| El registro diario no sigue una distribución uniforme | Comparar perfiles y modelos diarios | Error diario y coherencia con la semana por separado |

## 4. Diseño del sistema de pronóstico

### 4.1. Integración, calendario y disponibilidad

La unidad semanal es finca, producto, color, variedad y semana. La base de pronóstico agrega origen y horizonte: una semana objetivo puede aparecer varias veces porque fue anticipada en fechas distintas. Por eso sus cantidades no se suman como inventario producido. Las proyecciones ya calculadas se incorporan como insumo; los modelos de ajuste no vuelven a consultar plantas ni curvas para reconstruirlas. [E3]

H1 corresponde a la semana siguiente a la semana en curso cuando se emite el archivo; por ejemplo, el archivo 18–22 se envía el jueves de la semana 17 y H1 es la semana 18 y H5 a la que comienza cuatro semanas después. Sólo se usan semanas cerradas al entrenar. Las variables diarias se desplazan un día y las predicciones de los siete días de H1 se congelan al lunes, sin actualizarse con lo ocurrido dentro de esa semana. Se supone que los reportes pasados ya están disponibles; su latencia real debe confirmarse. AL1 aporta una referencia de disponibilidad supuesta para los planos, no una prueba de publicación.

Las homologaciones conservan la identidad comercial y no fuerzan coincidencias ambiguas. Los movimientos legítimos de producción se mantienen, los objetivos ausentes no se imputan y los parámetros de imputación de predictores se estiman con entrenamiento. Una prueba que modifica producción futura verifica que las variables anteriores al origen permanezcan iguales. Estos controles hacen revisable el significado de cada caso.

### 4.1.1. Cómo leer la base analítica consolidada

La base común tiene 621.195 filas y 47 columnas; incluye también casos sin objetivo observado o sin historia suficiente. No equivale al conjunto de entrenamiento ni al benchmark estricto vigente, actualizado a 16.325 comparaciones. Cada fila representa una combinación comercial y una semana objetivo vista desde un origen. El diccionario completo, con las 47 columnas agrupadas, está en el cuaderno `lectura.ipynb`; aquí resumimos sólo lo necesario para interpretar el ejemplo.

| Campo | Cómo leerlo en una fila |
| --- | --- |
| `finca`, `producto`, `color`, `variedad` | Identifican a quién corresponde el pronóstico; aquí, DINO amarillo de GAITANA. |
| `origen` | Fecha de corte desde la que se pronostica y hasta la cual llega la información disponible. |
| `semana_objetivo`, `horizonte` | Semana que se quiere estimar y qué tan adelante queda. En la comparación con archivos del ingeniero, la primera semana del nombre del archivo determina H1: el archivo 18–22 tiene H1 en semana 18; el renglón de semana 17 que se repite allí es de la semana en curso. |
| `teoria_modelo` | Referencia teórica utilizable si la curva representa las edades de todas las cohortes del plano. Vacío significa que esta ruta no aplica; no significa cero producción. |
| `media_4`, `observaciones_previas` | Resumen de producción real anterior al origen: media de cuatro semanas e historial reportado disponible. |
| `y` | Producción real de la semana objetivo. Se conoce al cerrar esa semana y se usa para evaluar; no está disponible al emitir el pronóstico. |

En el ejemplo, origen 3 de agosto de 2026 y H5 corresponden a la semana objetivo del 31 de agosto al 6 de septiembre. La última semana histórica empieza el 27 de julio y reporta 19.202 tallos; `media_4` es 22.250,75 y hay 213 semanas reportadas. El plano calcula 27.916,61 tallos para las edades representadas, pero dos de las 25 cohortes no tienen tasa en esa curva: por eso `teoria_modelo` queda vacío y el modelo usa su respaldo de producción reciente. La suma parcial no se toma como total teórico del plano ni señala pérdida de camas o producción. Al cerrar la semana, `y` registra 18.970 tallos reales. La fila es admisible para pronosticar, pero eso no implica que pertenezca a test.

La teoría previa tampoco es el horizonte anterior: es lo que un plano anterior calculaba para esa misma semana objetivo. En este ejemplo, el plano seleccionado del 13 de julio llega al objetivo en su horizonte teórico 7; los dos anteriores, en 8 y 9. Cada plano genera diez semanas teóricas, mientras el modelo evalúa H1–H5 desde su propio origen. Las versiones anteriores existían, pero sus curvas no representaban todas las cohortes; por eso sus teorías no se habilitaron como referencia. Un campo vacío no representa cero tallos.

### 4.2. Metodología del pronóstico semanal

El flujo siguiente ordena las decisiones en el orden en que se hicieron. Cada bloque identifica el modelo o referencia, qué información se agregó y qué decisión metodológica habilitó el paso siguiente. La variante que queda como selección general y las pruebas posteriores por horizonte se mantienen diferenciadas.

![Diagrama A. Secuencia de construcción del modelo semanal: modelos probados, información añadida y decisiones entre etapas. Fuente: cuadernos 10–25.](Figuras_resultados/metodologia_modelo_semanal.png)

Cuando la curva representa todas las cohortes, el sistema aprende la diferencia entre producción real y esa referencia teórica. Cuando no, utiliza una corrección de la media de producción reciente de cuatro semanas. Así, la base conserva la observación real y el modelo tiene una ruta para producir un pronóstico admisible sin inventar un valor teórico para edades no representadas. Los modelos de boosting comparten información entre series e incorporan identificación comercial, horizonte, memoria semanal y los bloques de clima y teoría definidos en los notebooks. [E5]

La extensión incorpora 28 variables diarias: medias, sumas y conteos de corte en ventanas de 3, 5, 7 y 14 días; dispersión, rezagos, media exponencial, tendencias y días desde el último corte; y medias pasadas de temperatura, humedad y radiación. También se evalúa una corrección relativa. Una variante de pérdida absoluta se ensayó después de inspeccionar resultados y se identifica como exploratoria; además cambia la forma de combinar las rutas, por lo que su resultado no aísla únicamente el efecto de la función de pérdida.

Los candidatos semanales usan parámetros fijos de boosting: tasa de aprendizaje 0,08, 80 iteraciones, hasta 15 hojas, mínimo 40 observaciones por hoja, regularización L2 de 1 y semilla 42. El detalle reproducible permanece en los notebooks. El reentrenamiento mensual permite comparar los candidatos sobre los mismos orígenes de 2026, sin ajustar cada combinación hasta obtener un resultado favorable.

El algoritmo principal es HistGradientBoostingRegressor, implementado en scikit-learn. Cada árbol aprende condiciones sobre las entradas; los árboles se incorporan por etapas para reducir el error que queda. Puede representar relaciones no lineales e interacciones, por ejemplo respuestas distintas a una tendencia en horizontes cercanos y lejanos. La variante por histogramas agrupa valores numéricos para buscar divisiones eficientemente. Se compara con referencias simples y Ridge; no se justifica su elección únicamente por complejidad.

El objetivo aprendido es una corrección en tallos: real menos teoría, o real menos Media4 en el respaldo. La predicción final suma referencia y corrección estimada, con mínimo cero. Como ejemplo ilustrativo, una teoría de 28.000 y una corrección estimada de −3.500 producen un pronóstico de 24.500 tallos. El modelo aprende la corrección con resultados históricos, pero no conoce la producción objetivo futura al emitirla. Ridge estima esa corrección con una combinación lineal regularizada; boosting suma aportes de árboles. Ambos se evalúan fuera del entrenamiento.

### 4.2.1. Modelos semanales probados y por qué se compararon

La teoría de la curva es una referencia productiva, no el pronóstico final por sí sola. Se estima como punto de partida cuando representa las edades de todas las cohortes del plano. El modelo aprende la diferencia entre producción real y teoría; cuando la curva no representa todas las edades, aprende una corrección sobre Media4. Así se conservan dos rutas interpretables y cada caso usa la referencia que sí aplica.

HistGradientBoosting se probó porque sus árboles pueden aprender relaciones no lineales entre memoria, producto y horizonte. Ridge sirve de contraste lineal regularizado. Las referencias simples y las ablaciones muestran si el aprendizaje y cada bloque de variables aportan algo frente a reglas más sencillas. La secuencia completa es:

| Cuaderno / modelo | Qué hace | Entradas principales | Decisión o conclusión |
| --- | --- | --- | --- |
| 12 · `Ultimo_valor`, `Media4`, `Teoria_sin_ajuste` | Repite el último dato, promedia cuatro semanas o usa la curva sin corregir. | Una referencia cada vez. | Puntos de comparación sencillos para todos los H1–H5. |
| 12 · `Ajuste_media4_sin_planos` | Boosting estima real−Media4 y suma la corrección a Media4. | Identidad comercial, calendario, memoria real y clima disponible; no recibe teoría. | Respaldo para casos sin curva aplicable. |
| 12–13 · `Modelo_teorico` / `Sistema_teoria_con_respaldo` | Boosting estima real−teoría; si la curva no aplica, el sistema usa el ajuste de Media4. | Identidad, horizonte/calendario, rezagos y tendencias reales, clima y variables de curva en la ruta teórica. | Arquitectura de dos rutas; no promedia ambas referencias. |
| 12 · `Ridge_ajuste_teoria`, `Teorico_sin_memoria`, `Teorico_sin_clima` | Ridge prueba una corrección lineal; las otras dos variantes quitan memoria o clima. | Mismo problema con una diferencia controlada por variante. | Contrastes para medir no linealidad y aporte de cada bloque. |
| 12 · `Modelo_teorico_historia` | Añade revisiones de teorías anteriores para la misma semana objetivo. | Teoría actual, variables semanales y versiones previas. | Prueba si los cambios entre planos agregan señal. |
| 14 · Boosting semanal con señales de corte diario | Mantiene el objetivo semanal y añade 28 resúmenes de corte/clima recientes. | Ventanas 3/5/7/14 días, rezagos, conteos, dispersión, EMA y tendencias. | Prueba si una trayectoria diaria creciente o decreciente anticipa el total semanal. No es el modelo diario. |
| 15 · Boosting con memoria larga y grupos | Añade memoria de hasta 12 semanas, dispersión/conteos y prueba H1–H2 separado de H3–H5. | Producción histórica y, en una variante, teorías previas. | Motiva el uso de dos grupos de horizontes; pesos fijados con validación de 2025. |
| 19 · **Boosting sin clima, selección anual** | Dos grupos de HistGradientBoosting corrigen teoría o Media4: H1–H2 y H3–H5. | Memoria semanal/diaria y de 12 semanas, identidad/calendario y teoría cuando aplica; sin clima. | Ganador anual entre variantes propias, elegido antes de evaluar 2026. Detalle de variables y parámetros en 4.2.5. |
| 22–24 · Modelos separados por horizonte | Entrena un modelo por cada H1, H2, H3, H4 y H5; ajusta `max_iter` con validación temporal. | Variables semanales, memoria y teoría; clima sólo si hay cobertura suficiente. | Experimento distinto del ganador anual. La validación eligió 80 iteraciones en H1, H2 y H5, y 40 en H3 y H4. |
| 25 · Ensayo de modelos propios por producto | Conserva el grupo H1–H2 para H1 y el modelo H2 separado. En H3–H5, para Minicarnation y Carnation prueba un modelo propio de cada producto y horizonte junto con el modelo general de ese horizonte. Otros productos conservan el general. | Producción previa, calendario, teoría y proyecciones anteriores si aplican; el clima no estaba disponible en esta corrida. | Experimento reciente de 1.226 casos; no reemplaza la selección anual. La mezcla y sus parámetros se explican en 5.1.1. |

En el cuaderno 25, “especializado” es sólo una forma abreviada de decir “entrenado para un producto y horizonte específicos”. El ejemplo H3 de Minicarnation usa únicamente su historial de H3; no es otro tipo de algoritmo, sino HistGradientBoosting entrenado con un subconjunto más acotado. Después se combina —con un peso definido en validación anterior— con la predicción del modelo general de H3. El ingeniero y las semanas recientes no determinan ese peso.


### 4.2.2. Variables diarias que alimentan el pronóstico semanal

El experimento 13 enfrenta el sistema inicial al ingeniero; el 14 conserva boosting y añade 28 entradas, sin convertir todavía la tarea en pronóstico diario. Para un mismo total semanal, una trayectoria de corte creciente puede contener información distinta de una decreciente. Se prueba esa hipótesis, no se impone una corrección automática por tendencia.

| Nuevas entradas en 14 | Construcción y significado |
| --- | --- |
| corte_media, corte_suma y corte_dias, cada una en 3/5/7/14 días (12) | Nivel, volumen observado y cantidad de días con dato. Los faltantes no se sustituyen por cero. |
| corte_std_7d; corte_lag1d; corte_lag7d (3) | Dispersión de siete días, valor del día anterior y de siete días atrás. |
| corte_ema_5d (1) | Promedio exponencial con mayor peso reciente; conserva influencia de días anteriores, no trunca exactamente a cinco días. |
| corte_tendencia_3d/5d (2) | Media de los últimos 3/5 días menos media del bloque inmediatamente anterior de igual longitud. |
| dias_desde_corte (1) | Días desde el último valor reportado, incluso cero; no necesariamente desde el último corte positivo. |
| Temperatura/humedad/radiación media en 3/5/7 días (9) | Nueve resúmenes meteorológicos previos al origen. |

Las medias y sumas productivas admiten ventanas parciales y se acompañan de conteos. Todas excluyen el día del origen. La variante aditiva conserva las dos rutas; la alternativa relativa usa el mismo boosting para aprender log(1+real) menos log(1+Media4), invierte la transformación y limita a cero. Otra variante exploratoria cambia pérdida a error absoluto y usa una ruta conjunta sobre Media4, con teoría como predictor: no aísla exclusivamente el efecto de la pérdida.

### 4.2.3. Experimentos acotados después de corregir calidad

El experimento 15 documenta la corrección de calidad y los cambios de arquitectura. Su referencia anterior a calidad conserva el clima de aquella ejecución: tras actualizar la fuente, ese contraste ya no aísla sólo calidad. Dentro de los candidatos recalculados mantiene el clima común; luego separa modelos para H1–H2 y H3–H5, añade memoria de doce semanas, dispersión y conteos, y finalmente añade historia de proyecciones a las rutas teórica y de respaldo. Las medias de cuatro/ocho semanas y la referencia de un año ya existían y no se presentan como variables nuevas. Cada etapa conserva la anterior y añade un bloque. [E10]

La combinación sencilla usa pesos de 0, 0,25, 0,50, 0,75 o 1 sobre el modelo y una referencia de media4 o teoría con respaldo. Los pesos por grupo de horizontes se eligen mediante predicciones de noviembre–diciembre de 2025, con entrenamiento anterior a cada origen y objetivos cerrados antes de enero de 2026. Se mantienen fijos al evaluar 2026. El periodo 2026 continúa siendo desarrollo retrospectivo y no selecciona esos pesos.

### 4.2.4. Prueba acotada del clima y de la procedencia de curvas

El experimento 19 mantiene HistGradientBoostingRegressor, parámetros, memoria larga, separación H1–H2/H3–H5 y rutas teórica/respaldo. Compara retirar todo el clima, usar el clima básico actualizado, añadir señales de catorce/veintiocho días y lluvia, y cambiar la referencia a la curva atribuida a GAITANA manteniendo el mismo clima ampliado. La última comparación afecta tanto referencia como cobertura; se desglosa por rutas y se compara la teoría cruda sobre casos completos para ambas alternativas. [E16]

La selección utiliza el menor WAPE de noviembre–diciembre de 2025, con objetivos cerrados antes de enero de 2026. Se conserva al evaluar 2026. Los modelos se reentrenan mensualmente usando sólo semanas objetivo terminadas antes del corte; imputación y codificación se ajustan en train. Los predictores climáticos terminan antes del lunes de emisión. No se usa clima futuro observado ni pronóstico meteorológico externo. Las pruebas de perturbación del futuro comprueban que no cambien las variables pasadas.

Actualizar clima básico permite medir el efecto de completar la fuente manteniendo la arquitectura anterior. Añadir el bloque ampliado mide una pregunta distinta. La historia previa al arreglo de calidad de 15 se conserva como referencia, pero su contraste con modelos de clima nuevo ya no aísla sólo calidad de curvas. Ningún periodo examinado durante el desarrollo se presenta como prueba prospectiva intacta.

La validación anterior a 2026 produce esta comparación; no es el test frente al ingeniero:

| Método | Casos | MAE (tallos) | WAPE | Sesgo (%) |
| --- | --- | --- | --- | --- |
| Boosting sin clima | 3.548 | 2.045,72 | 21,70 % | 1,28 % |
| Boosting con clima básico | 3.548 | 2.065,49 | 21,91 % | 2,14 % |
| Boosting con clima ampliado y lluvia | 3.548 | 2.086,87 | 22,14 % | 3,16 % |
| Boosting con clima ampliado y curva atribuida a GAITANA | 3.548 | 2.194,51 | 23,28 % | 4,62 % |

Una diferencia pequeña entre candidatos en estos dos meses no acredita superioridad estable. Se conserva la elección para evitar escoger de nuevo mirando el resultado de 2026.

### 4.2.5. Modelo semanal seleccionado: arquitectura, variables y parámetros

El ganador anual es el **Boosting sin clima del cuaderno 19**. No se entrenó un parámetro distinto para cada H. Se ajusta un modelo para H1–H2 y otro para H3–H5; dentro de cada grupo se crean dos regresiones complementarias: una corrige la teoría en los casos donde la curva cubre todas las edades y otra corrige Media4 como respaldo. Cada fila toma sólo la ruta que le corresponde; no se promedian teoría y Media4.

La ruta de Media4 recibe producto, color, variedad, horizonte y calendario, nueve variables de memoria semanal, 28 resúmenes diarios de producción/clima ya observados y siete señales de memoria larga. La ruta teórica recibe ese mismo bloque más `teoria_modelo`, `antiguedad_curva` y `desviacion_reciente_teoria`. Como se eligió la variante sin clima, no entran columnas meteorológicas al modelo final. La imputación numérica usa medianas calculadas en train y las categorías se codifican con indicadores; la cobertura decide la ruta, pero no se entrega al algoritmo como predictor.

Los dos grupos y las dos rutas comparten la misma configuración de HistGradientBoostingRegressor:

| Parámetro | Valor | Interpretación sencilla |
| --- | ---: | --- |
| Tasa de aprendizaje (`learning_rate`) | 0,08 | Cuánto aporta cada árbol nuevo. |
| Iteraciones máximas (`max_iter`) | 80 | Número de etapas de árboles. |
| Hojas máximas por árbol (`max_leaf_nodes`) | 15 | Complejidad permitida a cada árbol. |
| Mínimo por hoja (`min_samples_leaf`) | 40 | Evita reglas basadas en muy pocos casos. |
| Regularización L2 | 1,0 | Penaliza ajustes excesivamente grandes. |
| Parada temprana | No | Usa las 80 iteraciones definidas. |
| Semilla (`random_state`) | 42 | Hace reproducible la ejecución. |

Por tanto, aunque el sistema tenga varios ajustes por grupo y por ruta, **no tiene hiperparámetros distintos entre H1–H2 y H3–H5**. Los parámetros diferentes aparecen en el experimento posterior de modelos separados por horizonte (cuadernos 22–24), no en el ganador anual. Allí se eligieron 80 iteraciones para H1, H2 y H5 y 40 para H3 y H4; se mantuvieron 15 hojas y el resto de la configuración. Esa variante no sustituyó al ganador anual.

### 4.2.6. Secuencia temporal de entrenamiento, validación y evaluación

En 12 se fijan cortes el 7 de julio de 2025, 5 de enero y 4 de mayo de 2026, con ocho semanas de orígenes de evaluación por corte. Cada entrenamiento exige semana_objetivo + siete días menor o igual al corte: no basta con que el origen sea antiguo si su resultado aún no había cerrado. No hay división aleatoria. En 13–19 se reentrena al primer origen de cada mes, conservando los mismos parámetros y el pasado disponible.

Para pesos del 15 y selección del 19 se usan predicciones temporales de noviembre–diciembre de 2025, con objetivos terminados antes de enero de 2026. Luego se evalúa 2026 sin cambiar la elección por el ingeniero. Durante esa evaluación mensual pueden entrar al entrenamiento resultados de meses anteriores de 2026 que ya cerraron: es actualización temporal, no uso de los objetivos del mes que se está evaluando. Los errores train y test se comparan por el mismo ajuste; no se interpreta el train del último mes como si fuera el entrenamiento fijo de todo el año. Como esos periodos se revisaron durante desarrollo, aún se requiere una evaluación prospectiva nueva.

### 4.3. Comparación con el ingeniero

La evaluación principal exige misma finca, producto, color, variedad, origen, objetivo y horizonte, además de un archivo del ingeniero no posterior al origen bajo la regla nominal adoptada. Los emparejamientos recuperados por color, los archivos posteriores y los casos sin pareja se separan. El pronóstico del ingeniero se utiliza para evaluar; no alimenta los modelos candidatos. [E5]

Se informa MAE en tallos, RMSE, WAPE y sesgo, con cortes por horizonte y segmento. El WAPE es la suma de errores absolutos dividida por la suma de producción real: un 20 % no significa 80 % de casos acertados. En las tablas vigentes de 19 y diario 05, sesgo = predicción menos real: positivo indica sobreestimar y negativo subestimar. Su versión porcentual divide la suma de errores firmados por la suma real y multiplica por cien. Los diagnósticos históricos de teoría y algunos notebooks anteriores usan real menos predicción; sus signos no se comparan sin invertirlos. El remuestreo por semana objetivo aporta intervalos exploratorios, sin convertir retrospectivamente estos periodos en una prueba independiente intacta.

### 4.4. Metodología independiente del pronóstico diario

(En revisión: este bloque es un piloto independiente del modelo semanal.)

El objetivo diario es estimar los tallos reportados en cada día de H1. No se vuelve a pronosticar la semana completa en esta sección. Hay dos tareas: el modelo autónomo predice cada día sin recibir el total semanal actual; el reconciliado parte del total semanal ya pronosticado y aprende cómo distribuirlo en siete días. Sus WAPE responden preguntas distintas. El piloto SARIMA/SARIMAX es un contraste exploratorio de series temporales.

![Diagrama B. Secuencia de trabajo del pronóstico diario, con modelos y decisiones; desarrollo todavía en revisión. Fuente: cuadernos diarios 01–05.](Figuras_resultados/metodologia_modelo_diario.png)

El modelo diario autónomo aprende el corte de cada día con historia de producción, clima pasado y calendario, sin recibir el pronóstico semanal actual. Las variantes reconciliadas calculan pesos no negativos para los siete días, los normalizan para que sumen uno y los multiplican por el pronóstico semanal. Se comparan reparto uniforme, perfil de volumen registrado en las ocho semanas previas y perfil de boosting ponderado por frecuencia histórica de reporte. Este último representa el volumen registrado esperado, no una afirmación de producción física cero en días ausentes. [E7]

La evaluación separa error diario, distribución relativa y conservación del total semanal. Se puntúan días con reporte y se informa la cantidad asignada a días sin registro como diagnóstico. El total semanal real se utiliza sólo al analizar posteriormente la forma de la distribución, nunca como entrada de un pronóstico supuestamente perfecto.

Como contraste de series de tiempo se prueban SARIMA (1,0,1)×(0,1,1,7) y SARIMAX con el mismo orden y clima rezagado siete días, sobre log(1+tallos), con 365 días de historia. Ese rezago permite conocer al lunes las variables climáticas de los siete días futuros sin usar clima futuro realizado. El piloto considera las tres series con mayor volumen de 2025 y al menos 120 días reportados, y el primer origen de cada mes de enero a agosto de 2026. Se audita convergencia y se comparan todos los métodos en los mismos días disponibles. [E8]

## 5. Resultados: qué mejoró y dónde persisten las dificultades

### Recorrido de resultados antes de la selección vigente

Los resultados de experimentos iniciales que se muestran a continuación conservan el panel común utilizado en esas corridas (15.838 casos). Sirven para documentar cómo se compararon arquitecturas y qué decisiones motivaron; no son el benchmark anual vigente. La comparación actualizada con el ingeniero, que aplica la regla nominal del archivo semanal, utiliza 16.325 casos y aparece en 5.1.

Los resultados de 12 preguntan si puede corregirse una referencia con información pasada. En los mismos casos donde la curva representa las edades de todas las cohortes se comparan reglas sencillas, boosting y Ridge. Los nombres describen qué referencia y qué bloque recibe cada ajuste. [E5]

| Modelo y referencia | Casos | WAPE |
| --- | --- | --- |
| Boosting que corrige Media4, sin teoría | 2.107 | 20,69 % |
| Media4: promedio real de cuatro semanas | 2.107 | 23,52 % |
| Boosting que corrige la teoría con memoria y clima | 2.107 | 19,31 % |
| Boosting teórico con proyecciones anteriores | 2.107 | 19,21 % |
| Ridge: corrección lineal regularizada de teoría | 2.107 | 19,97 % |
| Teoría cruda, sin corrección | 2.107 | 28,72 % |
| Mismo boosting, sin clima | 2.107 | 18,96 % |
| Mismo boosting, sin memoria real | 2.107 | 23,26 % |
| Último valor real: referencia de persistencia | 2.107 | 21,22 % |

El sistema completo conserva una ruta de pronóstico para todos los casos admisibles. Cuando la curva no representa todas las edades, se usa la ruta basada en producción reciente. En 12 se evalúa el sistema completo por separado:

| Sistema y referencia | Casos | WAPE |
| --- | --- | --- |
| Boosting sobre Media4 | 14.108 | 21,14 % |
| Curva para todas las cohortes + respaldo de producción reciente | 14.108 | 20,95 % |

El experimento 14 añadió señales de corte diario y clima diario a un boosting semanal. Como entran conjuntamente, la comparación no aísla el efecto de cada señal:

| Experimento 14 | Casos | WAPE |
| --- | --- | --- |
| Corrección relativa de Media4 en escala logarítmica | 15.838 | 20,58 % |
| Boosting con pérdida absoluta y rutas exploratorias | 15.838 | 19,86 % |
| Sistema antes de añadir señales diarias | 15.838 | 20,24 % |
| Boosting semanal con 28 señales recientes de corte y clima | 15.838 | 19,92 % |
| Ingeniero | 15.838 | 19,74 % |

En 15 se agruparon horizontes, se añadió historia productiva larga y se probaron versiones anteriores de la teoría. Los pesos se fijaron con validación temporal previa a 2026:

| Experimento 15 | Casos | WAPE |
| --- | --- | --- |
| Referencia anterior (usa otra configuración y clima) | 15.838 | 20,04 % |
| Mezcla fijada con validación anterior a 2026 | 15.838 | 19,49 % |
| Boosting separado con memoria productiva de hasta 12 semanas | 15.838 | 19,46 % |
| Boosting con proyecciones previas | 15.838 | 19,49 % |
| Boosting agrupado H1–H2 y H3–H5 | 15.838 | 19,54 % |
| Boosting con señales diarias de 14 | 15.838 | 19,92 % |
| Ingeniero | 15.838 | 19,74 % |

«Sin memoria» significa que el modelo no recibe rezagos productivos, aunque sí aprende de casos históricos. Las proyecciones previas son versiones anteriores del plano para la misma semana objetivo. La referencia “Antes” conserva otra configuración y clima, por lo que no aísla el efecto de esta revisión. La selección final por validación temporal se informa aparte en 5.1.

### 5.1. Resultado del modelo semanal seleccionado frente al ingeniero

Esta es la comparación principal del **Boosting sin clima seleccionado en el cuaderno 19**: dos ajustes con la misma configuración, uno para H1–H2 y otro para H3–H5. La elección se fijó por validación temporal de noviembre–diciembre de 2025, antes de observar esta evaluación de 2026. Se comparan 16.325 pronósticos emparejados con la regla nominal de archivos: la primera semana del nombre determina H1. Por ejemplo, el archivo 18–22 se envía en la semana 17 y su H1 es la 18; la fila repetida de la semana 17 corresponde a la semana aún en curso.

La gráfica separa magnitud del error (WAPE) y dirección del error (sesgo). Los valores negativos de sesgo indican subestimación. Cada punto/segmento se calcula sobre el volumen agregado de su horizonte; no representa un error promedio por planta.

![Figura 1. WAPE y sesgo por horizonte del Boosting sin clima seleccionado y del estimado del ingeniero. El panel izquierdo muestra magnitud del error; el derecho, dirección y tamaño del sesgo. Fuente: evaluación anual estricta actualizada, cuadernos 13 y 19.](Figuras_resultados/comparacion_modelo_semanal_ganador.png)

| Horizonte | Ajuste del sistema seleccionado | Casos | WAPE: modelo / ingeniero | Sesgo: modelo / ingeniero | Menor WAPE |
| --- | --- | ---: | ---: | ---: | --- |
| H1 | Grupo H1–H2 | 3.512 | 15,53 % / 16,93 % | -1,34 % / -7,54 % | Modelo |
| H2 | Grupo H1–H2 | 3.388 | 17,49 % / 19,16 % | -2,01 % / -7,97 % | Modelo |
| H3 | Grupo H3–H5 | 3.264 | 20,33 % / 20,26 % | -2,46 % / -9,38 % | Ingeniero |
| H4 | Grupo H3–H5 | 3.141 | 21,78 % / 20,97 % | -3,18 % / -11,52 % | Ingeniero |
| H5 | Grupo H3–H5 | 3.020 | 22,20 % / 21,60 % | -2,97 % / -13,09 % | Ingeniero |
| Total H1–H5 | Ambos grupos | 16.325 | 19,36 % / 19,71 % | -2,36 % / -9,81 % | Modelo |

El modelo gana en H1, H2 y el total; el ingeniero gana en H3–H5 por WAPE. El sesgo del modelo es menos negativo en todos los horizontes: subestima menos el volumen agregado, aunque eso no basta para ganar WAPE en H3–H5. Sesgo = 100 × suma(predicción − real) / suma(real). Los resultados son retrospectivos, no una prueba prospectiva independiente.

### 5.1.1. Ensayo reciente: modelos propios por producto y horizonte

Este experimento no es el ganador anual. Compara 1.226 pronósticos de GAITANA en tres semanas objetivo recientes. El ingeniero se usa sólo para medir. En esta sección, “modelo propio por producto y horizonte” significa un modelo entrenado con el historial de un solo producto y un solo horizonte. Por ejemplo, el modelo propio de Minicarnation para H3 aprende de Minicarnation en H3; el modelo general de H3 aprende de los productos disponibles en ese horizonte. Ambos siguen siendo HistGradientBoosting. Se probaron modelos propios para Minicarnation y Carnation; los demás productos usan el modelo general.

| Horizonte/producto | Qué predice el candidato | Cómo se obtiene el valor final |
| --- | --- | --- |
| H1, todos los productos | Modelo general agrupado H1–H2 | Se conserva directamente. |
| H2, todos los productos | Modelo general separado H2 | Se conserva directamente. |
| H3–H5, productos distintos de Minicarnation y Carnation | Modelo general separado para cada horizonte | Se conserva directamente. |
| H3–H5, Minicarnation y Carnation | Un HistGradientBoosting por producto y horizonte, entrenado sólo con ese producto, más el modelo general separado del horizonte | `predicción final = (1 − peso) × general + peso × especializado`. El peso se eligió con validación previa de noviembre. |

Para Minicarnation y Carnation se eligieron pesos de 1,00 en H3, 1,00 en H4 y 0,75 en H5. Así, en H3 y H4 se usa por completo la predicción del modelo propio; en H5 se combinan 75 % de la predicción propia y 25 % de la general. Los pesos son iguales para ambos productos. No se utiliza la predicción del ingeniero para entrenar ni para determinar los pesos.

Los modelos especializados usan HistGradientBoostingRegressor. En la validación previa se eligieron 40 iteraciones para Minicarnation en H3–H5 y 80 iteraciones para Carnation en H3–H5; todos usan 15 hojas. Se mantienen tasa de aprendizaje 0,08, mínimo de 40 casos por hoja, regularización L2 de 1, sin parada temprana y semilla 42. El modelo general por horizonte usa 80 iteraciones en H1/H2/H5 y 40 en H3/H4, con 15 hojas y los mismos valores restantes. La selección de parámetros y pesos ocurrió en noviembre, separada de las tres semanas recientes de evaluación. En esa corrida el clima no estaba disponible en las entradas, así que estos modelos funcionaron sin clima.

| Horizonte | Candidato reciente | WAPE candidato / ingeniero | Sesgo candidato / ingeniero | Lectura |
| --- | --- | ---: | ---: | --- |
| H1 | General agrupado H1–H2 | 12,28 % / 15,23 % | +2,75 % / -7,79 % | Candidato gana WAPE; sobreestima ligeramente. |
| H2 | General separado H2 | 14,96 % / 14,98 % | -0,02 % / -5,80 % | Empate práctico en WAPE; sesgo del candidato casi neutro. |
| H3 | General + mezcla especializada para dos productos | 17,27 % / 16,51 % | -5,85 % / -7,99 % | Ingeniero gana WAPE. |
| H4 | General + mezcla especializada para dos productos | 18,89 % / 16,79 % | -3,96 % / -7,67 % | Ingeniero gana WAPE. |
| H5 | General + mezcla 75/25 para dos productos | 19,76 % / 16,95 % | -7,76 % / -7,86 % | Ingeniero gana WAPE. |
| Total | Ensamble por horizonte/producto | 17,53 % / 16,34 % | -4,22 % / -7,51 % | Ingeniero gana el total. |

El ensamble reduce el WAPE del candidato previo de 17,80 % a 17,53 %, pero todavía no supera al ingeniero en el total ni en H3–H5. La mejora reciente de H1 es clara; H2 es un empate práctico. Esta evaluación breve no desplaza al Boosting sin clima anual.

### 5.2. Precisión diaria y coherencia semanal con el clima actualizado

(En revisión: desarrollo preliminar y siguientes pasos.)

El componente diario conserva sus modelos y usa los nuevos totales semanales. El autónomo pronostica cada día con producción reciente, calendario y clima pasado; el reconciliado distribuye el total semanal mediante pesos de boosting. El perfil histórico y el reparto uniforme son referencias. Se emiten siete días desde el lunes sin usar reportes de esa semana. [E17]

| Método | Casos | MAE (tallos) | WAPE | Sesgo (%) |
| --- | --- | --- | --- | --- |
| Autónomo: referencia histórica anterior al clima | 22.973 | 543,76 | 26,76 % | -7,23 % |
| Boosting diario reconciliado con selección semanal | 22.973 | 553,80 | 27,26 % | -6,03 % |
| Boosting diario autónomo | 22.973 | 542,84 | 26,72 % | -7,11 % |
| Boosting reconciliado con memoria semanal | 22.973 | 556,82 | 27,41 % | -6,27 % |
| Perfil histórico con selección semanal | 22.973 | 562,31 | 27,68 % | -5,60 % |
| Perfil histórico con memoria semanal | 22.973 | 565,17 | 27,82 % | -5,85 % |
| Reconciliado: referencia histórica anterior al clima | 22.973 | 557,78 | 27,45 % | -6,21 % |
| Uniforme con selección semanal | 22.973 | 585,22 | 28,80 % | -16,92 % |
| Uniforme con memoria semanal | 22.973 | 589,21 | 29,00 % | -17,09 % |

Antes de esta revisión, el reconciliado con la selección semanal tenía WAPE 27,27 %; tras reconstruir curvas y modelos, 27,26 %. El autónomo obtiene 26,72 %. La comparación se realiza sobre días reportados; un día sin registro no se convierte en cero. Todos los repartos coherentes conservan su total semanal.

![Figura 12. Precisión diaria sobre mismos días reportados. Fuente: E17.](Figuras_resultados/diario_clima_actualizado.png)

La sensibilidad a semanas con siete reportes se conserva en Semanas_completas del Excel de diario 05. Su composición difiere del panel general y no puede usarse su completitud futura para elegir método al emitir. No existe aquí un benchmark diario del ingeniero ni un umbral operativo validado.

### 5.3. Piloto SARIMA/SARIMAX

(En revisión: desarrollo preliminar y siguientes pasos.)

Se mantienen las tres series elegidas por volumen de 2025, los órdenes SARIMA (1,0,1)×(0,1,1,7), clima rezagado siete días en SARIMAX y auditoría de convergencia. El clima se actualiza, no se cambian los órdenes buscando mejorar 2026. El nuevo total sólo modifica la reconciliación. La tabla utiliza días comunes a todos los métodos; no se compara directamente con el WAPE diario de toda la finca. [E8, E17]

| Método | Casos | MAE (tallos) | WAPE | Sesgo (%) |
| --- | --- | --- | --- | --- |
| Boosting diario reconciliado con selección semanal | 135 | 2.457,22 | 27,18 % | -11,75 % |
| Boosting diario autónomo | 135 | 2.791,97 | 30,88 % | -12,53 % |
| Perfil histórico con selección semanal | 135 | 2.445,79 | 27,05 % | -11,96 % |
| SARIMA | 135 | 2.252,11 | 24,91 % | -2,61 % |
| SARIMAX | 135 | 2.217,70 | 24,53 % | -2,98 % |
| SARIMAX reconciliado con selección semanal | 135 | 2.704,76 | 29,92 % | -21,96 % |
| SARIMA reconciliado con selección semanal | 135 | 2.689,74 | 29,75 % | -21,85 % |
| Semana_anterior | 135 | 2.839,95 | 31,41 % | -2,87 % |
| Uniforme con selección semanal | 135 | 2.680,33 | 29,65 % | -22,32 % |

### 5.4. Interpretación de variables del modelo seleccionado

El notebook 16 vuelve a calcular el ajuste del 3 de agosto y permuta bloques de entradas para observar cuánto cambia el WAPE. Esto no es SHAP, no es un porcentaje de producción y no mide un efecto causal. El cambio por permutación puede ser grande con pocos casos o variables relacionadas; se presenta con el tamaño del grupo. [E12]

Como la selección semanal fijada es Sin_clima, esa alternativa no recibe variables meteorológicas. La importancia climática no es cero: se evalúa por los contrastes de modelos de 19.

| Grupo de horizonte / ruta | Bloque con mayor cambio | Casos evaluados | Cambio WAPE (pp) |
| --- | --- | --- | --- |
| H1_H2 / Respaldo | Producción semanal reciente | 857 | 82,43 |
| H1_H2 / Teoria_completa | Teoría y desvío | 79 | 69,76 |
| H3_H5 / Respaldo | Producción semanal reciente | 577 | 80,50 |
| H3_H5 / Teoria_completa | Teoría y desvío | 47 | 40,60 |

![Figura 13. Importancia por bloques de la alternativa semanal seleccionada. Fuente: E12.](Figuras_resultados/importancia_bloques_semanal.png)

![Figura 14. Variables con mayor cambio al permutarlas dentro de cada grupo. Fuente: E12.](Figuras_resultados/importancia_variables_semanal.png)

Las entradas con información redundante pueden sustituirse entre sí y la permutación puede crear combinaciones poco habituales. El grupo donde la curva representa todas las cohortes es menor que el universo completo; sus resultados se leen con cautela y no se usan para cambiar la selección retrospectivamente.

### 5.5. Entrenamiento y evaluación del mismo ajuste

El inventario 17 conserva los distintos cortes. Aquí se compara train con test del corte del 3 de agosto de 2026 para las mismas configuraciones; también se informa cuántos casos contiene cada partición. El ingeniero es una referencia evaluada, no un modelo entrenado en el proyecto. [E13, E16, E17]

| Modelo semanal | WAPE train | WAPE test mismo corte | Casos train | Casos test |
| --- | --- | --- | --- | --- |
| Boosting sin clima | 22,41 % | 15,44 % | 140.994 | 1.758 |
| Boosting con clima básico | 21,96 % | 15,25 % | 140.994 | 1.758 |
| Boosting con clima ampliado y lluvia | 21,85 % | 15,34 % | 140.994 | 1.758 |
| Boosting con clima ampliado y curva atribuida a GAITANA | 22,30 % | 15,47 % | 140.994 | 1.758 |

| Modelo diario | WAPE train | WAPE test mismo corte | Casos train | Casos test |
| --- | --- | --- | --- | --- |
| Boosting diario autónomo | 25,90 % | 26,65 % | 70.448 | 3.192 |
| Reparto uniforme con selección semanal | 28,68 % | 30,99 % | 70.448 | 3.192 |
| Perfil histórico con selección semanal | 27,39 % | 27,33 % | 70.448 | 3.192 |
| Boosting reconciliado con selección semanal | 26,56 % | 27,24 % | 70.448 | 3.192 |

El ingeniero no tiene un train de nuestro algoritmo. SARIMA/SARIMAX dentro de muestra excluyen la inicialización del filtro y no equivalen a pronósticos emitidos día a día. Una diferencia entre train histórico y un mes de test también refleja composición y dificultad del periodo; no prueba por sí sola fuga ni ausencia de sobreajuste.

### 5.6. De dónde proviene el WAPE: productos, colores y variedades

El notebook 20 descompone los mismos casos estrictos usados en la comparación semanal. Los aportes se expresan en puntos del WAPE total: error absoluto del grupo dividido por el volumen real de todo el panel. Así se distinguen grupos con una tasa alta de error de los grupos que más pesan por volumen. No se cambió el modelo a partir de este diagnóstico. [E18]

## H1: productos

| Producto | Casos | WAPE modelo | WAPE ingeniero | Aporte modelo (pp) | Aporte ingeniero (pp) | Sesgo modelo | Sesgo ingeniero |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION | 979 | 14,33 % | 14,53 % | 8,64 | 8,77 | -1,92 % | -6,86 % |
| CARNATION | 1258 | 18,90 % | 20,17 % | 3,50 | 3,74 | -1,30 % | -7,85 % |
| SOLOMIO | 396 | 15,14 % | 18,77 % | 1,72 | 2,13 | 0,24 % | -9,63 % |
| RAFFINE | 203 | 16,16 % | 25,58 % | 0,98 | 1,54 | -0,70 % | -9,41 % |
| STAR | 35 | 16,74 % | 19,10 % | 0,17 | 0,19 | -0,83 % | -17,00 % |
| BARBATUS | 165 | 25,46 % | 29,20 % | 0,15 | 0,17 | 4,07 % | -0,75 % |
| TRACHELIUM | 33 | 35,19 % | 41,93 % | 0,10 | 0,12 | -2,73 % | -24,17 % |
| VERONICA | 66 | 22,18 % | 26,54 % | 0,09 | 0,11 | 2,87 % | -7,91 % |
| GREEN BALL | 33 | 13,93 % | 16,10 % | 0,08 | 0,10 | 2,82 % | -1,39 % |
| VERONICA SPRAY | 66 | 23,02 % | 23,72 % | 0,09 | 0,09 | 3,82 % | -3,33 % |
| STATICE | 109 | 27,55 % | 29,79 % | 0,08 | 0,08 | 0,82 % | -2,23 % |
| AMAZON | 33 | 28,99 % | 22,66 % | 0,05 | 0,04 | 6,11 % | 0,39 % |
| ACHILLEA | 37 | 380,92 % | 99,26 % | 0,01 | 0,00 | 350,26 % | -89,63 % |

Modelo: los tres mayores aportes (MINICARNATION, CARNATION, SOLOMIO) concentran 88,49 % de su error absoluto.

Ingeniero: los tres mayores aportes (MINICARNATION, CARNATION, SOLOMIO) concentran 85,63 % de su error absoluto.

### Color: mayores aportes del modelo

| Grupo | Casos | WAPE modelo | WAPE ingeniero | Aporte modelo (pp) | Exceso frente al ingeniero (pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION / ORANGE | 76 | 17,69 % | 18,69 % | 1,09 | -0,06 |
| MINICARNATION / HOT PINK | 66 | 14,92 % | 14,87 % | 1,08 | 0,00 |
| MINICARNATION / LIGHT PINK | 99 | 16,26 % | 14,92 % | 1,02 | 0,08 |
| MINICARNATION / RED | 66 | 13,20 % | 13,31 % | 0,79 | -0,01 |
| MINICARNATION / WHITE | 99 | 14,54 % | 16,76 % | 0,76 | -0,12 |

### Variedad: mayores aportes del modelo

| Grupo | Casos | WAPE modelo | WAPE ingeniero | Aporte modelo (pp) | Exceso frente al ingeniero (pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION / ORANGE / UCHUVA | 33 | 18,40 % | 17,50 % | 0,96 | 0,05 |
| MINICARNATION / HOT PINK / LORENZO | 33 | 16,33 % | 16,11 % | 0,67 | 0,01 |
| MINICARNATION / LIGHT PINK / ACADEMY | 33 | 19,15 % | 16,36 % | 0,63 | 0,09 |
| MINICARNATION / YELLOW / CAESAR | 33 | 13,65 % | 14,58 % | 0,51 | -0,03 |
| MINICARNATION / LAVENDER / NENUFAR | 33 | 13,45 % | 15,00 % | 0,50 | -0,06 |
## H1–H5: productos

| Producto | Casos | WAPE modelo | WAPE ingeniero | Aporte modelo (pp) | Aporte ingeniero (pp) | Sesgo modelo | Sesgo ingeniero |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION | 4567 | 17,42 % | 17,75 % | 10,59 | 10,79 | -4,81 % | -9,13 % |
| CARNATION | 5825 | 23,39 % | 22,43 % | 4,28 | 4,11 | -0,80 % | -8,86 % |
| SOLOMIO | 1860 | 18,14 % | 18,54 % | 2,04 | 2,08 | 2,16 % | -12,02 % |
| RAFFINE | 945 | 23,42 % | 29,36 % | 1,41 | 1,77 | 0,20 % | -13,77 % |
| STAR | 158 | 18,23 % | 20,75 % | 0,18 | 0,20 | 1,52 % | -19,51 % |
| BARBATUS | 775 | 33,76 % | 28,54 % | 0,20 | 0,17 | 8,83 % | -2,38 % |
| TRACHELIUM | 148 | 41,96 % | 47,36 % | 0,12 | 0,14 | -4,75 % | -32,12 % |
| VERONICA | 310 | 28,16 % | 34,39 % | 0,11 | 0,14 | 5,67 % | -17,88 % |
| GREEN BALL | 155 | 19,12 % | 18,54 % | 0,11 | 0,11 | 9,95 % | 3,06 % |
| VERONICA SPRAY | 310 | 30,28 % | 26,16 % | 0,11 | 0,10 | 7,99 % | -6,93 % |
| STATICE | 475 | 35,03 % | 36,07 % | 0,09 | 0,09 | 8,11 % | -5,17 % |
| AMAZON | 155 | 32,66 % | 22,16 % | 0,06 | 0,04 | 12,81 % | 0,40 % |
| ACHILLEA | 155 | 821,83 % | 99,81 % | 0,02 | 0,00 | 806,45 % | -97,36 % |

Modelo: los tres mayores aportes (MINICARNATION, CARNATION, SOLOMIO) concentran 87,48 % de su error absoluto.

Ingeniero: los tres mayores aportes (MINICARNATION, CARNATION, SOLOMIO) concentran 86,02 % de su error absoluto.

### Color: mayores aportes del modelo

| Grupo | Casos | WAPE modelo | WAPE ingeniero | Aporte modelo (pp) | Exceso frente al ingeniero (pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION / HOT PINK | 310 | 18,80 % | 16,26 % | 1,37 | 0,19 |
| MINICARNATION / LIGHT PINK | 465 | 21,12 % | 20,14 % | 1,32 | 0,06 |
| MINICARNATION / ORANGE | 350 | 17,62 % | 21,76 % | 1,09 | -0,26 |
| MINICARNATION / RED | 310 | 17,70 % | 14,37 % | 1,05 | 0,20 |
| MINICARNATION / WHITE | 465 | 19,38 % | 21,26 % | 1,02 | -0,10 |

### Variedad: mayores aportes del modelo

| Grupo | Casos | WAPE modelo | WAPE ingeniero | Aporte modelo (pp) | Exceso frente al ingeniero (pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION / ORANGE / UCHUVA | 155 | 17,98 % | 20,43 % | 0,95 | -0,13 |
| MINICARNATION / HOT PINK / LORENZO | 155 | 19,94 % | 16,24 % | 0,83 | 0,15 |
| MINICARNATION / LIGHT PINK / ACADEMY | 155 | 21,54 % | 19,38 % | 0,70 | 0,07 |
| MINICARNATION / YELLOW / CAESAR | 155 | 18,19 % | 19,70 % | 0,69 | -0,06 |
| MINICARNATION / PURPLE / EPSILON | 155 | 20,02 % | 12,02 % | 0,67 | 0,27 |



Los gráficos detallados se mantienen junto al Excel diagnóstico: productos, colores, variedades, meses, rutas y semanas. Son hipótesis para revisar los episodios con operaciones; por sí solos no identifican una causa agronómica ni un error en el registro.

![Figura 15. Aporte de los productos al WAPE. Fuente: E18.](Figuras_resultados/error_aporte_productos.png)

![Figura 16. Diferencia de WAPE por producto y horizonte. Fuente: E18.](Figuras_resultados/error_producto_horizonte.png)

![Figura 17. Trayectorias semanales de variedades foco en H1 con el emparejamiento nominal corregido; los casos del origen 20 de abril se muestran cuando el archivo 17–21 ofrece comparación estricta. Fuente: E18 y cruce actualizado del cuaderno 13.](Figuras_resultados/error_variedades_foco_h1.png)
El espacio que todavía aparezca en una trayectoria corresponde a una serie-variedad sin pareja válida dentro del subconjunto gráfico, no a un hueco general de producción. Para el origen del 20 de abril se usa el archivo 17–21 como H1 nominal; el dato de semana 17 repetido en 18–22 es una estimación de la semana en curso.

## 6. Discusión: calidad, clima y distribución del error

La corrección de nombres recuperó observaciones reales de camas piloto sin crear cortes. En los registros de 2026, casi todas las estadísticas fechadas en ese año tienen una correspondencia única con cama, variedad y ciclo. Las correspondencias ambiguas que persisten corresponden a referencias concretas con más de una cama candidata y valores de plantas distintos; se identifican para revisión puntual. Esa auditoría no debe confundirse con el soporte de edades de la curva.

La base analítica conserva las semanas de producción real y añade la referencia derivada de los planos. La curva empírica representa las edades observadas en los pilotos utilizados. Si una cohorte pide otra edad, el sistema conserva el caso y usa la ruta basada en producción reciente. Es una condición metodológica de aplicación de la curva; no significa que se haya perdido producción ni que las camas no se hayan cruzado.

En el panel estricto actualizado de 16.325 casos, el modelo semanal obtiene 19,36 % WAPE y el ingeniero 19,71 %; H1 es 15,53 % y 16,93 %, respectivamente. El error firmado agregado del modelo es -2,36 % del volumen real. Se informa junto con WAPE porque errores positivos y negativos se compensan en el sesgo. La diferencia observada procede de una evaluación retrospectiva y no asegura el mismo resultado en periodos nuevos.

El EDA climático y los experimentos temporales no establecen por sí solos una relación causal. El clima de estación no representa necesariamente cada invernadero y la curva compartida no certifica igualdad agronómica entre fincas. La atribución a GAITANA sólo se hace cuando hay coincidencia verificable con plano.

La distribución diaria sigue en revisión. El modelo autónomo obtiene 26,72 %; el reparto reconciliado con la selección semanal, 27,26 %. El primero pronostica cada día y el segundo reparte un total semanal: resuelven preguntas distintas. No hay una comparación diaria con el ingeniero.

## 7. Conclusiones y continuidad

La cadena se recalculó desde las correspondencias de camas piloto hasta curvas, proyecciones, base analítica y modelos. La producción observada se conserva en la base. La curva se usa como referencia directa cuando representa todas las edades de las cohortes de un plano; cuando no aplica directamente, el modelo puede usar la historia reciente si el caso tiene información suficiente. Esto describe dos rutas del pronóstico y no una pérdida de producción ni una falla general de los cruces.

En la evaluación anual actualizada de 16.325 casos comunes, el modelo semanal seleccionado tiene 19,36 % WAPE y el ingeniero 19,71 %; en H1, 15,53 % y 16,93 %, respectivamente. En un experimento reciente separado, de 1.226 casos de GAITANA en tres semanas objetivo, la combinación de modelos por horizonte logra una ventaja clara en **H1: 12,28 % frente a 15,23 % del ingeniero**. En **H2: 14,96 % frente a 14,98 %**, la diferencia es de apenas 0,02 puntos y debe describirse como empate práctico. El resultado conjunto reciente sigue favoreciendo al ingeniero (17,53 % del modelo frente a 16,34 %). En H3–H5 también gana el ingeniero. Son evaluaciones retrospectivas y sus ventanas no se deben mezclar: la evidencia respalda especialmente la mejora de H1, mientras H2 requiere más semanas para confirmar una ventaja.

El experimento del cuaderno 25 probó modelos especialistas por producto y horizonte, y una combinación de modelos propios sin usar el pronóstico del ingeniero como entrada. Mejoró el WAPE total del candidato reciente previo de 17,80 % a 17,53 %, pero no desplazó al ingeniero en el total ni en H3–H5. El reparto diario reconciliado obtiene 27,26 % y continúa en revisión. Todos estos resultados son retrospectivos.

La siguiente comprobación útil es fijar esta configuración y registrar emisiones en un periodo nuevo. También se requiere confirmar las unidades de lluvia, disponibilidad real de reportes, identidad de los pilotos sin pareja y significado de días sin corte registrado. No ampliar a ARABELLA: el alcance de modelado y las conclusiones siguen restringidos a GAITANA.

El diagnóstico del origen del WAPE orienta esa continuidad: revisar MINICARNATION por volumen, CARNATION H3–H5 por anticipación y las semanas críticas de UCHUVA, EPSILON y ACADEMY. La prioridad se sostiene en aportes al error, persistencia y comparación emparejada, no sólo en el mayor WAPE local. No se cambiaron los modelos a partir de este EDA; cualquier mejora propuesta deberá evaluarse en datos posteriores.

Los cuadernos 21–25 ya realizaron la evaluación de semanas recientes, modelos separados por horizonte, el experimento n−1 y la especialización por producto para H3–H5. El n−1 no produjo una mejora general; la especialización del cuaderno 25 sí redujo modestamente el WAPE del candidato reciente, aunque el ingeniero mantiene ventaja global. El siguiente paso es conservar la estrategia que protege H1 y medirla en semanas futuras completas; en paralelo, probar mejoras para H3–H5 con cortes temporales nuevos y comparables. No se seleccionará un modelo por una diferencia marginal de una sola ventana.

(Pronóstico diario en revisión: siguientes pasos.) Mantener los resultados como avance, estudiar mejor calendario de reporte y ausencia de corte, y ajustar ventanas y parámetros mediante validación temporal anterior a una nueva evaluación. Comparar predicción autónoma y reparto coherente con el semanal sin confundir sus objetivos. Antes de ampliar modelos, revisar edades de curva sin soporte y semanas críticas de productos; no completar automáticamente con cero ni recalibrar usando el real de test.

### 7.1. Límites

Persisten la disponibilidad histórica supuesta de archivos, procedencia inferida de pilotos, representatividad agronómica y equivalencia entre tallos reportados y exportables. El EDA de desplazamiento analiza una ventana parcial y no mide retraso fisiológico de cohortes individuales. Los periodos fueron examinados durante desarrollo y no son test prospectivo intacto. El clima de estación no garantiza representar cada invernadero. No se han medido beneficios económicos ni adopción empresarial.

La literatura verificada, la validación empresarial y la pertinencia de PCA/MCA/PDN continúan pendientes; no se atribuyen resultados a componentes no ejecutados.

## Referencias de la evidencia y pendientes editoriales

Las referencias E1–E19 permiten ubicar la evidencia interna que sostiene las cifras y decisiones de este borrador. No sustituyen la bibliografía académica. La revisión de literatura del anteproyecto debe integrarse con lectura y citas verificadas de sus fuentes; aquí no se convierten nombres de artículos de la estructura original en afirmaciones bibliográficas no comprobadas.

| Referencia | Evidencia reproducible | Uso en el documento |
| --- | --- | --- |
| E1 | Proyecciones Teoricas Propias/Proyecciones_teoricas.ipynb | EDA de pilotos, camas, ciclos, inventario y curvas |
| E2 | Proyecciones Teoricas Propias/Proyecciones_teoricas_todos_los_anios.ipynb | Historia 2021–2026, cobertura y cinco planos |
| E3 | Analisis/10_base_analitica_proyecciones.ipynb | Conservación e integración semanal |
| E4 | Analisis/11_EDA_proyecciones.ipynb | Composición, cobertura, error y asociaciones |
| E5 | Analisis/12, 13 y 14 | Modelos, benchmark experto y tendencias diarias |
| E6 | Modelo_de_series_diario/01_base_diaria_EDA.ipynb | Calendario diario, conciliación y EDA |
| E7 | Modelo_de_series_diario/02_distribucion_semanal_a_diaria.ipynb | Distribución y evaluación diaria |
| E8 | Modelo_de_series_diario/03_SARIMA_SARIMAX_y_boosting.ipynb | Piloto temporal y convergencia |
| E9 | Proyecciones Teoricas Propias/00_catalogo_variedades y Auditoria_calidad_curvas.ipynb | Catálogo central y recuperación antes/después |
| E10 | Analisis/15_calidad_y_mejora_por_horizonte.ipynb | Diagnóstico del error, experimentos y pesos anteriores a 2026 |
| E11 | Modelo_de_series_diario/04_diario_con_memoria_semanal.ipynb | Efecto del nuevo total semanal, cobertura y sensibilidad diaria |
| E12 | Analisis/16_interpretacion_modelo_semanal.ipynb | Importancia por permutación y reproducción del ajuste |
| E13 | Analisis/17_inventario_modelos_train_test.ipynb | Inventario y errores de entrenamiento/evaluación por corte |
| E14 | Proyecciones Teoricas Propias/01_procedencia_pilotos_y_curvas_gaitana.ipynb | Procedencia inferida y sensibilidad de curvas |
| E15 | Analisis/18_EDA_clima_y_desfase.ipynb | Cobertura, lluvia, error de volumen y desplazamiento |
| E16 | Analisis/19_modelos_clima_y_curvas_gaitana.ipynb | Comparación temporal y elección previa a 2026 |
| E17 | Modelo_de_series_diario/05_diario_clima_actualizado.ipynb | Reparto del candidato y train/test compuesto |
| E18 | Analisis/20_EDA_origen_error_modelo_ingeniero.ipynb | Descomposición del WAPE y sesgo por producto, color, variedad y semanas |
| E19 | Analisis/21–25 | Semanas recientes, horizontes separados, experimento n−1 y especialistas H3–H5 |

Referencia técnica utilizada en la implementación: documentación oficial de SARIMAX de statsmodels, https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html.

### Correspondencia con la estructura anterior

La introducción conserva problema, objetivos y alcance. Los capítulos 2 y 3 desarrollan el entendimiento de fuentes y el EDA que antes figuraban como contenido previsto. El capítulo 4 concentra el método y el 5 sus resultados; el 6 integra la discusión que faltaba entre cifras y conclusiones. El capítulo 7 reúne conclusiones y límites. Se abandona la correspondencia rígida de todos los subtítulos entre metodología y resultados para dar continuidad a la explicación. Esta reorganización es una propuesta editorial para revisar con el asesor, no un cambio de resultados.

La literatura verificada, la revisión agronómica, la decisión sobre PCA/MCA/PDN y la validación empresarial siguen pendientes. Sus títulos no se mantienen como capítulos extensos vacíos. La documentación detallada de llaves, parámetros y tablas por segmento permanece en los notebooks y puede constituir anexos según las exigencias de entrega. Este documento es un borrador desarrollado del trabajo empírico, no una tesis lista para radicar.


## Anexo. Diccionario de la base analítica común

Se agrupan las 47 columnas para facilitar la lectura. Es la base del notebook 10; las variables ampliadas se documentan en la metodología y no se confunden con este archivo. NaN, NaT y valores ausentes no significan cero.

| Columna(s) | Significado |
|---|---|
| finca, producto, color, variedad | Identifican la serie comercial: finca, producto, color y variedad cuya producción semanal se estudia. |
| origen | Lunes desde el que se emite el pronóstico; separa el pasado disponible del futuro por estimar. |
| horizonte | Horizonte del MODELO semanal: H1 es la semana del origen y H5 empieza cuatro semanas después. El modelo evalúa H1–H5, pero las proyecciones TEÓRICAS de cada plano abarcan 10 semanas y se cuentan desde la semana siguiente a fecha_plano. Son numeraciones distintas porque parten de fechas distintas. |
| semana_objetivo | Lunes de la semana que se pronostica; la semana abarca de lunes a domingo. |
| ultima_semana_utilizada | Lunes de la última semana de producción histórica utilizada, anterior al origen. |
| y | Producción real reportada de la semana objetivo, en tallos. Es la respuesta que se intenta predecir, no una variable que se pueda conocer anticipadamente. |
| produccion_lag1, produccion_lag2, produccion_lag3 | Producción real, en tallos, de una, dos y tres semanas calendario antes del origen, respectivamente. |
| media_4, media_8 | Promedio semanal de tallos durante las cuatro u ocho semanas anteriores al origen; requiere las cuatro u ocho observaciones. |
| desv_4 | Desviación estándar de las cuatro semanas previas, en tallos: resume cuánto varió la producción reciente. |
| tendencia_4_8 | media_4 menos media_8, en tallos. Un valor negativo indica un nivel reciente inferior al promedio de ocho semanas. |
| cambio_reciente | produccion_lag1 menos produccion_lag2, en tallos: cambio entre las dos últimas semanas. |
| observaciones_previas | Número de semanas históricas con producción reportada antes del origen; no tienen que ser consecutivas. |
| temperatura_semana_lag1, humedad_semana_lag1, radiacion_semana_lag1 | Promedio climático de la semana anterior al origen, construido con los promedios diarios válidos. Una semana requiere al menos cinco días válidos. Conservan las unidades de la fuente depurada. |
| temperatura_semana_media4, humedad_semana_media4, radiacion_semana_media4 | Promedio de los cuatro valores semanales anteriores de cada variable climática; requiere las cuatro semanas. El clima corresponde a la finca, no a una medición por variedad. |
| fecha_estacional | Fecha de la semana objetivo menos 52 semanas (364 días). |
| produccion_52 | Producción real de la misma serie comercial en fecha_estacional, en tallos; referencia estacional del año anterior. |
| semana_seno, semana_coseno | Dos números que ubican la semana objetivo en un calendario circular: seno indica posición horizontal y coseno posición vertical (imaginando una aguja que parte de arriba y gira como un reloj). Se calculan a partir del número de semana del año; no son tallos ni porcentajes de producción. Para la semana 36 del ejemplo de DINO valen −0,935 y −0,355. Debajo de esta tabla se muestra el cálculo completo, paso a paso. |
| union_finca, union_producto, union_color, union_variedad | Nombres normalizados para unir la producción con las proyecciones. No son identificadores oficiales ni cultivos adicionales. |
| plano | Archivo o versión del plano del que procede la proyección seleccionada para ese origen. |
| fecha_plano | Fecha nominal de esa versión del plano. |
| disponible | Fecha supuesta de disponibilidad usada por el proceso para permitir utilizar ese plano. No certifica su publicación histórica real. |
| teoria | Suma teórica de las cohortes con una edad representada en la curva para la semana objetivo, unida por finca, producto, color, variedad y fecha objetivo. No acumula H1–H5. En DINO, H5 del modelo emitido el 3 de agosto coincide con el horizonte teórico 7 del plano del 13 de julio: `teoria` conserva 27.916,61 tallos como suma parcial. No se interpreta como total de todas las cohortes ni como pronóstico final. |
| cohortes | Número de grupos de plantas con la misma finca, producto, color, variedad, clave de curva y fecha de siembra dentro del plano. Un grupo puede reunir varias camas; no equivale a una cama física ni cuenta tallos. |
| sin_cobertura | Nombre técnico de la cantidad de cohortes cuya edad objetivo no está representada en la curva aplicada. Es una condición de uso de la curva, no el conteo de producción perdida o de camas mal unidas. |
| curva_completa | Indicador técnico: verdadero cuando la curva representa las edades de todas las cohortes y el total puede usarse como referencia directa del modelo. |
| teoria_modelo | Valor de `teoria` habilitado como referencia directa si la curva representa todas las cohortes; queda vacío si solo se dispone de suma parcial. No es la predicción final. En DINO queda vacío para activar la ruta de producción reciente; la producción real sí permanece. |
| teoria_previa_1, teoria_previa_2 | Valores de una y dos versiones anteriores del plano para la misma semana objetivo y serie comercial. El 1 y el 2 cuentan versiones hacia atrás, no H1 y H2. Pueden existir incluso en H5 del modelo porque cada plano produce diez semanas teóricas. En DINO corresponden a los horizontes teóricos 8 y 9. No se habilitan si la curva no representa todas las cohortes de esa versión; también pueden faltar si el plano anterior no alcanza la semana objetivo. |
| revision_teoria | Cambio en tallos entre una referencia de curva utilizable del plano seleccionado y `teoria_previa_1`, siempre para la misma semana objetivo. Positivo: la nueva versión proyecta más; negativo: menos. Si alguna referencia directa no se puede usar, queda vacío. No compara H5 contra H1. |
| antiguedad_curva | Tiempo en semanas entre origen y fecha_plano: indica qué tan antiguo es el plano seleccionado al emitir el pronóstico. No es la edad de las plantas. En DINO: del 13 de julio al 3 de agosto = 3 semanas. |
| desviacion_reciente_teoria | media_4 menos teoria_modelo, en tallos. Compara el promedio real de las cuatro semanas anteriores al origen con la teoría de la semana objetivo. No es un error de pronóstico porque compara períodos distintos. En DINO está vacío porque teoria_modelo está vacío. |
| admisible_modelo | Indica si la fila tiene `media_4` y al menos 26 semanas históricas con producción reportada. No exige que la curva represente todas las cohortes: en ese caso puede usarse la ruta de respaldo. Tampoco exige que `y` ya se conozca ni indica train o test. |
| motivo_cobertura | Nombre técnico del estado de aplicación de la curva: `curva_completa` indica que todas las cohortes tienen edad representada; `cohortes_sin_curva` indica que alguna no la tiene; `sin_snapshot_disponible` significa que no hay plano elegible; `sin_pareja_comercial_u_objetivo` significa que no coincide la serie o semana. En DINO se refiere a edades 9 y 16; no significa que falten registros de producción ni toda la curva de la variedad. |

Semana seno y coseno son dos coordenadas del calendario anual: seno(2π × semana ISO / 52) y coseno(2π × semana ISO / 52). Mantienen cerca las semanas 52 y 1; en la semana 36 valen aproximadamente −0,935 y −0,355. No son porcentajes de producción ni indican una caída. El ciclo fijo de 52 semanas aproxima los años con semana ISO 53.
