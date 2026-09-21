# Informe interpretativo · MCA de GAITANA

**Lectura de la limpieza.** Se conservan **4,638,217 registros** y **326,664,331 tallos** en la selección. Hay **52,305 copias entre fuentes** retiradas antes del filtro de año ISO. Se imputaron **37,110 cortes**; **1,876,858** siguen sin referencia. Los años con más de la mitad de sus registros sin corte son **[2021, 2022, 2023]**. En la siguiente sección se ensaya una imputación adicional con validación entre años. Los faltantes de grado se revisan por año antes de interpretar cambios comerciales.

**Imputación de grado.** Se completan **61,003 registros adicionales**; **1,118,985** se conservan como SIN_REFERENCIA en la columna analítica. La regla entre años queda **habilitada**. El acierto por registros en años evaluables va de **94.6 %** a **99.7 %**, con coberturas entre **8.6 % y 16.6 %**. La escasa cobertura limita el alcance del acierto. No se conoce el valor real de los faltantes históricos.

**Imputación de tipo_corte.** Se completan **0 registros adicionales**; **1,876,858** se conservan como SIN_REFERENCIA en la columna analítica. La regla entre años queda **descartada por su validación**. El acierto por registros en años evaluables va de **42.8 %** a **100.0 %**, con coberturas entre **0.4 % y 6.2 %**. La escasa cobertura limita el alcance del acierto. No se conoce el valor real de los faltantes históricos.

**Cobertura del análisis.** El MCA utiliza **4,638,217 filas con fecha válida y tallos positivos**, equivalentes a **326,664,331 tallos**, en **6 años ISO**. El producto con mayor masa es **MINICARNATION**, con **62.9 %**. Las categorías con mayor volumen pesan más en el análisis ponderado; esto es intencional porque la unidad de interés es el tallo. Los totales de años parciales no son comparables directamente con años completos.

**Pico de 2021: semana 42**, del 2021-10-18 al 2021-10-23, con **2,282,123 tallos** y **32,336 registros**. Los bloques y sus filas de origen se detallan arriba. Las hipótesis de copia no modifican el total observado ni el análisis principal.

**Posible duplicación.** Entre los bloques 1 y 2 coinciden **16,125 registros** (**99.73 %** del bloque menor), respetando multiplicidades. La evidencia apunta a tres posibilidades: (1) una copia accidental dentro de la misma hoja, (2) una segunda exportación o fotografía operativa de la misma cosecha, enriquecida con identificadores de inventario, o (3) una segunda versión con correcciones. No parece una segunda cosecha independiente porque fecha, producto, color, variedad e invernadero se repiten fila a fila. En las 43 filas restantes, el primer bloque suma 4.177 tallos y el segundo 3.440: hay una diferencia neta de 737 tallos, siempre con 80 tallos en el segundo bloque. Esto prueba que existe una actualización o diferencia de carga, pero no permite decidir cuál cantidad es correcta. El segundo bloque además tiene Estado Inventario informado en las 16.168 filas, mientras el primero no lo tiene. Debe revisarse la procedencia y fecha de exportación antes de eliminar o reemplazar un bloque.

**Decisión sobre la semana irregular.** La semana 42 tiene **1.83 veces** la mediana de sus semanas vecinas (40–44) y **supera** el umbral IQR. Por eso la decisión operativa es: **REVISAR EN ORIGEN antes de usar la semana 42 para decisiones o modelos**. La alerta no autoriza borrar la semana ni convertirla en cero. Primero se debe confirmar en el Excel si los dos bloques son versiones de la misma carga. Hasta esa confirmación, los análisis descriptivos reportan el dato observado y separan este caso como alerta de calidad.

**Diagnóstico.** La asociación más alta de esta matriz es **K_grado–K_anio**, con **V = 0.423**. Entre producto y color es **0.298**; entre semana y producto, **0.021**. V describe una relación global, no su causa ni su estabilidad anual. Las asociaciones con SIN_DATO pueden reflejar cambios de registro. Para semana, agrupar todos los años puede diluir patrones distintos o confundirlos con diferencias de cobertura: se revisará su recurrencia explícitamente.

**Dimensionalidad.** El plano 1–2 recoge **9.7 % de inercia cruda** y **57.5 % según Greenacre**. La corrección no convierte el mapa en una explicación causal ni garantiza que todas sus categorías estén bien representadas. Para interpretar un punto revisaremos su cos² y su contribución, incluyendo los ejes 3–4 cuando el primer plano sea insuficiente.

