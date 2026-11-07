# Registro de cumplimiento — revisión del asesor

Documento: `Documento_LaGaitana_v9_revision_asesor_20261104_final.docx`, con PDF de comprobación. **Páginas verificadas: 36.**

Esta matriz responde a las indicaciones consolidadas del prompt del 04/11/2026. Sus IDs identifican apartados y viñetas del prompt, no pretenden reconstruir la numeración de los 60 comentarios originales. Las restricciones empíricas se incorporaron al texto; «implementada» no significa que se haya confirmado una equivalencia comercial o realizado un piloto aún pendiente. Esos faltantes concretos están en `PENDIENTES_EQUIPO.md`.

Se conservaron la configuración y las predicciones de los modelos. La revisión es editorial y de consistencia de evidencia, no una nueva selección estadística.

## 1. Forma de trabajo

| ID | Indicación | Cambio y ubicación | Estado |
| --- | --- | --- | --- |
| 1.01 | Identificar versión vigente y generadores | V8 identificada como base; se conservan fuentes y documentos. V9 se compone con plantilla, evidencia y renderizador propios. **Ubicación:** Fuentes y README de reproducción. | Implementada |
| 1.02 | Modificar fuentes y regenerar de manera reproducible | Prosa editable, tablas desde resultados, figuras desde Parquet y Word con campos REF/TOC. **Ubicación:** contenido_academico.md; scripts v9. | Implementada |
| 1.03 | Conservar copia inicial y avances válidos | Copia de MD/Word/PDF v8 y huellas; originales comprobados sin cambios. **Ubicación:** Version_inicial; version_inicial_sha256.json. | Implementada |
| 1.04 | Registro separado por indicación, cambio, ubicación y estado | Este registro incluye cada indicación consolidada, con IDs propios del prompt. **Ubicación:** REGISTRO_CUMPLIMIENTO.md/.csv/.json. | Implementada |
| 1.05 | Resolver edición y explicitar faltantes sin inventar | Se delimita alcance y se documentan faltantes concretos fuera del manuscrito. **Ubicación:** 1.2; 3.5–3.7; 4.6; PENDIENTES_EQUIPO.md. | Implementada |

## 2. Portada, resumen y palabras clave

| ID | Indicación | Cambio y ubicación | Estado |
| --- | --- | --- | --- |
| 2.01 | Cambiar título solicitado | Se aplica literalmente el título indicado en portada y propiedades del Word. **Ubicación:** Portada. | Implementada |
| 2.02 | Incluir asesor y conservar autores | Rafael Amaya Gomez; Elián Durán, Julián Osorio y Anderson Gonzalez. **Ubicación:** Portada. | Implementada |
| 2.03 | Reescribir resumen con contexto, problema, método, resultados y aporte | Resumen nuevo, centrado en el apoyo al estimado y con resultados acotados. **Ubicación:** Resumen. | Implementada |
| 2.04 | Explicar productos, tallos y corte antes de cifras | Se presentan flores de corte, unidad reportada y actividad de cosecha. **Ubicación:** Resumen; 1.1. | Implementada |
| 2.05 | Evitar siglas indefinidas y definir horizontes reales | Resumen usa primera semana; H1–H5 se definen con calendario y edición 18–22. **Ubicación:** Resumen; 1.1–1.2. | Implementada |
| 2.06 | Presentar propósito analítico sin centrar resumen en Gradient Boosting | Se explica integración, corrección y utilidad; el algoritmo se desarrolla después. **Ubicación:** Resumen; 3.4. | Implementada |
| 2.07 | Identificar función del profesional de referencia | Se define responsable de producción y se usa esa denominación consistentemente. **Ubicación:** 1.1; tablas de resultados. | Implementada |
| 2.08 | Ajustar palabras clave a curvas y métodos reales | Curvas empíricas de rendimiento, boosting, SARIMA/SARIMAX y reconciliación; se retiran calidad y validación temporal. **Ubicación:** Palabras clave. | Implementada |

