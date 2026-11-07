# Análisis de pronósticos semanales y diarios de corte de productos en La Gaitana Farms

Elián Durán · Julián Osorio · Anderson Gonzalez

Asesor: Rafael Amaya Gomez

Universidad de los Andes

Facultad de Ingeniería Industrial

Maestría en Inteligencia Analítica para la Toma de Decisiones

Noviembre de 2026

<!-- PORTADA_FIN -->

## Resumen

La Gaitana Farms es una empresa floricultora cuyos registros incluyen clavel, miniclavel y otros productos de flor de corte. La operación necesita anticipar cuántos tallos estarán disponibles para coordinar ventas, compras y poscosecha. En este estudio, un tallo es la unidad de cantidad reportada y el corte es la actividad de cosecha que origina esos registros. El pronóstico de referencia lo elabora el profesional responsable de estimar la producción, combinando información del cultivo y conocimiento experto. Se propone complementarlo mediante la integración de inventarios de plantas, rendimientos de camas piloto, producción registrada y clima histórico, y la comparación temporal de métodos de pronóstico.

El análisis reconstruye curvas empíricas de rendimiento por variedad y edad y utiliza la producción reciente cuando no es posible calcular una referencia teórica total. El método semanal seleccionado aprende correcciones de esas referencias y diferencia las dos primeras semanas de las tres siguientes. En la evaluación retrospectiva ampliada de 2026, sobre 20.283 casos comparables de GAITANA, obtiene un error porcentual absoluto ponderado de 19,27 %, frente a 19,40 % del profesional de producción. En la primera semana de pronóstico los valores son 15,04 % y 17,02 %, y los sesgos firmados son −0,94 % y −7,97 %, respectivamente. La ventaja no se extiende a todos los horizontes: el referente experto registra menor error en las semanas tercera a quinta y en el agregado de la extensión más reciente. Los ejercicios diarios muestran potencial para distribuir el total semanal, pero conservan carácter exploratorio. El aporte es una propuesta reproducible para apoyar la revisión del estimado; no se acredita todavía beneficio económico ni equivalencia entre tallos reportados y producción exportable. La disponibilidad histórica de las fuentes limita la interpretación prospectiva de los resultados.

**Palabras clave:** flor de corte; curvas empíricas de rendimiento; pronóstico semanal; boosting de gradiente; SARIMA; SARIMAX; reconciliación diaria.

<!-- CONTENIDO -->

## 1. Introducción

### 1.1. Contexto operativo y problema de decisión

La Gaitana Farms produce flores de corte. En la información utilizada aparecen clavel —Carnation—, miniclavel —Minicarnation—, Solomio, Raffine y otros productos. Los registros distinguen finca, producto, color y variedad, una desagregación necesaria para estimar disponibilidad comercial: un excedente de un color o variedad no necesariamente resuelve la falta de otro. El estudio se concentra en GAITANA; la presencia de ARABELLA en las fuentes no implica que sus resultados estén validados con el mismo modelo.

El proceso relevante comienza con plantas instaladas en camas de cultivo, continúa con su desarrollo y los cortes registrados, y termina en decisiones de disponibilidad y coordinación de poscosecha. Los planos de siembra describen las existencias y sus fechas de establecimiento; las estadísticas de camas piloto permiten observar el rendimiento a distintas edades. La producción real registra los tallos cortados reportados en el sistema. Estas fuentes tienen frecuencias, niveles de detalle y funciones diferentes; integrarlas requiere respetar tanto el calendario como la identidad del cultivo.

El pronóstico utilizado como referencia es elaborado por el profesional encargado de la estimación de producción, denominado en adelante **responsable de producción**. Según el flujo documentado del proyecto, revisa las existencias del cultivo, las curvas por variedad, el comportamiento reciente y su conocimiento de la operación. Su estimación contiene un componente empírico y de juicio experto, cuyo criterio no se reduce a una fórmula observable en los archivos. El proyecto busca aportar un contraste cuantitativo y una sugerencia revisable, conservando ese conocimiento como parte del proceso de decisión.

Los estimados se envían el jueves de la semana anterior al inicio del periodo anunciado. Una edición denominada 18–22 tiene su primera semana de pronóstico en la semana 18, aunque incluya todavía una columna de la semana 17 en curso. Esa columna no redefine la primera semana. Una recuperación desde una edición posterior, cuando falta la edición nominal anterior, se identifica como tal y no se confunde con una emisión nominalmente comparable. La distinción importa porque comparar fechas objetivo sin conservar cuándo fueron anticipadas altera la evaluación.

Anticipar el corte es útil para revisar compromisos comerciales, posibles compras complementarias y la planeación de poscosecha. Sin embargo, mejorar una métrica retrospectiva no demuestra que ya se hayan reducido costos o faltantes. La pregunta de negocio es **en qué medida una propuesta analítica puede complementar el estimado semanal del responsable de producción y qué evidencia permite explorar su distribución diaria, sin perder la interpretación agronómica ni utilizar información futura**.

Responderla exige establecer si los rendimientos piloto representan las edades del inventario, si su proyección necesita correcciones y qué aportan la producción reciente y el clima. También requiere comparar referencias sencillas, una corrección lineal y métodos de aprendizaje no lineal. Para el componente diario se examinan perfiles históricos, modelos SARIMA y SARIMAX y una red recurrente exploratoria. Los modelos de series temporales se implementaron en el piloto diario; no se presentan como candidatos semanales que no fueron ejecutados. Su detalle se desarrolla en la metodología.

### 1.2. Objetivos y alcance efectivo

**Objetivo general.** Analizar y comparar métodos de pronóstico semanal y diario del corte reportado por producto, color y variedad en GAITANA, integrando información histórica y operativa para construir una propuesta reproducible de apoyo a la estimación de producción de La Gaitana Farms.

**Objetivo específico 1.** Caracterizar el proceso de estimación y consolidar las fuentes de producción, planos, camas piloto, estadísticas y clima, identificando sus llaves, dimensiones y restricciones temporales.

