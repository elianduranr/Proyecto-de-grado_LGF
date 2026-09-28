# Contexto vigente del proyecto

## Objetivo

Estudiar la desviación entre estimado y producción reportada por producto/color/variedad, con siembras, edad, curvas y clima. La producción real reciente debe investigarse como información para ajustar las semanas siguientes, sin afirmar causalidad biológica. Ya hay base, EDA y una primera comparación de modelos ejecutados.

## Arquitectura actual

Originales → cinco limpiezas → bases limpias → base analítica → EDA/benchmark → features/modelos.

- Limpiezas 01–05: `Notebooks/Limpieza data, Notebooks y Scripts/`.
- WebFlor: `Notebooks/Extracción SQL/02_webflor_complemento_necesario.ipynb`, modo local por defecto.
- Base/EDA/features/modelos 06–09: `Notebooks/Analisis/`.
- Ocho datasets oficiales: `Datos_analiticos_proyecto/`.

Cada notebook es autocontenido. Una salida fija por proceso; SQL sólo dos salidas finales. No crear módulos, frameworks, manifests, versiones, hashes, cifrado o backups automáticos. Los controles se muestran dentro de los notebooks.

## Fuentes y reglas que se deben preservar

Cinco familias: 24 Excel de curvas/pilotos, 6 de clima, 184 estimados, 294 planos y 6 de producción. No modificar originales.

El usuario considera referencia principal `Notebooks/03_benchmark_estimado_ingeniero.ipynb` y los tres notebooks originales de extracción, producción y benchmark de la carpeta de limpieza. Están recuperados para consulta. No volver a perder sus reglas ni ejecutar su antigua cadena de exports en paralelo al flujo oficial.

### Estimados

Leer TIPO=ESTIMADO de las cachés internas Excel. Seleccionar archivo principal no ajustado por año/semana; marca ENVIO y sello de descarga participan en la prioridad original.

Tomar año del nombre antes que carpeta. Existe un archivo 2024-S01 dentro de 2023.

Si no existe el archivo exacto, usar el siguiente disponible del mismo año. Construir H1–H5 desde la semana solicitada, no desde el nombre del archivo posterior. Preservar origen solicitado, nominal, objetivo, archivo y desfase.

2026-S02 se recupera de S03: 970 líneas H1–H5, contrastadas con las funciones del original. Si la caché no contiene una semana objetivo no inventar cantidades.

Salida oficial verificada: 176.140 líneas; 178 archivos principales, 193 solicitudes y 15 recuperaciones. Las 162.827 líneas de entregas exactas coinciden con la extracción anterior sin diferencias de cantidades. Tres solicitudes sólo tienen cuatro horizontes presentes; no completar con ceros.

El archivo posterior es recuperación retrospectiva, no evidencia de disponibilidad previa. No retirarlo del benchmark por ese motivo: conservarlo y separar su evaluación.

### Producción

Todas las hojas de detalle configuradas, incluidas particiones; sólo retirar filas completamente vacías. No deduplicar movimientos legítimos. Normalizar dimensiones, fechas, enteros y horas.

Mantener la imputación original de Tipo Corte mediante moda de producto/color/variedad en semana anterior/actual/siguiente dentro del libro; conservar original y bandera. Es retrospectiva y no entra como X conocida al origen.

6.389.201 movimientos; Gaitana conserva 4.654.552 movimientos y 327.991.200 tallos. El panel conserva 44.053 llaves semanales sin diferencias de cantidad. GAITANA PPTO es distinta de GAITANA. La unidad es tallos reportados, no exportable certificado.

### Benchmark

Agregar líneas del estimado por llave comercial/horizonte sin sumar distintos archivos de la misma solicitud. Unión estricta y, sólo para pendientes con correspondencia única, unión por finca/producto/variedad/semana. No forzar N:N ni elegir un color arbitrario. Preservar color real y estimado, método y procedencia.

No convertir pendientes en ceros. Se mantienen los cinco horizontes en columnas del panel para no multiplicar tallos reales.

El panel vigente tiene 44.053 filas y 108 columnas. Las métricas excluyen sumas de estimados con cantidades fuente faltantes y separan archivos posteriores de entregas nominales.

### Planos, curvas y clima

Planos = estado semanal, no eventos de nuevas plantas para sumar. Elegir edición explícita; señalar segmentos ambiguos y discrepancias de edad. 2022-S02 no tiene hoja Datos.

