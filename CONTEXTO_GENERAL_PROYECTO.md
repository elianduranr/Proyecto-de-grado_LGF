# Contexto general del proyecto de tesis

## Propósito

Construir y evaluar una metodología reproducible para pronosticar tallos exportables de flores en la finca **La Gaitana**, a nivel de producto, color y variedad, con horizontes semanales de corto plazo. El resultado se comparará contra el estimado preparado actualmente por el ingeniero para saber si el modelo aporta una mejora real y operativamente útil.

## Alcance acordado

- Finca: exclusivamente **La Gaitana**. En las fuentes puede aparecer como `GAITANA`, `LA GAITANA`, `GF` u otras variantes; durante la limpieza se normaliza como `GAITANA`.
- Variable principal: tallos exportables.
- Granularidad de evaluación: primero producto-color y después producto-color-variedad.
- Frecuencia: diaria cuando la fuente lo permita y semanal para comparar pronósticos.
- Horizonte principal: semanas +1 a +5; se admitirán horizontes mayores en temporadas especiales.
- Periodo disponible: las fuentes observadas cubren principalmente 2021-2026, con cobertura distinta por fuente.
- Formato preprocesado: CSV para inventarios, auditorías y tablas de tamaño moderado. La base relacionada de Curvas usa Parquet por superar dos millones de filas; evita un CSV redundante de cientos de MB y conserva tipos.

## Pregunta central

Qué variables productivas, climáticas y del plan de siembra explican los cambios en la producción exportable semanal, y si un modelo basado en esas variables puede igualar o superar el estimado empírico actual.

## Fuentes y uso previsto

### Producción real

Es la verdad observada para entrenar y evaluar. Se conservan fecha y semana de corte, finca, sector, invernadero, producto, color, variedad, grado, tipo de corte, lote y tallos. Las columnas administrativas o de inventario que no aportan al objetivo quedan fuera.

### Estimados semanales

Son libros con tablas dinámicas/matrices. De cada Excel se extrae exclusivamente la base del bloque `ESTIMADO` y se guarda un CSV independiente dentro de `datos preprocesados/por año/<año de emisión>/`. Cada fila conserva el archivo de origen, año de emisión, semana inicial y final del envío, finca, producto, color, variedad, año/semana objetivo, horizonte y tallos. Esta fuente representa el benchmark del ingeniero.

Los envíos son versiones sucesivas del pronóstico y **no son intercambiables**. Por ejemplo, el estimado de la semana objetivo 2 incluido en el envío 1-5 es una observación distinta del estimado de esa misma semana 2 incluido en el envío 2-6. La primera fue emitida con mayor anticipación; la segunda incorpora una semana adicional de información. Ambas se conservan para medir cómo cambia la predicción y cómo mejora o empeora según el horizonte.

### Clima

La hoja base es `BD`. Se conservan fecha/hora, sede, temperatura, humedad, punto de rocío, viento, lluvia, radiación solar, UV, evapotranspiración y PAR cuando existen. Para modelar semanalmente se deberán crear agregados como media, mínimo, máximo, suma y variabilidad.

### Plano de Siembras

La fuente principal es la pestaña cruda `Datos`. Se conservan finca, invernadero, sector, cama, producto-color-variedad, plantas, fechas de siembra/producción, sustrato, propagador, proveedor y edad. Se excluyen valores vacíos y errores de Excel como `#REF!`, pero se registra su falta de cobertura.

Los archivos no son bases independientes: cada uno muestra el **estado completo del plan en una semana**. En nombres técnicos antiguos se usa “fotografía”, pero no se trata de una imagen. La capa primaria queda organizada como `datos preprocesados/bases semanales/<año>/siembras_<año>_semana_<nn>.csv`. Por eso se procesan las 294 versiones disponibles y se materializan cuatro niveles:

1. CSV limpio de cada archivo semanal, con año, semana y fecha de referencia semanal;
2. estado vigente del último archivo;
3. historial de diferencias entre archivos consecutivos;
4. tabla de ciclos únicos para cruces analíticos.

La llave provisional para seguir un ciclo es `invernadero + cama + fecha_siembra`. Producto, color, variedad, plantas, sustrato, propagador y proveedor se comparan como atributos que pueden cambiar. Esta llave es una hipótesis técnica y debe ser confirmada por Producción.

No se calcula el anterior “ciclo observable” con `FECHA PRODUCCION`: la definición de ese campo no está confirmada y su cobertura desaparece casi por completo desde 2022. Las curvas usan directamente `Edad` en semanas.

### Curvas por variedad