**Objetivo específico 2.** Construir e interpretar curvas empíricas de rendimiento y proyecciones teóricas por edad, y establecer cuándo pueden utilizarse como referencia del pronóstico semanal y cuándo corresponde utilizar producción reciente.

**Objetivo específico 3.** Comparar los métodos semanales implementados con el pronóstico del responsable de producción mediante evaluación temporal y métricas por horizonte y segmento, examinando el aporte de memoria productiva, clima y especialización de modelos.

**Objetivo específico 4.** Evaluar de manera exploratoria alternativas de pronóstico diario autónomo y de distribución del total semanal, y delimitar las condiciones de uso de una salida analítica revisable por la organización.

La formulación precisa el alcance comprobable del estudio respecto a la aspiración inicial de estimar producción exportable y validar impacto empresarial. No da esas aspiraciones por cumplidas. **Producción exportable** designa la que satisface los criterios comerciales de exportación; **no exportable**, la que no los satisface. Los **tallos reportados** son la cantidad registrada en la fuente de corte, utilizada aquí como variable objetivo. El estimado de referencia se identifica en su formato como exportable, pero no existe una conciliación confirmada que permita tratar ambos conceptos como equivalentes. La comparación mide concordancia contra el corte reportado y conserva esa limitación de unidad comercial.

GAITANA y GAITANA PPTO son etiquetas distintas y no se suman como si describieran el mismo universo observado. Tampoco se reasignan registros de finca desconocida a GAITANA. La evaluación principal utiliza series de GAITANA con historia suficiente. Las demás fincas permanecen en las fuentes conservadas y requieren una evaluación propia antes de extenderles las conclusiones.

Se utilizan cinco horizontes semanales. **H1** es la primera semana objetivo de la edición y **H2, H3, H4 y H5** son las cuatro semanas consecutivas siguientes, de lunes a domingo. En los cálculos, el origen es el lunes de H1. Este índice permite ordenar las filas; no certifica que el modelo y el responsable de producción hayan contado con exactamente la misma información el jueves anterior. El componente diario estudia los siete días de H1 y, en un ensayo diferente, el pronóstico de un día adelante.

La revisión académica conserva la última evaluación ejecutada, con corte del 28 de octubre de 2026 y producción fuente hasta el 27 de octubre. El año 2026 evaluado comprende las semanas ISO 1–43, no un año calendario completo. La semana ISO 1 comienza el 29 de diciembre de 2025. Las fechas de observación y las versiones archivadas pueden verificarse; las fechas históricas completas de publicación y corrección no están acreditadas para todas las fuentes. Por ello, el alcance es retrospectivo y sus supuestos se explicitan antes de interpretar los resultados.

## 2. Radiografía de los datos: fuentes, características y caso actual

### 2.1. Términos operativos y unidades de análisis

{{tabla:glosario}}

El plano representa existencias en una fecha, no altas acumulables. Si una cama con 1.000 plantas aparece en dos planos consecutivos, se observa dos veces el mismo inventario; no se concluye que hubo dos siembras ni se suman 2.000 plantas. Para proyectar un objetivo se utiliza una versión elegible del inventario. Al comparar versiones se alinean las mismas semanas objetivo para estudiar revisiones, sin acumular sus totales como producción nueva.

La unidad observada de producción semanal es finca–producto–color–variedad–semana. La unidad de pronóstico añade origen y horizonte. Una semana real puede, por tanto, formar parte de varios casos porque se anticipó desde fechas diferentes. Los denominadores de evaluación cuentan **casos de pronóstico**, no plantas, camas ni volumen físico único acumulado.

### 2.2. Fuentes y dimensiones verificadas

{{tabla:fuentes}}

Las cantidades de @tab_fuentes corresponden a las tablas depuradas y versionadas de la extracción utilizada, no a la suma de filas de todos los libros originales. La producción se conserva al nivel de movimiento, sin eliminar cortes legítimos por tener cantidades repetidas. Los originales se archivan por separado y las tablas limpias mantienen procedencia. Las estadísticas consolidadas entre ediciones y la vista de estadísticas de la edición 2026 son universos diferentes: esta última incluye historia que vuelve a aparecer en libros posteriores, por lo que no deben sumarse sus filas entre años.

Una edición identificada como 2026 puede contener cortes anteriores a 2026. El año de edición informa qué versión del libro se utilizó; la fecha de corte identifica cuándo se observó el rendimiento. La historia piloto disponible empieza en 2012, pero la curva aplicada a un plano sólo utiliza la ventana histórica especificada en el método. Tener historia antigua en el libro no habilita a usarla indiscriminadamente.

Las llaves se construyen después de homologar nombres comerciales, espacios y mayúsculas, conservando los códigos y nombres originales. Para las estadísticas piloto se utiliza la edición o libro, referencia de cama, variedad homologada y ciclo de siembra; cuando existe se prioriza la fecha de siembra, y en su defecto año y semana compatibles. Los planos identifican ubicación mediante finca, invernadero y cama, y separan las cohortes por fecha de siembra e identidad comercial. La producción se agrega por serie y fecha; el clima se integra por finca y fecha, no como si existiera una estación por variedad. Las proyecciones se vinculan por serie, versión elegible y semana objetivo. Los estimados de referencia añaden origen nominal y horizonte para asegurar una comparación equivalente.

Los nombres ambiguos no se resuelven por similitud aproximada. Una variedad ausente en estadísticas se recupera sólo cuando la referencia completa dentro del mismo libro identifica una única combinación compatible. Las coincidencias equivalentes se consolidan sin duplicar cortes. La integridad de las uniones se comprueba antes de construir rendimientos; no puede deducirse de que una suma final resulte numéricamente plausible.

### 2.3. Curvas empíricas y significado de la referencia teórica