## 3. Introducción, problema, objetivos y alcance

| ID | Indicación | Cambio y ubicación | Estado |
| --- | --- | --- | --- |
| 3.01 | Comenzar explicando empresa, productos y proceso verificable | Contexto basado en categorías de las fuentes y flujo del proyecto; no se inventan ubicación, área o historia empresarial. **Ubicación:** 1.1. | Implementada |
| 3.02 | Ampliar contexto para lector no experto | Se conecta cultivo, inventario, corte y decisiones de disponibilidad. **Ubicación:** 1.1; 2.1. | Implementada |
| 3.03 | Explicar pronóstico actual, responsable, información y decisiones | Se describe revisión de cultivo, curvas, trayectoria y criterio experto; envío jueves. **Ubicación:** 1.1. | Implementada |
| 3.04 | Reconocer componente empírico y complementar conocimiento experto | La propuesta es una sugerencia cuantitativa revisable; no reemplazo probado. **Ubicación:** 1.1; 4.6. | Implementada |
| 3.05 | Pregunta de negocio después del contexto y problema | Se formula tras explicar el flujo y su necesidad. **Ubicación:** 1.1. | Implementada |
| 3.06 | Convertir preguntas específicas en narrativa | Se reemplaza listado de preguntas por motivación conectada y objetivos explícitos. **Ubicación:** 1.1–1.2. | Implementada |
| 3.07 | Motivar curvas y contraste con SARIMA/SARIMAX reales | Se distingue piloto diario de modelos semanales para no inventar comparaciones. **Ubicación:** 1.1; 3.6. | Implementada |
| 3.08 | Revisar objetivo general y explicitar objetivos coherentes | Se precisa corte reportado y alcance exploratorio; se formulan cuatro objetivos y conclusiones correspondientes. **Ubicación:** 1.2; 5. | Implementada |
| 3.09 | Mencionar familias y propósito desde introducción | Referencias sencillas, corrección lineal/no lineal, perfiles, SARIMA/SARIMAX y recurrente. **Ubicación:** 1.1. | Implementada |
| 3.10 | Distinguir exportable, no exportable, objetivo y referente | Se separan clasificación comercial, corte registrado y formato exportable del referente. **Ubicación:** 1.2. | Implementada |
| 3.11 | No equiparar tallos reportados con exportable | Equivalencia explícitamente no confirmada; no se presenta certificación exportable. **Ubicación:** Resumen; 1.2; 4.6; 5. | Implementada |
| 3.12 | Mantener delimitación GAITANA / GAITANA PPTO | Etiquetas no acumuladas ni reasignadas; otras fincas fuera de la inferencia principal. **Ubicación:** 1.2. | Implementada |
| 3.13 | Aclarar disponibilidad/publicación y efectos retrospectivos | Se distingue fecha observada/versión archivada de publicación; se explicita asimetría jueves/lunes. **Ubicación:** 1.2; 3.5. | Implementada |

## 4. Contexto operativo y fuentes de información