**Decisión para las suplementarias.** Semana, año, variedad, invernadero, grado y corte sirven para explicar quién ocupa cada perfil, pero no alteran los ejes del MCA principal. Si una categoría aparece muy alejada, se debe comprobar primero su cos² y su volumen. Si aparece cerca del origen, no hay evidencia de un perfil propio en este plano. La siguiente decisión analítica es usar semana como activa solo en el modelo de sensibilidad, porque hacerlo puede repartir la inercia entre 52 niveles y volver menos estable la lectura del producto y el color.

**Lectura ejecutiva del mapa principal.** Las categorías que más construyen Dim1 son K_producto=GREEN BALL, K_color=GREEN, K_producto=RAFFINE, K_color=BICOLOR BURGUNDY, K_color=BICOLOR PURPLE. Las categorías mejor representadas en el plano son K_color=GREEN, K_producto=GREEN BALL, K_producto=RAFFINE, K_color=BICOLOR BURGUNDY, K_producto=MINICARNATION. Para gerencia, la primera lista indica qué perfiles explican la separación del mapa; la segunda indica dónde la lectura del plano es confiable. Una categoría cercana al origen no es necesariamente irrelevante: puede ser frecuente y poco diferenciadora. La acción recomendada es priorizar las categorías con alta contribución y cos², y consultar la tabla completa antes de intervenir sobre las demás.

**Dimensión 1.** La variable que más contribuye es **K_color (50.0 %)**. Las categorías que más construyen el eje son **K_producto=GREEN BALL** (44.1 %); **K_color=GREEN** (43.1 %); **K_producto=RAFFINE** (5.4 %); **K_color=BICOLOR BURGUNDY** (3.9 %); **K_color=BICOLOR PURPLE** (1.2 %). Estos nombres describen el contraste del catálogo; no son una clasificación de calidad de las flores.

**Contraste del eje 1.** En el lado positivo destacan K_producto=GREEN BALL, K_color=GREEN, K_producto=OTROS; en el negativo, K_producto=RAFFINE, K_color=BICOLOR BURGUNDY, K_color=BICOLOR PURPLE. El contraste expresa perfiles de coocurrencia. El signo podría invertirse sin cambiar el resultado.

**Dimensión 2.** La variable que más contribuye es **K_producto (50.0 %)**. Las categorías que más construyen el eje son **K_producto=RAFFINE** (40.5 %); **K_color=BICOLOR BURGUNDY** (31.1 %); **K_color=BICOLOR PURPLE** (6.2 %); **K_producto=MINICARNATION** (4.8 %); **K_producto=GREEN BALL** (4.4 %). Estos nombres describen el contraste del catálogo; no son una clasificación de calidad de las flores.

**Contraste del eje 2.** En el lado positivo destacan K_producto=RAFFINE, K_color=BICOLOR BURGUNDY, K_color=BICOLOR PURPLE; en el negativo, K_producto=MINICARNATION, K_color=HOT PINK, K_color=YELLOW. El contraste expresa perfiles de coocurrencia. El signo podría invertirse sin cambiar el resultado.

**Representación de categorías.** 4 de 34 categorías tienen al menos la mitad de su distancia al origen representada en el plano 1–2. Para las demás, la tabla completa y los ejes adicionales son necesarios antes de interpretar cercanías.

**Cómo leer estas proyecciones.** Si un grado aparece hacia el mismo lado que un producto o color, sus filas comparten parte del perfil descrito por ese eje. Eso no demuestra una relación causal. La posición de **SIN_DATO** informa sobre el registro, no sobre la flor. Las diferencias entre años también pueden reflejar cambios de catálogo, cobertura o criterios comerciales. Variedad e invernadero se conservan como detalle suplementario para investigar esas diferencias.

**Lectura temporal.** La curva conjunta indica cómo cambia el perfil promedio a lo largo del calendario. Las curvas por año permiten comprobar si esa forma se repite o si la produce un año particular. Una curva suave en el promedio no basta para afirmar estacionalidad: puede resultar de cobertura desigual o de cambios del catálogo. La siguiente sección contrasta directamente las curvas de participación por producto.

**Recurrencia observada.** Se compararon **29 semanas comunes**, de la **7 a la 35**. La mayor concordancia corresponde a **VERONICA**, con correlación media **0.215** y **q FDR = 0.180**. **0 productos** tienen correlación positiva y q ≤ 0,05 frente a los desplazamientos. Los restantes no muestran esa evidencia bajo este contraste; no equivale a demostrar ausencia de estacionalidad. Antes de usar estos patrones para planear, deben comprobarse en años reservados y con cobertura comparable.