Las estadísticas piloto vinculan tallos cortados con las plantas de una cama y su edad. Cada observación utilizable permite calcular tallos por planta; al reunir observaciones de la misma variedad y edad se construye una curva empírica de rendimiento. Esta curva describe los pilotos disponibles, no una ley biológica demostrada para todas las camas. Para trasladarla a un plano se requiere conocer las plantas y edades de sus cohortes y aceptar un supuesto de representatividad que aún debe contrastarse agronómicamente.

{{figura:curva}}

La @fig_curva muestra Solomio–Ard blanco en la referencia del plano del 12 de octubre de 2026. A edad 50 semanas, el rendimiento de la curva es 0,2542 tallos por planta, con 43 observaciones piloto–semana. Es un punto real de la curva construida; no es el rendimiento de todas las camas ni el valor de una planta individual. En edades poco observadas, especialmente los puntos aislados tardíos, la incertidumbre de representatividad es mayor. Los huecos no se conectan como si se hubiera observado toda la trayectoria.

La proyección teórica multiplica las plantas de cada cohorte por el rendimiento de su variedad a la edad que tendrá en la semana objetivo y suma los aportes. Si una edad requerida no está representada, ese aporte es desconocido y la suma de los demás es parcial. Esto no implica ausencia de producción real ni una falla del cruce piloto–estadística. La metodología conserva el caso y permite otra referencia cuando existe historia productiva suficiente.

Un corte cero registrado, válido y asociado a plantas positivas aporta un rendimiento cero al cálculo, igual que cualquier otra observación. Una edad sin observaciones no aporta evidencia de cero; un valor desconocido por falta de identificación o fecha tampoco. La decisión de conservar los ceros y no completar los otros estados evita confundir ausencia de cosecha registrada con ausencia de información. Sólo una regla agronómica confirmada permitiría asignar cero a edades no observadas.

## 3. Metodología

### 3.1. Fases del estudio y lógica del pronóstico

El procedimiento comprende cinco fases conectadas: integrar y depurar las fuentes; construir curvas y proyecciones; generar variables y comparar métodos semanales; evaluar temporalmente contra el responsable de producción; y explorar el componente diario y su utilización analítica. La @fig_semanal resume la lógica central antes de describir el algoritmo: cada caso utiliza una referencia aplicable, aprende su corrección con el pasado y se evalúa contra el corte observado. La existencia de una ruta alternativa es una decisión metodológica, no una imputación de producción real.

{{figura:semanal}}

El aprendizaje semanal corrige la referencia teórica cuando todas las cohortes tienen rendimiento por edad. En los demás casos admisibles corrige la media de las cuatro semanas previas —Media4—. No promedia ambas rutas ni convierte la suma teórica parcial en un total. La arquitectura seleccionada separa H1–H2 de H3–H5 porque la información cercana y la lejana plantean dificultades distintas; dentro de cada grupo mantiene una regresión para cada ruta.

### 3.2. Integración y pretratamiento

El pretratamiento normaliza identidades, verifica llaves y fechas, distingue ciclos y consolida historia repetida entre ediciones. Las condiciones de entrada a rendimientos exigen correspondencia única, plantas positivas, corte no negativo y fecha y edad válidas, además de los controles de repetición aplicables. La @fig_pretratamiento presenta los conteos verificados. Sus bloques distinguen filas piloto de casos de pronóstico; la flecha hacia la base no representa una igualdad de esos denominadores.

{{figura:pretratamiento}}

{{tabla:estados}}

En @tab_estados, «Única» significa que se identificó una pareja compatible; no certifica que la fila supere todos los filtros posteriores. «Ambigua» conserva varias parejas posibles; «Conflicto_ciclo» indica incompatibilidad de siembra entre candidatos; «Llave_incompleta» carece de componentes necesarios para decidir; y «Sin_pareja» no encuentra candidato compatible. Estos últimos estados quedan trazables y no aportan rendimientos hasta resolverlos. No se elige arbitrariamente una cama para aumentar la cantidad utilizable.

La base analítica conserva todos los casos construidos, aunque algunos no tengan todavía producción objetivo observada o historia suficiente. El aprendizaje requiere Media4 disponible y al menos 26 semanas históricas reportadas. Los objetivos ausentes no se imputan. Para predictores numéricos se estiman medianas dentro de cada entrenamiento; las categorías se codifican también dentro de ese conjunto. Las pruebas de perturbación de datos futuros comprueban que no cambien las variables pasadas. Es un control de transformación, no una acreditación de publicación histórica.

Los planos elegibles se seleccionan según la regla de disponibilidad nominal archivada. Las proyecciones se generan previamente y se incorporan como insumo; los modelos semanales no reconstruyen curvas durante la inferencia. Las fechas, cantidades y procedencia de los movimientos se conservan. El detalle de lectura de una fila y el diccionario de las 47 columnas se incluyen en el anexo A.

### 3.3. Construcción de curvas, referencias y variables

Para cada fecha de plano se utilizan las 78 semanas anteriores de cortes piloto utilizables. En cada variedad–edad se calcula el promedio de los cocientes tallos/plantas, limitando extremos con el criterio de 1,5 rangos intercuartílicos cuando hay al menos cuatro observaciones. Con menor soporte no se aplica ese ajuste. Se conserva el dato original; no se extrapolan edades ni se normaliza la curva para que sume uno. El promedio da igual peso a cada observación y difiere de dividir el total de tallos por la suma de plantas expuestas, que pondera por tamaño.

La edad se calcula entre los lunes de la semana de siembra y de la semana objetivo. El plano fija el inventario disponible; no reemplaza la fecha de siembra al calcular edad. Una cohorte de 10 semanas tendrá 15 cinco semanas después, independientemente del número de versiones del plano en que aparezca. Las proyecciones de cada plano abarcan diez semanas desde la siguiente a su fecha; esa numeración no es la de H1–H5 del modelo, que se cuenta desde su propio origen.