Son 24 libros (cuatro familias por año, 2021-2026). Las hojas analíticas son `Base de Datos` —denominada `corte semanal` en Green Ball— y `Camas Piloto`. La primera contiene corte semanal, edad y flores por planta; la segunda aporta referencia, variedad, bloque, cama y número de plantas.

La unión se resuelve dentro de cada libro mediante una cascada auditable: referencia normalizada única; referencia + fecha de siembra cuando una cama fue reutilizada; y variedad + bloque + cama únicamente si produce un candidato único. Los casos muchos-a-muchos no se expanden. `Flor/Planta` fue comprobado contra `Corte Semanal / No. Plantas` y se interpreta como **flores por planta por semana**.

### Fuentes actualmente vacías

La carpeta independiente `Camas Piloto` no contiene archivos originales, pero los 24 libros de `Curvas por variedad` sí incluyen una hoja `Camas Piloto`, que ya se procesa. `Estimados diarios` continúa sin originales.

## Principios de preparación

1. Los Excel originales nunca se modifican.
2. Cada fuente guarda resultados dentro de `datos preprocesados`. En Plano de Siembras, las fotografías limpias se separan por año en `bases semanales`; los productos derivados van en `bases consolidadas`, la calidad en `auditoria` y los manifiestos en `_control`.
3. El manifiesto registra tamaño, fecha de modificación, hash, filas y estado de cada archivo.
4. Un archivo se reprocesa solo si es nuevo, cambió o perdió su salida.
5. Se filtra a Gaitana durante la extracción para reducir volumen.
6. Se conservan las llaves necesarias para unir fuentes y la trazabilidad del archivo/hoja de origen.
7. Las duplicaciones exactas y solapamientos entre hojas se controlan antes de agregar producción.
8. La repetición de un ciclo entre fotografías semanales no se trata como duplicado: representa permanencia del estado.
9. Un dato ausente no se reconstruye con una correlación ni con una fórmula rota; se conserva como ausente y se convierte en solicitud de calidad para PDN.
10. En estimados, dos filas con la misma semana objetivo y producto-color no son duplicadas si pertenecen a emisiones diferentes. Solo se eliminan duplicados exactos dentro de un mismo archivo/emisión.

## Llaves de integración

La llave analítica mínima propuesta para producción, clima y siembras es:

`finca + anio + semana + producto + color`

La llave detallada agrega `variedad`. Cuando la calidad lo permita, se pueden sumar `invernadero`, `sector`, `nave` o `cama`. Los textos deben normalizarse antes de unirlos; una coincidencia aparente no garantiza que los catálogos usen la misma ortografía.

Para los estimados, la llave debe agregar la versión del pronóstico:

`archivo_origen/id_emision + anio_objetivo + semana_objetivo + producto + color (+ variedad)`

El horizonte se calcula dentro de cada emisión. Al cruzar con producción real, varias emisiones pueden apuntar a una misma semana real; se evalúan por separado y luego se resumen por horizonte. Nunca se debe sumar primero entre emisiones, porque eso mezclaría revisiones distintas del mismo pronóstico.

## Evaluación del estimado actual

Se comparará cada predicción del ingeniero con la producción real de la misma semana objetivo. Las métricas principales son MAE, RMSE, sesgo, WAPE y porcentaje dentro de ±8 %. Algunas salidas históricas todavía llaman `WMAPE` a la misma fórmula `Σ|error| / Σ|real|`; debe unificarse la etiqueta sin cambiar el cálculo. MAPE se reportará con cuidado porque falla o exagera cuando la producción real es cero o muy pequeña.

Para la revisión inicial se tomarán, con semilla reproducible, hasta tres emisiones de 2024, tres de 2025 y tres de 2026 que tengan cruce con producción real. Además de la muestra, el notebook dejará preparado el histórico completo. Los resultados deben mostrar volumen, error y sesgo por horizonte, producto y color: equivocarse en un color de alto impacto no equivale a hacerlo en uno marginal.

## Diseño recomendado de la tabla de modelado

Una fila por semana, producto, color y variedad de Gaitana. Debe incluir:

- objetivo: tallos reales de la semana futura;
- identificadores y calendario: año, semana ISO, producto, color, variedad y temporada comercial;
- rezagos productivos: tallos de semanas anteriores, medias móviles y tendencia;
- siembra: plantas, área, densidad, edad/ciclo y semanas desde la siembra;
- clima: acumulados y resúmenes semanales, además de rezagos coherentes con el ciclo productivo;
- benchmark: estimado del ingeniero y horizonte;
- controles de calidad: cobertura del cruce, dato imputado y procedencia.