| ID | Indicación | Cambio y ubicación | Estado |
| --- | --- | --- | --- |
| 4.01 | Títulos académicos y radiografía de datos | Capítulo 2 adopta el título propuesto; se evitan preguntas en encabezados. **Ubicación:** 2. | Implementada |
| 4.02 | Definir cama, piloto, ciclo, plano, cohorte, corte y rendimiento | Glosario breve previo a su uso técnico detallado. **Ubicación:** 2.1, tabla 1. | Implementada |
| 4.03 | Glosario breve sin duplicaciones extensas | Ocho términos con definición operativa; las decisiones quedan en método. **Ubicación:** 2.1. | Implementada |
| 4.04 | Explicar inventarios con ejemplo de cama en dos planos | Ejemplo de 1.000 plantas conservadas, no 2.000 siembras nuevas. **Ubicación:** 2.1. | Implementada |
| 4.05 | Dimensiones, periodos, variables y detalle verificados en fuentes | Cinco fuentes con filas, cantidad de columnas, contenido y rango; consulta al snapshot evaluado. **Ubicación:** 2.2, tabla 2; datos_verificados.json. | Implementada |
| 4.06 | Explicar integración y llaves | Se enumeran llaves por tipo de fuente, ciclo, serie, fecha y origen. **Ubicación:** 2.2. | Implementada |
| 4.07 | Eliminar Precaución principal y pasar cautelas al texto | Nueva tabla sin esa columna; precauciones integradas en prosa. **Ubicación:** 2.2. | Implementada |
| 4.08 | Identificar fuentes en vez de el archivo ambiguo | Se usa nombre de fuente/edición y su función; se retiran rutas internas académicas. **Ubicación:** 2.2; revisión global. | Implementada |
| 4.09 | Explicar curvas, traslado a otras camas y ejemplo sustentado | Ejemplo real Ard edad 50, 0,2542 tallos/planta y 43 observaciones; curva redibujada. **Ubicación:** 2.3; 3.3, figura 1. | Implementada |

## 5. Pretratamiento y análisis exploratorio

| ID | Indicación | Cambio y ubicación | Estado |
| --- | --- | --- | --- |
| 5.01 | Simplificar sustancialmente EDA a decisiones y resultados pertinentes | Se conserva composición, memoria, alcance de curva y contraste climático conectado con método. **Ubicación:** 4.1–4.2. | Implementada |
| 5.02 | Anexar complementos necesarios y eliminar redundancias | Un gráfico climático y comparaciones seleccionadas; se elimina repetición de rankings y extensos segmentos. **Ubicación:** Anexos B–C. | Implementada |
| 5.03 | Esquema con cantidades entrantes/utilizables/pendientes | Figura de pretratamiento reconstruida con 543.368, 523.336, 490.116 y controles. **Ubicación:** 3.2, figura 3. | Implementada |
| 5.04 | Distinguir universos y denominadores | Se separan historia de edición, cortes 2026, series–semana y casos origen–horizonte. **Ubicación:** 2.1–2.2; 3.2; 4.1. | Implementada |
| 5.05 | Interpretar Ambigua, Conflicto_ciclo, Llave_incompleta, Sin_pareja, Única | Tabla de estados, conteos y significado; texto explicativo. **Ubicación:** 3.2, tabla 3. | Implementada |
| 5.06 | Separar uniones correctas de representación de todas las edades | 99,84 % sobre cortes 2026 frente a 46.528/216.127 casos con referencia total. **Ubicación:** 4.1. | Implementada |
| 5.07 | Eliminar fechas internas irrelevantes como revisión 19 octubre | Se retiran fechas de revisiones editoriales; sólo quedan cortes de datos y evaluaciones relevantes. **Ubicación:** Revisión global. | Implementada |
| 5.08 | Distinguir edición 2026 de año de cortes | Se explica historia anterior repetida dentro de libros anuales. **Ubicación:** 2.2; tabla 3. | Implementada |
| 5.09 | Conectar ceros, edades sin observaciones y desconocidos | Se definen estados de evidencia y no se rellenan desconocidos con cero. **Ubicación:** 2.3. | Implementada |
| 5.10 | Integrar frase aislada de rendimiento cero | Se sustituye por párrafo conectado sobre registros válidos y ausencia de evidencia. **Ubicación:** 2.3. | Implementada |
| 5.11 | Mover decisión de curvas compartidas/GAITANA al método | Se explican atribución y sensibilidad sin asignar finca por descarte. **Ubicación:** 3.3. | Implementada |
| 5.12 | Mover concepto de aplicación por edad a fuentes/curvas | Alcance de referencia, cohortes y sumas parciales se introduce antes del método. **Ubicación:** 2.3. | Implementada |
| 5.13 | Adelantar esquema de teoría/ruta de producción reciente y simplificar | Figura metodológica temprana con dos referencias, grupos e inferencia; sin explicaciones inferiores duplicadas. **Ubicación:** 3.1, figura 2. | Implementada |
| 5.14 | Límite inferior 15 en figura de representación por edad | Figura redibujada desde panel actualizado, eje en porcentaje y advertencia de truncamiento. **Ubicación:** 4.1, figura 4; soporte_edades_por_horizonte.csv. | Implementada |
| 5.15 | Trasladar figura original 6b climática a anexos | Se conserva su análisis, redibujado desde asociaciones con etiquetas legibles, en anexo B. **Ubicación:** Anexo B, figura 6. | Implementada |
| 5.16 | Integrar frases y evitar repeticiones | Narrativa continua; eliminación de referencias a revisiones y recorridos de archivos. **Ubicación:** Todo el manuscrito. | Implementada |