Se construyen curvas compartidas porque la fuente piloto no identifica de manera completa su finca. Como sensibilidad se atribuyen a GAITANA sólo los pilotos que coinciden inequívocamente en ubicación, identidad y siembra con sus planos. No se asignan los casos desconocidos a ARABELLA por descarte. Cambiar a esa curva altera tanto las observaciones incluidas como las edades representadas; por tanto, su comparación no aísla una supuesta superioridad universal de curvas propias frente a compartidas.

{{tabla:variables}}

Las variables de @tab_variables se calculan antes del lunes de origen y se mantienen constantes durante el pronóstico semanal. Las medias y sumas diarias admiten ventanas parciales acompañadas de conteos; los días sin reporte no se convierten en corte cero. Las referencias de 364 días y el calendario circular aproximan la estacionalidad anual. Las versiones previas de teoría representan el mismo objetivo desde planos anteriores, no los horizontes H1 y H2 del registro actual.

El clima se examina como posible señal del error o desplazamiento del corte, no como causa identificada. La auditoría diaria adapta la frecuencia esperada a las lecturas observadas, exige al menos 80 % de lecturas y 22 horas de amplitud; algunos resúmenes semanales requieren cinco días válidos. Las ventanas ampliadas conservan sus propios umbrales. En febrero–mayo de 2026 se aprovechan las mediciones horarias completas; una ventana no calculable de lluvia no significa ausencia de toda la fuente climática ni se sustituye por lluvia cero. Las variantes climáticas utilizan exclusivamente pasado, no clima futuro realizado.

La ventana de 78 semanas, el peso igual de observaciones y el tratamiento de extremos son reglas implementadas, no óptimos agronómicos demostrados. La representatividad de los pilotos frente al manejo, época y ambiente de cada cama permanece como supuesto. Las variables aportan hipótesis cuya utilidad se contrasta predictivamente; su asociación exploratoria no basta para seleccionarlas.

### 3.4. Métodos semanales y decisiones de selección

Se comienza con último valor, Media4 y teoría sin corrección para establecer referencias verificables. Ridge contrasta una corrección lineal regularizada; boosting permite aproximar relaciones no lineales entre producción previa, identidad comercial y horizonte. Boosting agrega árboles sucesivamente para reducir la pérdida residual [1]. La implementación por histogramas empleada es HistGradientBoostingRegressor [2]; su papel es aprender una corrección en tallos, no volver a estimar las plantas del plano.

Si B es la referencia aplicable y f(X) la corrección aprendida, el pronóstico es máximo(0, B + f(X)). En la ruta teórica se aprende real − teoría; en la otra, real − Media4. Por ejemplo ilustrativo, una referencia de 28.000 tallos y una corrección de −3.500 producen 24.500 tallos. La corrección se aprende con objetivos históricos conocidos, sin entregar al algoritmo el objetivo que debe pronosticar ni el estimado del responsable de producción.

{{tabla:modelos}}

Las ablaciones retiran memoria o clima manteniendo el problema y los casos comunes. Después se incorporan resúmenes diarios y memoria de hasta doce semanas; otras variantes añaden revisiones de teoría. Se comparan grupos de horizontes y combinaciones con pesos de 0, 0,25, 0,50, 0,75 o 1, elegidos en validación anterior a 2026. La variante de pérdida absoluta y corrección relativa se conserva como exploración: modifica más de un elemento y no permite atribuir toda diferencia a una única función de pérdida.

La comparación climática mantiene arquitectura y contrasta sin clima, clima básico, clima ampliado y la curva atribuida a GAITANA con clima ampliado. El criterio de selección es menor WAPE en noviembre–diciembre de 2025, con objetivos terminados antes de enero de 2026. La configuración elegida fue **boosting sin clima, agrupado H1–H2/H3–H5 y con dos rutas de referencia**. Las revisiones de teoría fueron evaluadas, pero no son entradas de esta configuración final. Tampoco son predictores los estimados del responsable de producción.

Los ensayos posteriores entrenan por horizonte, separan clavel o miniclavel del resto —esquema n−1— o combinan modelos generales y propios de producto–horizonte. Un modelo propio es el mismo algoritmo ajustado a un subconjunto, no una nueva familia. Estos ensayos reentrenan por origen, usan memoria semanal y hasta seis variables de teoría y revisiones, y limitan el ajuste a una muestra de hasta 5.000 registros pasados por grupo, con semilla 42. No reproducen exactamente los bloques diario y de memoria larga de la configuración principal; por ello, sus diferencias no se atribuyen sólo a separar horizontes o productos. Los parámetros se seleccionan en noviembre de 2025 y algunos factores de volumen se calibran en diciembre; el ajuste reciente no vuelve a elegirlos mirando el resultado del responsable de producción. Estos experimentos no sustituyen automáticamente la selección general ni se mezclan sus paneles al informar una mejora.

{{tabla:parametros}}

La @tab_parametros concentra los parámetros reproducibles. En el modelo semanal seleccionado, los dos grupos de horizontes y sus rutas usan la misma configuración: cambia el conjunto aprendido, no los hiperparámetros. Se exige soporte suficiente para ajustar la ruta teórica; si no alcanza el mínimo implementado de 40 casos de entrenamiento se conserva la alternativa de producción reciente. La selección fue acotada, sin optimización exhaustiva ni garantía de estabilidad ante otras ventanas.

### 3.5. Entrenamiento, validación y comparación temporal

Se utiliza evaluación por orígenes sucesivos, coherente con el carácter temporal del problema [3]. Cada ajuste admite únicamente objetivos cuya semana terminó antes o al corte de entrenamiento: semana objetivo + siete días ≤ corte. La imputación y codificación se estiman sólo en ese entrenamiento, siguiendo la separación entre ajuste y evaluación [4]. Un origen antiguo no basta si su objetivo todavía no había terminado.

{{tabla:particiones}}