La separación de entrenamiento y prueba debe ser temporal, nunca aleatoria entre filas. Conviene evaluar por horizonte y reservar periodos completos recientes, incluyendo picos comerciales.

## Riesgos y decisiones pendientes

- La relación causal entre siembra y tallos exportables aún debe validarse con el negocio: fechas de producción, curvas y ciclos podrían ser planeados, reales o recalculados.
- Puede haber nombres distintos para la misma variedad/color/producto entre fuentes; se necesita un catálogo maestro o reglas de homologación auditables.
- Producción puede contener hojas solapadas. Antes de sumar se deben eliminar duplicados exactos y revisar si existen movimientos/correcciones legítimos.
- Faltan datos de camas piloto y estimados diarios; no deben asumirse como disponibles.
- El clima puede variar por estación o código dentro de Gaitana; hay que confirmar qué sensor representa cada bloque/invernadero.

## Hallazgos de la primera ejecución y EDA revisado (20 de agosto de 2026)

- Producción: 4.618.351 filas útiles de Gaitana en seis libros (2021-2026).
- Clima: 644.995 mediciones de Gaitana en seis libros. Los formatos 2021-2022 fueron adaptados desde `Base de datos Gaitana`; 2023-2026 usan `BD`.
- Estimados semanales: 180 envíos únicos y 148.502 filas exclusivamente `ESTIMADO`, distribuidas en 180 CSV independientes por emisión: 49 de 2023, 49 de 2024, 47 de 2025 y 35 de 2026. Los bloques `REAL` de las matrices no se incorporan porque la verdad observada proviene de Producción real.
- Plano de Siembras contiene 294 libros entre 2021 y 2026: 293 se extrajeron, uno (semana 02 de 2022) no contiene la hoja cruda y dos versiones de la semana 32 de 2026 se conservan pero una sola alimenta el análisis. El análisis longitudinal usa 292 archivos semanales seleccionados y 2.244.148 filas acumuladas de Gaitana.
- `FECHA PRODUCCION` es muy inestable entre versiones: aparece en 32 de 52 fotografías de 2021, 2 de 51 de 2022, una fotografía de 2023, una de 2024 y ninguna de 2025-2026. Esto demuestra que el libro semanal cambia de estructura/contenido y no debe tratarse como seis bases anuales estáticas.
- El historial detectó 50.340 altas, 78.000 modificaciones y 42.612 desapariciones frente a la fotografía anterior. De las modificaciones, 41.952 cambian valores informados, 35.358 son solo aparición/desaparición de datos y 690 son mixtas. Esta separación evita confundir un cambio de cobertura del Excel con una decisión agronómica.
- Varias columnas agronómicas dependen de fórmulas rotas (`#REF!`) o cambian de posición entre versiones. El extractor combina columnas duplicadas solo cuando el valor es válido y conserva su procedencia.
- Los análisis parten de 292 archivos semanales seleccionados: 293 bases extraídas menos una versión alternativa de la semana 32 de 2026. La semana 02 de 2022 permanece documentada como faltante de base cruda.
- Curvas por variedad aportó 2.347.275 observaciones longitudinales. El 78,24 % enlaza por referencia única y otro 5,21 % mediante referencia + fecha de siembra; 15,13 % queda ambiguo y 1,42 % sin match.
- La detección automática de encabezados fue necesaria: Clavel inicia `Camas Piloto` en la fila 1, mientras Miniclavel y Raffine/Solomio usan una fila numérica auxiliar y el encabezado real está en la fila 2.
- En 1.946.600 filas con cama y plantas comparables, 99,93 % de `Flor/Planta` coincide con `Corte Semanal / No. Plantas` a tolerancia 1e-8. Esto confirma la unidad operativa flores/planta/semana.
- La réplica `plantas × curva mediana` cubre típicamente 97,3 % de las plantas. Su WAPE por variedad pasa de 31,43 % en +1 a 28,72 % en +5 y tiene sesgo positivo. En los pares disponibles, el ingeniero obtiene 23,06 % en +1 y 26,07 % en +5, con sesgo negativo. La réplica pura aún no reproduce sus ajustes.
- Los Excel del ingeniero cuentan la propia semana de emisión como horizonte 1. En este proyecto `+1` significa la semana siguiente; por eso la comparación de métodos se alinea por semana objetivo y el desfase modal de etiquetas es una semana.

En la evaluación histórica producto-color para horizontes +1 a +5, conservando cada emisión como una versión distinta, el estimado actual obtuvo WMAPE de 22,55 % en 2024, 21,07 % en 2025 y 20,35 % en 2026. El sesgo agregado fue negativo en los tres años, lo que indica una tendencia general a subestimar, aunque el signo cambia por producto-color.

