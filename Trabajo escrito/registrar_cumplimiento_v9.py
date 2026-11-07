"""Registro externo de las indicaciones consolidadas; no se inserta en la tesis."""
from pathlib import Path
import sys,json,csv,hashlib
from revision_v9_config import NAME
sys.stdout.reconfigure(encoding='utf8')
F=Path(__file__).resolve().parent;O=F/'Revision_v9'
# Los IDs corresponden a apartados/viñetas del prompt, no a números inventados de comentarios Word.
groups={
'1. Forma de trabajo':[
('Identificar versión vigente y generadores','V8 identificada como base; se conservan fuentes y documentos. V9 se compone con plantilla, evidencia y renderizador propios.','Fuentes y README de reproducción'),
('Modificar fuentes y regenerar de manera reproducible','Prosa editable, tablas desde resultados, figuras desde Parquet y Word con campos REF/TOC.','contenido_academico.md; scripts v9'),
('Conservar copia inicial y avances válidos','Copia de MD/Word/PDF v8 y huellas; originales comprobados sin cambios.','Version_inicial; version_inicial_sha256.json'),
('Registro separado por indicación, cambio, ubicación y estado','Este registro incluye cada indicación consolidada, con IDs propios del prompt.','REGISTRO_CUMPLIMIENTO.md/.csv/.json'),
('Resolver edición y explicitar faltantes sin inventar','Se delimita alcance y se documentan faltantes concretos fuera del manuscrito.','1.2; 3.5–3.7; 4.6; PENDIENTES_EQUIPO.md')],
'2. Portada, resumen y palabras clave':[
('Cambiar título solicitado','Se aplica literalmente el título indicado en portada y propiedades del Word.','Portada'),
('Incluir asesor y conservar autores','Rafael Amaya Gomez; Elián Durán, Julián Osorio y Anderson Gonzalez.','Portada'),
('Reescribir resumen con contexto, problema, método, resultados y aporte','Resumen nuevo, centrado en el apoyo al estimado y con resultados acotados.','Resumen'),
('Explicar productos, tallos y corte antes de cifras','Se presentan flores de corte, unidad reportada y actividad de cosecha.','Resumen; 1.1'),
('Evitar siglas indefinidas y definir horizontes reales','Resumen usa primera semana; H1–H5 se definen con calendario y edición 18–22.','Resumen; 1.1–1.2'),
('Presentar propósito analítico sin centrar resumen en Gradient Boosting','Se explica integración, corrección y utilidad; el algoritmo se desarrolla después.','Resumen; 3.4'),
('Identificar función del profesional de referencia','Se define responsable de producción y se usa esa denominación consistentemente.','1.1; tablas de resultados'),
('Ajustar palabras clave a curvas y métodos reales','Curvas empíricas de rendimiento, boosting, SARIMA/SARIMAX y reconciliación; se retiran calidad y validación temporal.','Palabras clave')],
'3. Introducción, problema, objetivos y alcance':[
('Comenzar explicando empresa, productos y proceso verificable','Contexto basado en categorías de las fuentes y flujo del proyecto; no se inventan ubicación, área o historia empresarial.','1.1'),
('Ampliar contexto para lector no experto','Se conecta cultivo, inventario, corte y decisiones de disponibilidad.','1.1; 2.1'),
('Explicar pronóstico actual, responsable, información y decisiones','Se describe revisión de cultivo, curvas, trayectoria y criterio experto; envío jueves.','1.1'),
('Reconocer componente empírico y complementar conocimiento experto','La propuesta es una sugerencia cuantitativa revisable; no reemplazo probado.','1.1; 4.6'),
('Pregunta de negocio después del contexto y problema','Se formula tras explicar el flujo y su necesidad.','1.1'),
('Convertir preguntas específicas en narrativa','Se reemplaza listado de preguntas por motivación conectada y objetivos explícitos.','1.1–1.2'),
('Motivar curvas y contraste con SARIMA/SARIMAX reales','Se distingue piloto diario de modelos semanales para no inventar comparaciones.','1.1; 3.6'),
('Revisar objetivo general y explicitar objetivos coherentes','Se precisa corte reportado y alcance exploratorio; se formulan cuatro objetivos y conclusiones correspondientes.','1.2; 5'),
('Mencionar familias y propósito desde introducción','Referencias sencillas, corrección lineal/no lineal, perfiles, SARIMA/SARIMAX y recurrente.','1.1'),
('Distinguir exportable, no exportable, objetivo y referente','Se separan clasificación comercial, corte registrado y formato exportable del referente.','1.2'),
('No equiparar tallos reportados con exportable','Equivalencia explícitamente no confirmada; no se presenta certificación exportable.','Resumen; 1.2; 4.6; 5'),
('Mantener delimitación GAITANA / GAITANA PPTO','Etiquetas no acumuladas ni reasignadas; otras fincas fuera de la inferencia principal.','1.2'),
('Aclarar disponibilidad/publicación y efectos retrospectivos','Se distingue fecha observada/versión archivada de publicación; se explicita asimetría jueves/lunes.','1.2; 3.5')],
'4. Contexto operativo y fuentes de información':[
('Títulos académicos y radiografía de datos','Capítulo 2 adopta el título propuesto; se evitan preguntas en encabezados.','2'),
('Definir cama, piloto, ciclo, plano, cohorte, corte y rendimiento','Glosario breve previo a su uso técnico detallado.','2.1, tabla 1'),
('Glosario breve sin duplicaciones extensas','Ocho términos con definición operativa; las decisiones quedan en método.','2.1'),
('Explicar inventarios con ejemplo de cama en dos planos','Ejemplo de 1.000 plantas conservadas, no 2.000 siembras nuevas.','2.1'),
('Dimensiones, periodos, variables y detalle verificados en fuentes','Cinco fuentes con filas, cantidad de columnas, contenido y rango; consulta al snapshot evaluado.','2.2, tabla 2; datos_verificados.json'),
('Explicar integración y llaves','Se enumeran llaves por tipo de fuente, ciclo, serie, fecha y origen.','2.2'),
('Eliminar Precaución principal y pasar cautelas al texto','Nueva tabla sin esa columna; precauciones integradas en prosa.','2.2'),
('Identificar fuentes en vez de el archivo ambiguo','Se usa nombre de fuente/edición y su función; se retiran rutas internas académicas.','2.2; revisión global'),
('Explicar curvas, traslado a otras camas y ejemplo sustentado','Ejemplo real Ard edad 50, 0,2542 tallos/planta y 43 observaciones; curva redibujada.','2.3; 3.3, figura 1')],
'5. Pretratamiento y análisis exploratorio':[
('Simplificar sustancialmente EDA a decisiones y resultados pertinentes','Se conserva composición, memoria, alcance de curva y contraste climático conectado con método.','4.1–4.2'),
('Anexar complementos necesarios y eliminar redundancias','Un gráfico climático y comparaciones seleccionadas; se elimina repetición de rankings y extensos segmentos.','Anexos B–C'),
('Esquema con cantidades entrantes/utilizables/pendientes','Figura de pretratamiento reconstruida con 543.368, 523.336, 490.116 y controles.','3.2, figura 3'),
('Distinguir universos y denominadores','Se separan historia de edición, cortes 2026, series–semana y casos origen–horizonte.','2.1–2.2; 3.2; 4.1'),
('Interpretar Ambigua, Conflicto_ciclo, Llave_incompleta, Sin_pareja, Única','Tabla de estados, conteos y significado; texto explicativo.','3.2, tabla 3'),
('Separar uniones correctas de representación de todas las edades','99,84 % sobre cortes 2026 frente a 46.528/216.127 casos con referencia total.','4.1'),
('Eliminar fechas internas irrelevantes como revisión 19 octubre','Se retiran fechas de revisiones editoriales; sólo quedan cortes de datos y evaluaciones relevantes.','Revisión global'),
('Distinguir edición 2026 de año de cortes','Se explica historia anterior repetida dentro de libros anuales.','2.2; tabla 3'),
('Conectar ceros, edades sin observaciones y desconocidos','Se definen estados de evidencia y no se rellenan desconocidos con cero.','2.3'),
('Integrar frase aislada de rendimiento cero','Se sustituye por párrafo conectado sobre registros válidos y ausencia de evidencia.','2.3'),
('Mover decisión de curvas compartidas/GAITANA al método','Se explican atribución y sensibilidad sin asignar finca por descarte.','3.3'),
('Mover concepto de aplicación por edad a fuentes/curvas','Alcance de referencia, cohortes y sumas parciales se introduce antes del método.','2.3'),
('Adelantar esquema de teoría/ruta de producción reciente y simplificar','Figura metodológica temprana con dos referencias, grupos e inferencia; sin explicaciones inferiores duplicadas.','3.1, figura 2'),
('Límite inferior 15 en figura de representación por edad','Figura redibujada desde panel actualizado, eje en porcentaje y advertencia de truncamiento.','4.1, figura 4; soporte_edades_por_horizonte.csv'),
('Trasladar figura original 6b climática a anexos','Se conserva su análisis, redibujado desde asociaciones con etiquetas legibles, en anexo B.','Anexo B, figura 6'),
('Integrar frases y evitar repeticiones','Narrativa continua; eliminación de referencias a revisiones y recorridos de archivos.','Todo el manuscrito')],
'6. Metodología':[
('Describir fases primero y desarrollar subsecciones','Cinco fases y diagrama antes de los detalles algorítmicos.','3.1–3.7'),
('Explicar proceso completo antes de boosting','Referencias, integración y variables preceden a la explicación de corrección aprendida.','3.1–3.4'),
('Diferenciar modelos, referencias, sensibilidades y pilotos','Inventario por papel; diarios separados de semanales.','3.4, tabla 5; 3.6'),
('Incluir sólo métodos implementados','No se agregan modelos ni búsquedas; resultados conservan fuentes existentes.','3.4–3.6; verificacion_final.json'),
('Introducir boosting antes de explicar decisiones/resultados','Fundamento, corrección y fórmula antes de variantes y selección.','3.4'),
('Explicar alternativa sin confundir teoría y producción real','Media4 corregida mantiene casos admisibles; suma parcial no se usa como total.','3.1; 4.1'),
('Diferenciar semanal, diario autónomo y reconciliado/evaluaciones','Tareas, entradas, origen y paneles explícitos; LSTM de un día aparte.','3.6; 4.5'),
('Organizar por decisiones/fases, no por cuadernos','Se retiran números de notebooks y cronología de ejecución.','Capítulos 3–4'),
('Diagrama A como figura metodológica sin preguntas','Figura 2 con títulos descriptivos, algoritmo, entradas y grupos identificados.','3.1'),
('Diagrama B diario como tabla','Tabla de procedimientos diarios sustituye el diagrama.','3.6, tabla 8'),
('Diccionario y lectura consolidada en anexos','47 columnas verificadas, ejemplo calendario y lectura de vacíos.','Anexo A, tabla 19'),
('Unificar hiperparámetros y su presentación','Tabla única incluye seleccionado, Ridge, horizontes, propios, pesos, diario y LSTM.','3.4, tabla 6'),
('Explicar orden SARIMA/SARIMAX y periodo 7','p,d,q,P,D,Q y periodicidad semanal explicados en su contexto diario.','3.6'),
('Retirar sesgo elemental repetido y unificar signo','Convención pronóstico − real en método y notas de tablas.','3.5; resultados'),
('Explicar periodos, selección y disponibilidad al emitir','Validación 2025, prueba ISO2026, mensual/congelado; lunes frente a jueves y publicación no acreditada.','3.5; tabla 7')],
'7. Resultados y discusión':[
('Integrar resultados y discusión','Capítulo único, interpretaciones junto a resultados.','4'),
('Subsecciones correspondientes a fases metodológicas','Integración, EDA, métodos, extensión, diario e implicaciones.','4.1–4.6'),
('Interpretación, negocio y límites junto a resultado','Cada comparación incorpora alcance y restricción, no sólo ranking.','4.1–4.6'),
('Priorizar objetivos y aporte al procedimiento actual','Resultado central por horizonte y límites de uso empresarial.','4.3–4.6; 5'),
('Reducir tablas repetidas y párrafos que recitan cifras','Una tabla por función; resultados históricos complementarios resumidos.','4; Anexo C'),
('Complementos necesarios a anexos','Diccionario, análisis climático y contrastes seleccionados.','Anexos A–C'),
('Conservar diferencias relevantes de H/producto/método','Tabla anual, extensión, productos y tareas diarias distintas.','4.3–4.5'),
('No generalizar mejoras parciales','H1/H2 favorables; H3–H5 y extensión global favorables al referente.','Resumen; 4.3–4.4; 5'),
('Carácter retrospectivo/exploratorio explícito','Disponibilidad histórica, revisión previa de periodos y pilotos diarios delimitados.','1.2; 3.5; 4.5'),
('No afirmar causalidad, validación empresarial o beneficios no probados','Asociaciones no causales; prototipo no equivale a adopción ni ahorro.','4.2; 4.6'),
('Conclusiones por objetivos sin repetir toda discusión','Cinco conclusiones compactas alineadas con formulación revisada.','5')],
'8. Redacción, tablas, figuras y referencias':[
('Redacción académica natural y conectada','Reescritura integral centrada en decisiones y evidencia.','Todo el documento'),
('Eliminar títulos pregunta, De X a Y y Del hallazgo a decisión','Encabezados descriptivos verificados por script.','Índice y secciones'),
('Eliminar fórmulas grandilocuentes y resúmenes mecánicos','Se reemplazan por conclusiones acotadas y límites concretos.','Resumen; resultados; conclusiones'),
('Evitar recitar cuadros o explicar distribución editorial','Texto orientado a método e implicación; sin guía extensa de dónde se movió cada fragmento.','Capítulos 3–4'),
('Numerar/titular todas las tablas y figuras','20 tablas y 6 figuras con captions y marcadores.','objetos_y_referencias.json; Word'),
('Referencias cruzadas reproducibles en Word','22 campos REF enlazados a marcadores; TOC actualizado al exportar.','Word; verificacion_word.json'),
('Actualizar numeración, menciones e índices','Numeración automática desde orden de objetos; referencias regeneradas y comprobadas.','Word/PDF; índice'),
('Retirar E1/E3/Fuente E15/cuadernos 10–25','No quedan códigos de evidencia ni secuencias de notebooks en el texto académico.','Verificación de texto'),
('Describir procedimientos sin orden interno de notebooks','Modelos nombrados por función, familia y entradas.','3.4–3.6'),
('Retirar Referencias de evidencia y pendientes editoriales','Trazabilidad y pendientes se trasladan exclusivamente a archivos separados.','REGISTRO_CUMPLIMIENTO; PENDIENTES_EQUIPO'),
('Referencias académicas reales en IEEE','Seis referencias verificadas, numeradas según primera aparición; se preservan fuentes reales previas.','Referencias; 3.4–3.7'),
('Eliminar saltos innecesarios, incluido antes del EDA','Sin saltos forzados entre capítulos; sólo separaciones de portada e índice.','Generador Word; revisión PDF')],
'9. Extensión y comprobación final':[
('Máximo 50 páginas incluyendo todo','PDF renderizado con Word y conteo independiente; número final en verificacion_final.json.','Word/PDF completos'),
('Sintetizar manteniendo formato y legibilidad','Times New Roman 12, interlineado 1,5 y márgenes 2,54 cm; tablas 9–10 pt, no compresión del cuerpo.','verificacion_word.json'),
('No volcar todo lo retirado en anexos','Selección de tres anexos; no se incluye la totalidad del material retirado.','Anexos A–C'),
('Verificar cifras con datos y código','Recuentos recalculados y métricas contrastadas con predicciones; no se entrenan modelos.','evidencia_revision_v9.py; verificar_revision_v9.py'),
('Consistencia de resumen, objetivos, método y conclusiones','Mismo seleccionado y panel ampliado; comparación reciente separada.','Resumen; 1.2; 3.4–3.5; 4–5'),
('Regenerar figuras modificadas desde fuentes','Las seis figuras se reconstruyen desde datos o lógica implementada, sin editar píxeles.','Revision_v9/Figuras; evidencia_revision_v9.py'),
('Conservar resultados válidos y justificar cambios','Modelo y predicciones intactos; se actualizan sólo dimensiones/gráficos descriptivos con la misma extracción de la evaluación.','NOTAS_DE_CAMBIOS.md; fuentes_sha256.json'),
('No inventar contexto, cifras ni metodologías','Datos internos verificables y referencias primarias; limitaciones expresas.','Verificaciones y pendientes externos'),
('Renderizar PDF y revisar tablas, figuras, referencias y saltos','Render Word, conteo PDF, controles de desbordamiento y mosaicos de todas las páginas.','Comprobacion_visual; verificacion_final.json')],
'10. Entrega':[
('Word corregido','Documento nuevo final, sin sobrescribir v8.','Word final'),
('Registro separado de cumplimiento','Registro con indicación, cambio, ubicación y estado; disponible en MD, CSV y JSON.','REGISTRO_CUMPLIMIENTO'),
('Revisar cada indicación antes de terminar','Matriz y verificaciones finales cruzadas con documento renderizado.','Este registro; verificacion_final.json'),
('Informar ubicación, páginas y pendientes concretos','README de entrega y pendientes separados; resumen al usuario.','LEEME; PENDIENTES_EQUIPO.md')]
}
rows=[]
for group,items in groups.items():
    section=group.split('.')[0]
    for i,(instruction,change,location) in enumerate(items,1):
        rows.append({'id':f'{section}.{i:02d}','apartado_prompt':group,'indicacion':instruction,'cambio_realizado':change,'ubicacion':location,'estado':'Implementada','verificacion':'Documento y fuentes; verificacion_final.json'})