La validación de selección corresponde a noviembre–diciembre de 2025. La prueba ampliada conserva la configuración elegida y utiliza objetivos del año ISO 2026 cerrados antes del corte de evaluación. Se reentrena al primer origen de cada mes con las semanas ya cerradas. Una semana evaluada puede incorporarse al entrenamiento de un ajuste posterior; no fue conocida por el ajuste que la pronosticó. No hay reparto aleatorio 80/20 ni porcentaje global obtenido al sumar entrenamientos repetidos.

En el último ajuste, del 5 de octubre, el entrenamiento reúne 146.191 casos con objetivos del 5 de julio de 2021 al 28 de septiembre de 2026. La evaluación de ese ajuste contiene 685 casos de orígenes del 5 al 19 de octubre. El 99,53 %/0,47 % describe sólo esa partición por cantidad de casos; no indica que la prueba acumulada de 2026 sea únicamente ese 0,47 %. La evaluación ampliada contiene 43 semanas objetivo y 23.765 casos del modelo; 20.283 tienen pareja nominal del responsable de producción. En H1, la comparación nominal dispone de 41 semanas, aunque el conjunto entre horizontes alcance 43.

Se conserva además un ajuste congelado al 3 de agosto de 2026 para contrastar la actualización mensual en las semanas posteriores a la semana 36. Ambos métodos se comparan sobre los mismos casos con referente nominal. La extensión se define por **semana objetivo desde la 37**, no por fecha de origen; así no se omiten predicciones lejanas que anticiparon esos objetivos desde agosto. Los resultados semanales originales y los nuevos constituyen paneles distintos y no se agregan sus cifras como si provinieran de una sola extracción.

El error firmado se calcula siempre como pronóstico − real; el sesgo porcentual divide su suma por el real total. El WAPE divide la suma de errores absolutos individuales por ese mismo volumen, sin cancelar errores al agregar productos. MAE y RMSE se estiman en tallos; MAPE y proporción dentro de ±8 % utilizan reales positivos. No se reconstruyen estas dos últimas métricas desde promedios agregados. La banda de ±8 % es la referencia inicial del proyecto, no un nivel de servicio aprobado por la empresa. Se evalúan los casos con real conocido; un objetivo ausente no se trata como cero.

Los periodos de 2026 fueron revisados durante el desarrollo, aunque en esta ampliación no se retocaron parámetros. La evaluación es retrospectiva y no equivale a una prueba prospectiva intacta. Además, las variables del modelo se cortan antes del lunes objetivo, mientras el referente se envía el jueves anterior. Falta reconstruir para ambos exactamente los insumos disponibles al jueves. La ordenación temporal evita usar objetivos futuros en entrenamiento, pero no resuelve por sí sola las correcciones retrospectivas ni esa asimetría informativa. Los resultados deben interpretarse bajo esta restricción.

### 3.6. Componente diario

(El pronóstico diario continúa en revisión; sus resultados son exploratorios y orientan pasos siguientes.)

El componente diario distingue tres tareas en @tab_diario_metodo. El modelo autónomo estima cantidades sin recibir el total semanal pronosticado. El reconciliado calcula siete pesos no negativos que suman uno y los multiplica por dicho total. La LSTM es un ensayo de un día adelante, actualizado con el pasado disponible de cada día, no siete predicciones congeladas al lunes. Sus métricas no responden a la misma pregunta.

{{tabla:diario_metodo}}

El boosting autónomo aprende en escala logarítmica la corrección respecto a Media4/7, con identidad, calendario y señales previas; se invierte la transformación y se limita a cero. Los perfiles reconciliados distribuyen el total mediante reparto uniforme, volumen histórico de ocho semanas o volumen aprendido ponderado por frecuencia de reporte suavizada, (reportes + 0,5)/(días + 1). Los pesos se normalizan entre siete días; ante suma no positiva se utiliza el perfil histórico. La ausencia de reporte no se interpreta como cero físico del cultivo.

SARIMA y SARIMAX se aplican sobre log(1 + tallos), con 365 días de historia y orden fijo (1,0,1)×(0,1,1,7). En la parte no estacional, p = 1 incorpora un término autorregresivo, d = 0 no diferencia ordinariamente y q = 1 incorpora un término de media móvil de los errores. En la parte estacional, P = 0 no añade autorregresión estacional, D = 1 diferencia a siete días y Q = 1 añade un término de media móvil estacional; la periodicidad s = 7 representa el ciclo semanal del registro diario [3]. SARIMAX agrega clima rezagado siete días, conocido al emitir, sin pronóstico meteorológico externo. Se retienen ajustes convergentes y días comparables en tres series de alto volumen elegidas con 2025; el panel común queda en 135 días.

La red LSTM, de la familia de redes recurrentes con memoria [5], recibe secuencias de 28 días, máscaras de observación, calendario e historia desplazada 364 días. Se entrenó con objetivos de enero de 2025 a junio de 2026; julio–agosto se destinan a validación y septiembre a prueba. Su escala mediana positiva se calcula con historia anterior a julio, incluida historia de 2024, y las entradas se estandarizan con train. La selección de series por cantidad de reportes debe auditarse usando sólo el pasado del corte. No se reconcilió la red con el total semanal y sus resultados no certifican el reparto operativo de H1.

### 3.7. Salida analítica y actualización operativa

Se implementó un prototipo que conserva originales fuera de SQL, datos limpios versionados, carga trazable y una propuesta que puede revisarse por producto, color y variedad. Generar, ajustar y publicar son acciones distintas; una simulación no reemplaza automáticamente la versión vigente. El checklist registra revisión y reabre las combinaciones afectadas por cambios. Las pruebas de conservación y de coincidencia con el cálculo analítico comprueban integración del software, no impacto empresarial.

El reentrenamiento mensual se distingue de la actualización de indicadores: corregir una fuente o incorporar real permite recalcular desempeño, sin autorizar una nueva arquitectura. La operación propuesta conserva corte, versión de datos, modelo y métricas por emisión; la promoción de una variante exige evaluación y aprobación. La separación entre datos, entrenamiento y servicio facilita su control [6]. No se implementa aprendizaje automático después de cada tallo ni se presenta el prototipo como un sistema corporativo ya adoptado.