Para **horizonte +1 exclusivamente**, el WMAPE es 19,79 % en 2024, 17,85 % en 2025 y 18,67 % en 2026. El porcentaje dentro de ±8 % es 20,69 %, 22,03 % y 23,81 %, respectivamente. El ingeniero subestima 61,45 % de los casos de 2024, 64,25 % de 2025 y 62,94 % de 2026. La siguiente semana debe tener un reporte y, posiblemente, un modelo propios.

La muestra reproducible de tres envíos por año se regenera en el notebook a partir del inventario vigente. Sus tablas y gráficas deben consultarse en la ejecución actual, en vez de copiar cifras que quedarían obsoletas al incorporar nuevos envíos. El benchmark completo y la muestra mantienen separadas las emisiones y se comparan fuera de muestra.

Los mayores errores acumulados se concentran en Minicarnation, especialmente light pink, orange, red, hot pink, yellow, white y lavender. Raffine bicolor burgundy/light pink también presenta WMAPE alto. Esto respalda reportar el error por valor operativo y no solo un promedio global.

Los envíos especiales pueden cubrir intervalos mucho mayores a cinco semanas, incluso cruzando de año. El extractor interpreta por separado el año/semana de emisión y el año/semana objetivo; aun así, la fecha exacta se infiere del nombre porque no existe un timestamp oficial. Se conservan todos los horizontes para auditoría, pero la evaluación principal se limita a 1-16 y los resúmenes centrales a +1 a +5.

## Preguntas prioritarias para la empresa

1. ¿Qué significa `FECHA PRODUCCION` y por qué aparece y desaparece hasta quedar vacía en 2025-2026?
2. ¿Cuál es la llave oficial de un ciclo y cómo se distingue una corrección semanal de una decisión agronómica?
3. ¿Pueden entregar la semana 02 de 2022 y las fuentes de curva, densidad y ciclo sin fórmulas rotas?
4. ¿Las filas repetidas de Producción son movimientos distintos o correcciones, y cuál es su ID/fecha de actualización?
5. ¿Qué grados, tipos de corte y descartes componen exactamente `tallos exportables`?
6. ¿Pueden entregar fecha/hora de emisión y confirmar si los estimados faltantes nunca se emitieron?
7. ¿Qué información usa el ingeniero para ajustar el horizonte +1?
8. ¿Cuál es el costo de subestimar/sobreestimar por producto-color y en temporadas comerciales?
9. ¿Qué estación climática representa cada sector o invernadero de Gaitana?
10. ¿Qué factores aplica el ingeniero además de `plantas × flores/planta` (aprovechamiento, pérdidas, estado de cama, ajuste comercial o rezago)?
11. ¿La edad de las curvas y la edad del Plano de Siembras usan exactamente la misma convención semanal?
12. ¿Cómo debe elegirse una cama cuando la misma referencia aparece varias veces con igual fecha de siembra?

## Artefactos de trabajo

- Plan original: `Plan de Proyecto/Plan de proyecto_final.docx`.
- Notebook autocontenido de extracción incremental, preparación y EDA: `Notebooks/01_preprocesamiento_y_eda_tesis.ipynb`. Es la fuente principal del flujo y no importa módulos `.py` locales.
- Generador independiente de la lista Excel de envíos faltantes: `Notebooks/generar_estimados_faltantes.py`. Lee el inventario vigente; no contiene una lista histórica fija.
- Descarga de correo (proceso independiente): `Extracción de estimado a 5 semanas por correo/descargar_estimados_selenium.py`.
- Datos limpios: dentro de cada fuente, en `datos preprocesados`.
- Fotografías limpias de siembras: `Datos/Plano de Siembras/datos preprocesados/bases semanales/<año>/`.
- Estado vigente e historia de siembras: `Datos/Plano de Siembras/datos preprocesados/bases consolidadas/`.
- Inventario, versiones, cobertura y resumen de cambios: `Datos/Plano de Siembras/datos preprocesados/auditoria/`.
- Curvas limpias, base relacionada, métricas y auditorías: `Datos/Curvas por variedad/datos preprocesados/`.
- Solicitudes de calidad a PDN: `Datos/solicitudes_calidad_datos_PDN.xlsx`.

Este archivo debe actualizarse cuando cambie el alcance, aparezca una nueva fuente o se confirme una definición de negocio.

Para retomar el trabajo en otra sesión, leer primero `PROXIMA_SESION.md`.