verification=json.loads((O/'verificacion_final.json').read_text(encoding='utf8')) if (O/'verificacion_final.json').exists() else {}
pages=verification.get('paginas_pdf','en comprobación')
header=f'''# Registro de cumplimiento — revisión del asesor

Documento: `{NAME}.docx`, con PDF de comprobación. **Páginas verificadas: {pages}.**

Esta matriz responde a las indicaciones consolidadas del prompt del 04/11/2026. Sus IDs identifican apartados y viñetas del prompt, no pretenden reconstruir la numeración de los 60 comentarios originales. Las restricciones empíricas se incorporaron al texto; «implementada» no significa que se haya confirmado una equivalencia comercial o realizado un piloto aún pendiente. Esos faltantes concretos están en `PENDIENTES_EQUIPO.md`.

Se conservaron la configuración y las predicciones de los modelos. La revisión es editorial y de consistencia de evidencia, no una nueva selección estadística.

'''
for group in groups:
    header+='## '+group+'\n\n| ID | Indicación | Cambio y ubicación | Estado |\n| --- | --- | --- | --- |\n'
    for r in rows:
        if r['apartado_prompt']==group:header+=f"| {r['id']} | {r['indicacion']} | {r['cambio_realizado']} **Ubicación:** {r['ubicacion']}. | {r['estado']} |\n"
    header+='\n'