## 4. Resultados y discusión

### 4.1. Integración y alcance empírico de las referencias

El pretratamiento de la edición 2026 contiene 543.368 filas de estadísticas, de las cuales 523.336 tienen pareja única y 490.116 superan los filtros de utilización. Los 93.488 cortes cero conservados forman parte de esas observaciones. Entre los cortes efectivamente fechados en 2026, 46.085 de 46.157 filas tienen pareja única —99,84 %— y 72 permanecen ambiguas. El porcentaje describe correspondencia entre registros de ese subconjunto, no rendimiento predictivo ni representatividad de las edades.

El panel semanal de GAITANA contiene 45.108 combinaciones observadas de serie y semana y conserva 338.568.100 tallos reportados de su universo. La base ampliada tiene 648.030 filas y 47 columnas; 216.127 casos tienen objetivo observado y 148.435, además, cumplen los requisitos de historia. Las últimas cifras no se suman: son conjuntos anidados, no diferentes cantidades de flores. La fuente incluye movimientos de la semana en curso, que no se evalúan como una semana ya terminada.

{{figura:soporte}}

En @fig_soporte, 46.528 de los 216.127 casos observados permiten calcular la referencia teórica total —{{dato:pct_soporte}} %—. El resto conserva su producción real; la condición se refiere a las edades de las cohortes y a la alineación del plano con la serie y objetivo. El denominador no son plantas ni tallos. La escala comienza en 15 %, por lo que la comparación de alturas debe leerse con el eje indicado. El 99,84 % de correspondencias piloto y esta proporción son medidas diferentes.

La utilidad de la separación es evitar dos errores: descartar producción real porque una curva no permite sumar todo el inventario, o presentar una suma parcial como total. En un caso ilustrativo con dos cohortes, la curva puede contener la edad de una y no de otra aunque ambas camas estén correctamente identificadas. El modelo mantiene el caso si cuenta con historia admisible y utiliza Media4. Falta validar agronómicamente cuándo una edad no observada podría considerarse improductiva; no se impuso ese supuesto para aumentar el uso de teoría.

### 4.2. Hallazgos exploratorios que orientaron el método

La composición por producto concentra {{dato:pct_mini}} % del volumen semanal en miniclavel y {{dato:pct_clavel}} % en clavel. Esto justifica revisar el aporte de cada segmento al error, pues una mejora global puede depender de pocas familias comerciales. No se interpreta un año parcial como crecimiento frente a un año completo, ni se atribuyen cambios a festividades o manejo sin un contraste específico.

Antes del corte de desarrollo de julio de 2025, la mediana entre series de la asociación de Spearman entre producción semanal previa y error real − teoría fue {{dato:rho_h1}} en H1 y {{dato:rho_h5}} en H5. Se exigieron al menos veinte pares por serie y horizonte. La diferencia motivó probar rezagos y tendencias, pero no estima su beneficio predictivo ni justifica individualmente todas las variables. La evidencia sobre memoria se contrasta después retirando ese bloque del modelo.

El análisis climático no encontró una regla universal de desplazamiento. En ventanas de cinco semanas sin superposición, las asociaciones exploratorias entre clima previo y centro relativo del corte presentaron intervalos que incluyen cero. El calendario, el manejo y la composición pueden intervenir. Por ello se contrastaron bloques climáticos mediante pronóstico, sin afirmar que el clima carezca de efectos fisiológicos. El anexo B conserva el gráfico de asociaciones de las variables efectivamente evaluadas y delimita su muestra, en lugar de extender el cuerpo con matrices redundantes.

### 4.3. Comparación y selección de métodos semanales

{{tabla:iniciales}}

La @tab_iniciales mantiene 2.107 casos comunes para aislar los contrastes iniciales. La corrección teórica con memoria mejora respecto a Media4, la teoría cruda y la variante sin memoria; Ridge aporta un contraste lineal y la versión con revisiones muestra una diferencia acotada. No se traslada el error de esta muestra al panel ampliado: cambian fechas, disponibilidad de teoría y composición. El resultado respalda aprender correcciones y probar memoria, no una superioridad en todas las variedades.

{{tabla:seleccion}}

La @tab_seleccion contiene la validación de 2025 usada para escoger entre variantes climáticas. Sin clima obtuvo el menor WAPE y se conservó al evaluar 2026. La diferencia frente al clima básico es pequeña y la curva atribuida a GAITANA cambia a la vez la referencia y su soporte. No se concluye que el clima sea irrelevante ni que compartir curvas sea siempre mejor; bajo este diseño no se justificó añadir esos bloques al candidato principal.

{{tabla:horizontes}}

{{figura:comparacion}}

La @tab_horizontes y @fig_comparacion muestran el resultado principal con los mismos casos por método. En H1 el modelo reduce WAPE de 17,02 % a 15,04 %, una diferencia de 1,97 puntos porcentuales, y acerca el sesgo a cero. En H2 conserva ventaja. En H3–H5 el responsable de producción tiene menor WAPE, aunque el modelo subestima menos en términos netos. El balance conjunto de 19,27 % frente a 19,40 % es favorable por 0,13 puntos y no implica superioridad uniforme.

{{tabla:global}}

La @tab_global completa el contraste técnico. El modelo registra menor MAE y mayor proporción dentro de ±8 %, mientras el referente tiene menor RMSE y MAPE. La conclusión depende del criterio y la escala, no sólo de un ganador agregado. El sesgo neto del modelo es −{{dato:sesgo_tallos_modelo}} tallos frente a −{{dato:sesgo_tallos_referencia}} del referente, calculado sobre casos de pronóstico repetidos por horizonte; estas sumas no representan faltantes físicos únicos de todo el año. La posible utilidad se concentra en revisar mejor las primeras semanas, sujetas a la equivalencia de información y unidad aún pendiente.

{{tabla:train}}