La edad fuente se valida contra ROUND((AL1 − fecha_siembra)/7, 0), reconocida en los 293 libros con Datos. No confundir AL1 con lunes nominal ni fecha de publicación. Conservar edad reportada, edad esperada en AL1 y edad calculada al lunes. La corrección recuperó cobertura válida: edad en 42.818 filas del panel y potencial en 9.058, sin relajar soporte ni borrar producción.

Curvas = observación empírica piloto, distinta del coeficiente WebFlor. Desduplicar libros acumulativos con identidad defendible. Potencial descriptivo exige soporte/cobertura y no es predictor histórico si usa todo el histórico de curvas.

Clima = mediciones desduplicadas, agregadas a día y semana. Conservar conflictos/horas inválidas y cobertura. No usar clima futuro observado.

Semana 53 → semana 1 del siguiente año en todas las fuentes analíticas, preservando fechas y etiquetas originales.

## WebFlor

Sí hay histórico: 1.354.556 filas archivadas semanales y 22.985 diarias; estado actual 308.449; captura previa adicional 44 filas de GAITANA PPTO/2020. Total limpio 1.686.034. No sumar categorías.

El archivo SQL se relaciona con erradicaciones; FechaAuditoria no certifica generación. Una referencia puede persistir varias semanas: no exigir corridas semanales. Hay que validar disponibilidad, ámbito y eventos de sustitución/retiro antes de una corrección histórica.

No aplicar as-of sobre FechaAuditoria para crear una historia ficticia. No hay generaciones confirmadas en el limpio. La regla futura sería última referencia acreditada anterior al origen, por ámbito/objetivo, hasta reemplazo o retiro. Los coeficientes quedan auxiliares: el plano no identifica inequívocamente curva/ciclo SQL ni hay vigencia histórica probada.

Coeficientes internos: 128.567; SemanaDia es edad, PickPeriodo define días/semanas y PickForma la base documentada área/plantas. Sin vigencia histórica certificada.

SiembraCama/Historico/Log y maestros sólo complementan identidad de estas proyecciones, en memoria. No se exporta otro plano SQL. Cortes, clasificación e inventarios SQL están fuera del pipeline.

No conectar al servidor para esta fase local ni generar nuevas proyecciones.

## Análisis y modelado

07 estudia cobertura/asociaciones y benchmark descriptivo, separando archivos posteriores y métodos de unión. No presentar sus métricas como corrección WebFlor validada ni correlación como causalidad.

08 calcula rezagos calendarios, medias 4/8, tendencia y casos origen/horizonte en memoria. No utiliza objetivos futuros, imputación retrospectiva de Tipo Corte, potencial de todo el histórico ni estimados sin disponibilidad al origen. Clima: al menos cinco días por semana, lag1/media4 pasados. Planos: as-of bajo disponibilidad supuesta posterior al cierre nominal y a AL1, con tolerancia de cuatro semanas. Publicación real pendiente; una prueba de perturbación futura confirma que X anteriores no cambian.

09 está ejecutado: tres cortes temporales, ocho orígenes por bloque y H1–H5; último valor, media4, reacción fija del 50%, Ridge y variantes de boosting. Misma preparación explícita que 08, sin módulos propios ni datasets nuevos. Se requieren 26 observaciones previas y cuatro semanas recientes completas; 14.108 casos, 172 series, no toda la población de la finca.

Resultados iniciales: WAPE media4 22,39%, último valor 20,19%, Ridge 19,60%, boosting completo 20,30%. Añadir memoria productiva al boosting comparable mejora 4,76 puntos; añadir este bloque climático no mejora el conjunto. Ridge falla en bajo volumen (131,15% frente a 43,32% del último valor); no seleccionarlo por su métrica global. La demora adicional de una semana empeora el boosting de 19,92% a 23,09% sobre iguales casos del último bloque.

Se muestra una corrección de media4 y una simulación desde el último origen local 2026-09-07, para 118 series. No se presenta como emitida entonces ni como pronóstico actualizado a hoy. No es corrección WebFlor validada. Pendientes: disponibilidad, ausencia/cero, equivalencia exportable, variedades nuevas y validación en periodo nuevo. Los resultados son retrospectivos bajo supuestos, no aprobación operativa.

Documentación principal: `GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md`. Diseño del estudio: `METODOLOGIA.md`.