(O/'REGISTRO_CUMPLIMIENTO.md').write_text(header,encoding='utf8')
(O/'REGISTRO_CUMPLIMIENTO.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
with (O/'REGISTRO_CUMPLIMIENTO.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
pending='''# Información y decisiones pendientes del equipo

Las correcciones editoriales están implementadas. Los siguientes puntos limitan las afirmaciones empíricas y permanecen explícitos en el manuscrito; no impiden entregar la revisión.

| ID | Información o decisión concreta | Efecto y ubicación en la tesis |
| --- | --- | --- |
| P1 | Confirmar con producción/poscosecha qué categorías de corte reportado corresponden a exportable y no exportable, y conciliarlas con ESTI. EXPORTABLE del referente. | No afirmar equivalencia comercial ni un pronóstico certificado de exportable. Secciones 1.2 y 4.6. |
| P2 | Conservar fechas de publicación/corrección por fuente y reconstruir ambos pronósticos con un corte común al jueves de emisión. | La comparación actual es retrospectiva; el modelo usa pasado anterior al lunes y no tiene acreditada la misma información del referente. Sección 3.5. |
| P3 | Validación agronómica de edades improductivas, puntos tardíos, ventana de 78 semanas, ponderación por plantas y transferencia de pilotos compartidos. | No convertir edades desconocidas en cero ni presentar la curva como ley universal. Secciones 2.3 y 3.3. |
| P4 | Realizar un piloto prospectivo: congelar versión, registrar emisiones anticipadas, acuerdos de decisión y resultados de servicio/costos. Definir umbrales de faltante/normalidad/sobrante con acciones y responsables. | No afirmar adopción, impacto económico ni superioridad futura demostrada. Secciones 3.7 y 4.6. |
| P5 | En el piloto LSTM, auditar selección de series sólo con pasado; archivar predicciones train/validación en tallos; comparar siete días desde un origen común y reconciliar si corresponde. | Su ensayo actual es de un día adelante; no certifica el reparto semanal. Secciones 3.6 y 4.5. |
| P6 | Archivar las predicciones individuales faltantes de entrenamiento/validación de los experimentos recientes antes de extraer conclusiones de sobreajuste. | No reconstruir MAPE/±8 % desde MAE ni trasladar métricas de test a train. Anexo C. |
| P7 | Ratificar la formulación de objetivos revisada con el equipo: el alcance comprobado se expresa en corte reportado y evaluación retrospectiva, no en exportable certificado e impacto empresarial ya validado. | Cambio editorial autorizado por el prompt, documentado frente al anteproyecto. Sección 1.2 y conclusiones. |

No se solicita el Word comentado ni el correo del director. No se requieren para reproducir estas correcciones.
'''
(O/'PENDIENTES_EQUIPO.md').write_text(pending,encoding='utf8')
changes='''# Decisiones y cambios de evidencia de la revisión v9

- Base preservada: versión 8, 84 páginas. Copia inicial y SHA-256 en `Version_inicial` y `version_inicial_sha256.json`.
- No se reentrenó ni se afinó ningún modelo. Se conservaron las predicciones y la elección previa; el WAPE ampliado sigue siendo 19,27 % frente a 19,40 %, con ventaja en H1/H2 y sin superioridad general.
- Se eliminaron dimensiones históricas mezcladas con la extracción ampliada. La auditoría piloto actual contiene 543.368 filas, 523.336 con pareja única y 490.116 utilizables. Los conteos anteriores de 530.250/510.237/477.426 correspondían a la extracción previa, no a errores nuevos ni a una modificación del algoritmo. Entre cortes fechados en 2026: 46.085/46.157 parejas únicas (99,84 %).
- Se documenta el panel de la misma extracción de la evaluación: 648.030 casos, 216.127 con real y 148.435 con real/historia admisible. Los 46.528 casos con todas las edades representadas no son plantas, tallos ni uniones fallidas. La figura de edades se redibuja con eje inferior 15 %.
- Curva ilustrativa reconstruida al último plano de esa extracción (12/10/2026). Clima exploratorio conservado en su panel previo a julio de 2025 y redibujado para legibilidad, sin recalcular un resultado predictivo.
- Objetivos reformulados con el alcance efectivo, sin alterar el anteproyecto original. Se mantiene en el manuscrito la aspiración comercial y su equivalencia pendiente.
- Se sintetiza el EDA, se integran resultados/discusión y se separan los tres problemas diarios. Se elimina la tabla de evidencia interna del documento académico y se conserva su trazabilidad aquí.
- Hiperparámetros unificados, incluyendo pesos propios/general y diferencias de muestreo/variables de los experimentos recientes. No se atribuyen diferencias sólo a separar horizontes.
- Bibliografía en IEEE: se preservan las fuentes reales de evaluación temporal, fuga y operación; se verifican publicaciones originales de boosting y LSTM. Las referencias de código internas no se hacen pasar por bibliografía académica.
'''
(O/'NOTAS_DE_CAMBIOS.md').write_text(changes,encoding='utf8')
print(json.dumps({'indicaciones_registradas':len(rows),'paginas_verificadas':pages,'pendientes_equipo':7},ensure_ascii=False))