La @tab_train contrasta entrenamiento y evaluación del mismo ajuste de octubre. No se compara el entrenamiento de ese mes con un test arbitrario de otra configuración. La diferencia también refleja composición y dificultad del periodo; por sí sola no prueba ausencia de sobreajuste. La evidencia de generalización está limitada por el carácter retrospectivo de la selección y las fuentes, por lo que se requiere una evaluación prospectiva congelada.

### 4.4. Extensión reciente, especialización y segmentos de error

{{tabla:extension}}

En @tab_extension se evalúan únicamente objetivos desde la semana 37. H1 conserva una mejora: 12,10 % frente a 17,07 %, con sesgo −0,21 % frente a −11,18 %. H2 también mejora, pero H3–H5 deterioran el balance global: 18,10 % frente a 17,66 %. H1 tiene seis semanas nominalmente comparables en esta extensión, mientras otros horizontes reúnen siete; no se inventan estimados ausentes para igualar los tamaños.

En los mismos 3.399 casos, el ajuste congelado registra WAPE de 18,17 % y el actualizado mensualmente 18,10 %. La diferencia de 0,07 puntos es pequeña y no demuestra estabilidad en emisiones futuras. El modelo mensual reduce el error absoluto pero no mejora todos los indicadores: su sesgo −4,76 % queda algo más lejos de cero que el −4,59 % del congelado. Actualizar entrenamiento no garantiza superar al referente ni mejorar simultáneamente toda métrica.

Los ensayos de modelos por horizonte, n−1 y propios de producto se informan en el anexo C con sus paneles originales. La combinación de modelos propios obtuvo 17,53 % frente a 17,80 % de otra combinación autónoma, pero el referente logró 16,34 % en esos 1.226 casos. Son comparaciones recientes y acotadas, no un reemplazo demostrado del modelo principal. La mejora local motivó continuar examinando H3–H5; no autoriza a escoger retrospectivamente un ganador distinto para cada semana.

{{tabla:productos}}

La @tab_productos descompone el panel ampliado. Miniclavel aporta {{dato:aporte_mini}} puntos de los 19,27 de WAPE del modelo por su volumen, aunque su WAPE sea parecido al del referente; clavel presenta una diferencia desfavorable mayor. Raffine favorece al modelo. El diagnóstico permite priorizar revisión agronómica y pruebas posteriores por producto y horizonte, sin confundir un porcentaje alto en un segmento pequeño con la mayor contribución al error global. Las causas concretas requieren contrastar siembras, manejo, corte y registro, no sólo observar correlaciones.

### 4.5. Resultados diarios y límites de comparación

(El componente diario continúa en revisión; estos resultados no constituyen una solución diaria operativa validada.)

{{tabla:diario}}

En los 22.973 días reportados comunes de @tab_diario, el reparto reconciliado aprendido reduce el WAPE del uniforme de 28,80 % a 27,26 % y conserva el total semanal del que parte. El autónomo obtiene 26,72 %, pero no garantiza esa coherencia. No se compara esa diferencia como si ambos recibieran el mismo insumo: uno usa el total semanal y el otro no. El resultado depende de los errores de dicho total y del patrón de reporte; no demuestra que los días ausentes tengan producción física cero.

{{tabla:sarima}}

En @tab_sarima, SARIMAX obtiene 24,53 % y SARIMA 24,91 % en 135 días comunes. Es una diferencia exploratoria en tres series, no evidencia de superioridad para toda la finca. La reconciliación de esos métodos aumenta el error y la subestimación en este piloto; imponer un total semanal puede perjudicar una trayectoria diaria si ambos componentes son incompatibles. Los ajustes no convergentes y la exigencia de casos comunes restringen la muestra.

{{tabla:lstm}}

La @tab_lstm corresponde a un día adelante en septiembre, no a una semana emitida conjuntamente. Sin clima, la LSTM obtiene 27,17 %, frente a 27,71 % de la media de siete días observados en su soporte; el panel estricto de comparación entre todos los métodos, incluido clima, se reduce a 1.888 casos y se conserva en el anexo C. La muestra, las fechas y la tarea difieren de las del reparto semanal. La falta de predicciones archivadas de entrenamiento y validación en tallos, y la selección retrospectiva de series, impiden una conclusión firme de generalización. No se recomienda reemplazar el esquema semanal con este piloto.

### 4.6. Implicaciones organizacionales y condiciones de uso

El principal aporte operativo es una sugerencia cuantitativa interpretable y revisable, especialmente útil para contrastar el estimado de las primeras dos semanas. Conservar el valor original, el ajuste del responsable y la versión publicada permite estudiar posteriormente cuándo el conocimiento experto mejora la propuesta. El prototipo verifica ese flujo y la coherencia de los totales; no mide todavía ahorro, servicio ni efecto sobre ventas, compras o poscosecha.

Las limitaciones atraviesan las fases: las fuentes no acreditan toda su disponibilidad histórica; los pilotos no validan por sí solos la transferencia agronómica; el corte reportado no está conciliado con exportable; la comparación de emisión debe igualar el jueves; y los modelos exploratorios se examinaron en ventanas pequeñas. Los resultados justifican un piloto controlado con fuentes congeladas al emitir y métricas por horizonte, no una sustitución incondicional del responsable de producción.

Los siguientes pasos son acordar la unidad comercial y calendario de publicación, registrar pronósticos realmente anticipados, evaluar estabilidad en nuevas semanas y verificar las diferencias por producto. Los umbrales de faltante, normalidad y sobrante deben definirse con responsables y acciones empresariales antes de presentarse como señales validadas. El pronóstico diario requiere además un origen común de siete pasos y evaluación de calendarios de reporte. Esas condiciones delimitan el uso de la herramienta, sin negar el valor del desarrollo ya comprobado.

## 5. Conclusiones