## 6. Metodología

| ID | Indicación | Cambio y ubicación | Estado |
| --- | --- | --- | --- |
| 6.01 | Describir fases primero y desarrollar subsecciones | Cinco fases y diagrama antes de los detalles algorítmicos. **Ubicación:** 3.1–3.7. | Implementada |
| 6.02 | Explicar proceso completo antes de boosting | Referencias, integración y variables preceden a la explicación de corrección aprendida. **Ubicación:** 3.1–3.4. | Implementada |
| 6.03 | Diferenciar modelos, referencias, sensibilidades y pilotos | Inventario por papel; diarios separados de semanales. **Ubicación:** 3.4, tabla 5; 3.6. | Implementada |
| 6.04 | Incluir sólo métodos implementados | No se agregan modelos ni búsquedas; resultados conservan fuentes existentes. **Ubicación:** 3.4–3.6; verificacion_final.json. | Implementada |
| 6.05 | Introducir boosting antes de explicar decisiones/resultados | Fundamento, corrección y fórmula antes de variantes y selección. **Ubicación:** 3.4. | Implementada |
| 6.06 | Explicar alternativa sin confundir teoría y producción real | Media4 corregida mantiene casos admisibles; suma parcial no se usa como total. **Ubicación:** 3.1; 4.1. | Implementada |
| 6.07 | Diferenciar semanal, diario autónomo y reconciliado/evaluaciones | Tareas, entradas, origen y paneles explícitos; LSTM de un día aparte. **Ubicación:** 3.6; 4.5. | Implementada |
| 6.08 | Organizar por decisiones/fases, no por cuadernos | Se retiran números de notebooks y cronología de ejecución. **Ubicación:** Capítulos 3–4. | Implementada |
| 6.09 | Diagrama A como figura metodológica sin preguntas | Figura 2 con títulos descriptivos, algoritmo, entradas y grupos identificados. **Ubicación:** 3.1. | Implementada |
| 6.10 | Diagrama B diario como tabla | Tabla de procedimientos diarios sustituye el diagrama. **Ubicación:** 3.6, tabla 8. | Implementada |
| 6.11 | Diccionario y lectura consolidada en anexos | 47 columnas verificadas, ejemplo calendario y lectura de vacíos. **Ubicación:** Anexo A, tabla 19. | Implementada |
| 6.12 | Unificar hiperparámetros y su presentación | Tabla única incluye seleccionado, Ridge, horizontes, propios, pesos, diario y LSTM. **Ubicación:** 3.4, tabla 6. | Implementada |
| 6.13 | Explicar orden SARIMA/SARIMAX y periodo 7 | p,d,q,P,D,Q y periodicidad semanal explicados en su contexto diario. **Ubicación:** 3.6. | Implementada |
| 6.14 | Retirar sesgo elemental repetido y unificar signo | Convención pronóstico − real en método y notas de tablas. **Ubicación:** 3.5; resultados. | Implementada |
| 6.15 | Explicar periodos, selección y disponibilidad al emitir | Validación 2025, prueba ISO2026, mensual/congelado; lunes frente a jueves y publicación no acreditada. **Ubicación:** 3.5; tabla 7. | Implementada |

## 7. Resultados y discusión