**Volumen semanal.** La mayor concordancia corresponde a **CARNATION** (correlación media **0.566**; q FDR **0.030**). **2 productos** tienen correlación positiva y q ≤ 0,05. Este resultado se refiere a la forma de los volúmenes en el tramo común. Las discrepancias entre volumen y participación ayudan a distinguir variación propia del producto de cambios del total de la finca; ninguna de las dos pruebas identifica por sí sola su causa.

**Grado comercial.** Esta subbase representa **73.5 %** de los tallos del análisis principal. El grado aporta **49.7 % a Dim1** y **8.8 % a Dim2** de este segundo ajuste. La tabla producto–grado permite comprobar si el mapa está destacando una clasificación casi exclusiva de un producto. No se atribuye esa asociación al manejo agronómico ni se supone un destino comercial que el archivo no documenta.

**Semana activa.** Aporta **0.4 % a Dim1** y el plano 1–2 recoge **3.8 % de inercia cruda** en ese ajuste. Esto mide cuánto participa en los ejes cuando se le permite construirlos, no el porcentaje de producción explicado por el calendario. La comparación por registros cambia la pregunta: describe el registro típico, mientras el ajuste ponderado describe la distribución de los tallos.

**MCA sin eliminar faltantes.** Este ajuste incluye **4,638,217 registros**, el **100 % de los 326,664,331 tallos** de la base MCA. SIN_REFERENCIA aporta **0.0 % a Dim1**. Los porcentajes comerciales de la siguiente sección se calculan únicamente con grados observados; las filas sin grado siguen disponibles en la base general y en este ajuste.

**Asociación producto–grado.** V de Cramér es **0.353** en los tallos con grado conocido. Hay **31 combinaciones año–producto** con al menos dos variedades que cumplen 100.000 tallos y 12 semanas observadas. Sus diferencias se expresan en puntos porcentuales, sin cocientes inestables cuando una variedad tiene 0 %. Aun dentro del mismo producto y año, las semanas efectivamente cosechadas y la política comercial pueden explicar parte de la diferencia. Por tanto, el resultado orienta una revisión operativa; no demuestra un efecto causal de la variedad.

**Base y alcance.** 4,638,217 registros limpios de GAITANA; 4,638,217 evaluados en el MCA, entre 2021-01-04 y 2026-08-29. La auditoría permite reconstruir los libros y hojas utilizados.

**Estructura productiva.** K_color es la variable que más construye Dim1 (50.0 %). El primer plano resume 57.5 % de inercia Greenacre. Se interpretan contribuciones y representación de categorías, no una predicción de tallos.

**Clasificación comercial.** El MCA con grado utiliza 73.5 % de los tallos como referencia observada. El ajuste de sensibilidad con imputación y SIN_REFERENCIA conserva el 100 %. Los faltantes históricos limitan comparaciones; no deben leerse como cambios de calidad.

**Imputación trazable.** Se completan 61,003 grados adicionales en una columna separada. El traslado histórico del corte se evalúa y puede descartarse; los valores sin respaldo permanecen identificados sin eliminar sus registros.

**Semana.** Se conserva como categoría ordinal/cíclica para la interpretación cronológica, pero el MCA estándar la trata nominalmente. La proyección y el contraste entre años complementan el mapa.

**Producto y grado.** Su asociación descriptiva tiene V=0.353. El detalle por variedad y año no controla todas las diferencias de mezcla ni establece causalidad.

**Pico de 2021.** La semana 42 suma 2,282,123 tallos. La auditoría muestra los bloques fuente y sus coincidencias. La posible copia se mantiene señalada; ningún escenario alternativo sustituye el dato observado sin confirmar su procedencia.

**Repetición entre años.** En semanas 7–35, VERONICA tiene la mayor correlación media de participación (0.215; q=0.180). Es evidencia descriptiva sobre composición en ese tramo, No se detecta evidencia tras FDR si q supera 0,05; no es una garantía de repetición anual.

**Forma del volumen.** CARNATION tiene la mayor correlación media entre años (0.566; q=0.030) en el tramo común. Este contraste complementa la composición, sin confundir un mayor volumen con una curva más repetible.

**Siguientes comprobaciones.** Validar con la empresa las equivalencias de grados y los posibles solapamientos entre archivos. Para evaluar capacidad predictiva, reservar un año y comparar contra una referencia de la misma semana del año anterior. Si se quiere estudiar diferencias comerciales por variedad, controlar al menos producto y semana; el MCA por sí solo no identifica sus causas.