**Objetivo general.** Se construyó una propuesta analítica reproducible de pronóstico semanal y una evaluación diaria exploratoria. En GAITANA, el modelo semanal seleccionado registra WAPE de 19,27 % frente a 19,40 % del referente en el panel retrospectivo ampliado. La ventaja se concentra en las primeras dos semanas y no acredita una superioridad general ni una validación de producción exportable. Para la organización, constituye una base para contrastar y documentar la revisión del estimado.

**Objetivo específico 1.** La integración preservó las fuentes, sus niveles de detalle y sus fechas, y consolidó un panel semanal sin sumar inventarios repetidos como nuevas siembras. Se distinguieron los 216.127 casos con real de los 148.435 con historia admisible y de las comparaciones nominales. La trazabilidad facilita actualizar información y estudiar discrepancias; no resuelve la disponibilidad histórica no registrada ni la conciliación comercial pendiente.

**Objetivo específico 2.** Las curvas empíricas relacionaron rendimientos piloto con edad y permitieron delimitar cuándo su suma representa todo el inventario. La correspondencia única de 99,84 % en los cortes piloto fechados en 2026 no equivale a la proporción de casos con todas las edades representadas. Conservar una ruta basada en producción reciente evita presentar referencias parciales como totales o eliminar el real observado. La representatividad agronómica de la curva compartida sigue siendo un supuesto por revisar.

**Objetivo específico 3.** La comparación temporal respaldó la configuración sin clima, con grupos H1–H2/H3–H5 y corrección de teoría o Media4. En H1 obtuvo WAPE de 15,04 % y sesgo −0,94 %, frente a 17,02 % y −7,97 % del referente; la extensión reciente conserva esa ventaja. El referente mantiene menor WAPE en H3–H5 y en el agregado de la extensión. Estos contrastes orientan la prioridad de mejora y evitan prometer una sustitución universal con evidencia parcial.

**Objetivo específico 4.** Se diferenciaron el pronóstico diario autónomo, la reconciliación semanal y el ensayo recurrente de un día adelante. El reparto aprendido mejoró al uniforme en su panel, pero SARIMA/SARIMAX y LSTM conservaron tamaños, tareas y límites que impiden un ranking único. El prototipo permite revisar propuestas y ajustes; el impacto empresarial y la solución diaria de siete pasos requieren un piloto prospectivo y criterios operativos acordados.

## Referencias

[1] J. H. Friedman, “Greedy function approximation: A gradient boosting machine,” *The Annals of Statistics*, vol. 29, no. 5, pp. 1189–1232, 2001, doi: 10.1214/aos/1013203451.

[2] scikit-learn developers, “HistGradientBoostingRegressor,” *scikit-learn documentation*. Consultado: 4 nov. 2026. [En línea]. Disponible: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html

[3] R. J. Hyndman y G. Athanasopoulos, *Forecasting: Principles and Practice*, 3.ª ed. Melbourne, Australia: OTexts, 2021, caps. 5 y 9. [En línea]. Disponible: https://otexts.com/fpp3/

[4] scikit-learn developers, “Common pitfalls and recommended practices,” *scikit-learn documentation*. Consultado: 4 nov. 2026. [En línea]. Disponible: https://scikit-learn.org/stable/common_pitfalls.html

[5] S. Hochreiter y J. Schmidhuber, “Long short-term memory,” *Neural Computation*, vol. 9, no. 8, pp. 1735–1780, 1997, doi: 10.1162/neco.1997.9.8.1735.

[6] Google Cloud, “MLOps: Continuous delivery and automation pipelines in machine learning,” *Cloud Architecture Center*. Consultado: 4 nov. 2026. [En línea]. Disponible: https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning

## Anexo A. Lectura y diccionario de la base analítica

Una fila representa una serie comercial y una semana objetivo vistas desde un origen. Por ejemplo, el origen 3 de agosto de 2026 en H5 apunta a la semana del 31 de agosto al 6 de septiembre. La producción de esa semana sólo se conoce posteriormente; no entra como predictor. La teoría se refiere a ese objetivo, no a la suma de las cinco semanas. Una referencia parcial puede conservarse para trazabilidad aunque no se habilite en la ruta teórica. Un campo vacío significa desconocido o no aplicable, nunca cero por definición.

{{tabla:diccionario}}

Las coordenadas anuales usan seno(2π × semana ISO/52) y coseno(2π × semana ISO/52). Son posiciones en un círculo, no porcentajes de tallos: las semanas 52 y 1 quedan próximas aunque sus números difieran. Para la semana 36 los valores son aproximadamente −0,935 y −0,355. El periodo fijo de 52 aproxima los años con semana ISO 53. Las teorías previas cuentan versiones anteriores del plano para el mismo objetivo; pueden existir en H5 porque cada plano genera diez semanas de proyección.

## Anexo B. Análisis climático complementario

{{figura:clima}}

La @fig_clima conserva la comparación exploratoria entre pares disponibles y casos comunes para las variables climáticas efectivamente contrastadas. Corresponde a objetivos terminados antes del 7 de julio de 2025, con curva aplicable y al menos veinte pares por serie–horizonte. El panel común de H1 conserva 5.078 casos y 142 orígenes; 95 series cumplen el soporte para resumir asociaciones. La restricción cambia el universo frente al panel disponible, no demuestra deterioro de los datos ni una mejora de WAPE. Una medición de finca repetida entre variedades no crea observaciones ambientales independientes. Las asociaciones orientan hipótesis; la selección se realizó mediante predicción temporal.

## Anexo C. Comparaciones complementarias

{{tabla:complementos}}

Cada bloque de @tab_complementos conserva sus casos y fechas originales: la adición de señales diarias y memoria utiliza el panel histórico de 15.838 casos; las pruebas recientes por horizonte, calibración y modelos propios utilizan 1.226; n−1 cambia de subconjunto según el producto retirado. Las métricas no constituyen una secuencia de mejoras sobre un único test. Las predicciones de entrenamiento y validación no archivadas en tallos no se sustituyen por las del test. La prueba prospectiva y la igualdad de corte de emisión permanecen como condiciones para confirmar cualquier cambio.