| ID | Indicación | Cambio y ubicación | Estado |
| --- | --- | --- | --- |
| 7.01 | Integrar resultados y discusión | Capítulo único, interpretaciones junto a resultados. **Ubicación:** 4. | Implementada |
| 7.02 | Subsecciones correspondientes a fases metodológicas | Integración, EDA, métodos, extensión, diario e implicaciones. **Ubicación:** 4.1–4.6. | Implementada |
| 7.03 | Interpretación, negocio y límites junto a resultado | Cada comparación incorpora alcance y restricción, no sólo ranking. **Ubicación:** 4.1–4.6. | Implementada |
| 7.04 | Priorizar objetivos y aporte al procedimiento actual | Resultado central por horizonte y límites de uso empresarial. **Ubicación:** 4.3–4.6; 5. | Implementada |
| 7.05 | Reducir tablas repetidas y párrafos que recitan cifras | Una tabla por función; resultados históricos complementarios resumidos. **Ubicación:** 4; Anexo C. | Implementada |
| 7.06 | Complementos necesarios a anexos | Diccionario, análisis climático y contrastes seleccionados. **Ubicación:** Anexos A–C. | Implementada |
| 7.07 | Conservar diferencias relevantes de H/producto/método | Tabla anual, extensión, productos y tareas diarias distintas. **Ubicación:** 4.3–4.5. | Implementada |
| 7.08 | No generalizar mejoras parciales | H1/H2 favorables; H3–H5 y extensión global favorables al referente. **Ubicación:** Resumen; 4.3–4.4; 5. | Implementada |
| 7.09 | Carácter retrospectivo/exploratorio explícito | Disponibilidad histórica, revisión previa de periodos y pilotos diarios delimitados. **Ubicación:** 1.2; 3.5; 4.5. | Implementada |
| 7.10 | No afirmar causalidad, validación empresarial o beneficios no probados | Asociaciones no causales; prototipo no equivale a adopción ni ahorro. **Ubicación:** 4.2; 4.6. | Implementada |
| 7.11 | Conclusiones por objetivos sin repetir toda discusión | Cinco conclusiones compactas alineadas con formulación revisada. **Ubicación:** 5. | Implementada |

## 8. Redacción, tablas, figuras y referencias

| ID | Indicación | Cambio y ubicación | Estado |
| --- | --- | --- | --- |
| 8.01 | Redacción académica natural y conectada | Reescritura integral centrada en decisiones y evidencia. **Ubicación:** Todo el documento. | Implementada |
| 8.02 | Eliminar títulos pregunta, De X a Y y Del hallazgo a decisión | Encabezados descriptivos verificados por script. **Ubicación:** Índice y secciones. | Implementada |
| 8.03 | Eliminar fórmulas grandilocuentes y resúmenes mecánicos | Se reemplazan por conclusiones acotadas y límites concretos. **Ubicación:** Resumen; resultados; conclusiones. | Implementada |
| 8.04 | Evitar recitar cuadros o explicar distribución editorial | Texto orientado a método e implicación; sin guía extensa de dónde se movió cada fragmento. **Ubicación:** Capítulos 3–4. | Implementada |
| 8.05 | Numerar/titular todas las tablas y figuras | 20 tablas y 6 figuras con captions y marcadores. **Ubicación:** objetos_y_referencias.json; Word. | Implementada |
| 8.06 | Referencias cruzadas reproducibles en Word | 22 campos REF enlazados a marcadores; TOC actualizado al exportar. **Ubicación:** Word; verificacion_word.json. | Implementada |
| 8.07 | Actualizar numeración, menciones e índices | Numeración automática desde orden de objetos; referencias regeneradas y comprobadas. **Ubicación:** Word/PDF; índice. | Implementada |
| 8.08 | Retirar E1/E3/Fuente E15/cuadernos 10–25 | No quedan códigos de evidencia ni secuencias de notebooks en el texto académico. **Ubicación:** Verificación de texto. | Implementada |
| 8.09 | Describir procedimientos sin orden interno de notebooks | Modelos nombrados por función, familia y entradas. **Ubicación:** 3.4–3.6. | Implementada |
| 8.10 | Retirar Referencias de evidencia y pendientes editoriales | Trazabilidad y pendientes se trasladan exclusivamente a archivos separados. **Ubicación:** REGISTRO_CUMPLIMIENTO; PENDIENTES_EQUIPO. | Implementada |
| 8.11 | Referencias académicas reales en IEEE | Seis referencias verificadas, numeradas según primera aparición; se preservan fuentes reales previas. **Ubicación:** Referencias; 3.4–3.7. | Implementada |
| 8.12 | Eliminar saltos innecesarios, incluido antes del EDA | Sin saltos forzados entre capítulos; sólo separaciones de portada e índice. **Ubicación:** Generador Word; revisión PDF. | Implementada |

## 9. Extensión y comprobación final

| ID | Indicación | Cambio y ubicación | Estado |
| --- | --- | --- | --- |
| 9.01 | Máximo 50 páginas incluyendo todo | PDF renderizado con Word y conteo independiente; número final en verificacion_final.json. **Ubicación:** Word/PDF completos. | Implementada |
| 9.02 | Sintetizar manteniendo formato y legibilidad | Times New Roman 12, interlineado 1,5 y márgenes 2,54 cm; tablas 9–10 pt, no compresión del cuerpo. **Ubicación:** verificacion_word.json. | Implementada |
| 9.03 | No volcar todo lo retirado en anexos | Selección de tres anexos; no se incluye la totalidad del material retirado. **Ubicación:** Anexos A–C. | Implementada |
| 9.04 | Verificar cifras con datos y código | Recuentos recalculados y métricas contrastadas con predicciones; no se entrenan modelos. **Ubicación:** evidencia_revision_v9.py; verificar_revision_v9.py. | Implementada |
| 9.05 | Consistencia de resumen, objetivos, método y conclusiones | Mismo seleccionado y panel ampliado; comparación reciente separada. **Ubicación:** Resumen; 1.2; 3.4–3.5; 4–5. | Implementada |
| 9.06 | Regenerar figuras modificadas desde fuentes | Las seis figuras se reconstruyen desde datos o lógica implementada, sin editar píxeles. **Ubicación:** Revision_v9/Figuras; evidencia_revision_v9.py. | Implementada |
| 9.07 | Conservar resultados válidos y justificar cambios | Modelo y predicciones intactos; se actualizan sólo dimensiones/gráficos descriptivos con la misma extracción de la evaluación. **Ubicación:** NOTAS_DE_CAMBIOS.md; fuentes_sha256.json. | Implementada |
| 9.08 | No inventar contexto, cifras ni metodologías | Datos internos verificables y referencias primarias; limitaciones expresas. **Ubicación:** Verificaciones y pendientes externos. | Implementada |
| 9.09 | Renderizar PDF y revisar tablas, figuras, referencias y saltos | Render Word, conteo PDF, controles de desbordamiento y mosaicos de todas las páginas. **Ubicación:** Comprobacion_visual; verificacion_final.json. | Implementada |

## 10. Entrega

| ID | Indicación | Cambio y ubicación | Estado |
| --- | --- | --- | --- |
| 10.01 | Word corregido | Documento nuevo final, sin sobrescribir v8. **Ubicación:** Word final. | Implementada |
| 10.02 | Registro separado de cumplimiento | Registro con indicación, cambio, ubicación y estado; disponible en MD, CSV y JSON. **Ubicación:** REGISTRO_CUMPLIMIENTO. | Implementada |
| 10.03 | Revisar cada indicación antes de terminar | Matriz y verificaciones finales cruzadas con documento renderizado. **Ubicación:** Este registro; verificacion_final.json. | Implementada |
| 10.04 | Informar ubicación, páginas y pendientes concretos | README de entrega y pendientes separados; resumen al usuario. **Ubicación:** LEEME; PENDIENTES_EQUIPO.md. | Implementada |

