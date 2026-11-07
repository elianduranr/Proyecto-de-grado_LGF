"""Nueva edición basada en v7 y en los resultados ejecutados del cuaderno 26."""
from pathlib import Path
import json
import re as regex
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'Trabajo escrito'
OUT=ROOT/'Datos_analiticos_proyecto/validacion_temporal_20261028'
NAME='Documento_LaGaitana_v8_validacion_temporal_actualizada_20261028'
REV=FOLDER/'Revision_v8';REV.mkdir(exist_ok=True)

def number(x,d=2):
    if pd.isna(x):return '—'
    return f'{x:,.{d}f}'.replace(',','X').replace('.',',').replace('X','.')

def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |',
        *['| '+' | '.join(str(v) for v in row)+' |' for row in rows]])

def main():
    summary=json.loads((OUT/'resumen_ejecucion.json').read_text(encoding='utf-8'))
    checks=json.loads((OUT/'verificacion_final.json').read_text(encoding='utf-8'));assert checks['passed']
    metrics=pd.read_csv(OUT/'metricas_comparadas.csv',dtype={'horizonte':str})
    recent=metrics.loc[metrics.periodo.eq('extension_desde_S37')&metrics.comparacion.eq('19_mensual_sin_clima')]
    rm=recent.loc[recent.metodo.eq('19_mensual_sin_clima')&recent.horizonte.eq('Total')].iloc[0]
    re=recent.loc[recent.metodo.eq('Ingeniero')&recent.horizonte.eq('Total')].iloc[0]
    sources=pd.read_csv(OUT/'fuentes_validadas.csv');splits=pd.read_csv(OUT/'particiones_por_corte.csv')
    annual=pd.read_csv(OUT/'metricas_2026_completo.csv',dtype={'horizonte':str})
    annual_model=annual.loc[annual.metodo.eq('19_mensual_sin_clima')&annual.horizonte.eq('Total')].iloc[0]
    annual_engineer=annual.loc[annual.metodo.eq('Ingeniero')&annual.horizonte.eq('Total')].iloc[0]
    annual_rows=[]
    for h in ['1','2','3','4','5','Total']:
        m=annual.loc[annual.metodo.eq('19_mensual_sin_clima')&annual.horizonte.eq(h)].iloc[0]
        e=annual.loc[annual.metodo.eq('Ingeniero')&annual.horizonte.eq(h)].iloc[0]
        annual_rows.append(['H'+h if h!='Total' else 'H1–H5',number(m.casos,0),number(m.WAPE)+' / '+number(e.WAPE),number(m.sesgo_pct)+' / '+number(e.sesgo_pct)])
    annual_table=table(['Horizonte','Casos comunes','WAPE (%) modelo / ingeniero','Sesgo (%) modelo / ingeniero'],annual_rows)
    audit=pd.read_csv(OUT/'auditoria_semanas.csv')
    text=(FOLDER/'Documento_LaGaitana_v7_revision_profesor_20261028.md').read_text(encoding='utf-8')
    text=text.replace('Esta edición reorganiza el argumento y completa indicadores a partir de predicciones archivadas; no reentrena modelos. Distingue los paneles históricos, el benchmark anual nominal actualizado y los ensayos recientes. Las nuevas cargas del prototipo no se presentan como una nueva validación de la tesis.',
        'Esta edición conserva los resultados históricos y añade una reconstrucción validada de fuentes y una evaluación temporal ampliada del modelo 19, sin cambiar sus parámetros. Se reentrena por corte y se contrasta esa actualización con un ajuste congelado. La nueva evaluación es retrospectiva; no se presenta una simulación como publicación anticipada. La consulta de WebFlor, la reconstrucción local, la persistencia SQL y la evaluación se ejecutan como procesos separados y trazables.')
    text=text.replace('Versión 7','Versión 8')
    summary_extra=(f' La comprobación local del cuaderno 26 amplía la evaluación a {summary["semanas_objetivo"]} semanas objetivo distintas, '
        f'hasta {summary["objetivo_hasta"]}. El balance 2026 reconstruido obtiene WAPE {number(annual_model.WAPE)} % para el modelo y {number(annual_engineer.WAPE)} % para el ingeniero sobre {number(annual_model.casos,0)} casos comunes. En el panel posterior a S36, el modelo mensual registra WAPE {number(rm.WAPE)} % '
        f'y sesgo {number(rm.sesgo_pct)} %, frente a {number(re.WAPE)} % y {number(re.sesgo_pct)} % del ingeniero, '
        f'sobre {number(rm.casos,0)} casos nominales comunes. Es evidencia retrospectiva adicional, con límites de disponibilidad histórica y de igualdad del corte de emisión.')
    text=text.replace('Palabras clave:',summary_extra+'\n\nPalabras clave:',1)
    methodology='''

### 4.2.8. Actualización temporal, train/validación/test y entrenamiento en operación

El cuaderno 26 comprueba la configuración elegida con una versión local de los datos más reciente. No se vuelve a elegir el ganador ni se ajustan hiperparámetros con sus nuevos errores. Las entradas del ingeniero siguen fuera de los predictores. Las fuentes, su hash, fechas, reglas de sustitución del corte y el código se conservan en un manifiesto local; no se requiere conexión a la empresa para reproducir esta corrida.

**Qué significa cada partición.** Train es el pasado disponible de cada ajuste; los objetivos deben terminar antes del corte. Validación es el período temporal previo utilizado para escoger la variante, noviembre–diciembre de 2025, con objetivos cerrados antes de 2026. La referencia de prueba de 2026 se conserva y la extensión incorpora semanas objetivo posteriores a S36. Como esos períodos se han revisado durante desarrollo, se denominan evaluaciones retrospectivas; una validación prospectiva exige guardar primero el pronóstico y observar después la producción. No se sustituyen estas funciones por una división aleatoria de registros relacionados.

La evaluación con origen móvil imita decisiones sucesivas: se pronostica el futuro desde cada corte y sólo después los resultados conocidos pueden incorporarse a ajustes posteriores. Es una alternativa al reparto fijo que conserva el orden temporal y permite medir varios horizontes (Hyndman y Athanasopoulos, 2021, sección 5.10). Una semana puede ser test de un ajuste y train de otro posterior; nunca debe ser ambas para la misma predicción. [N1]

Para una comprobación complementaria se conserva un ajuste congelado al 03/08/2026 y se evalúa el mismo panel de semanas objetivo desde S37. Ese ajuste no incorpora los objetivos de la extensión. El modelo mensual sí puede incorporar resultados anteriores que ya cerraron, reproduciendo el protocolo del 19. Se comparan ambas políticas, no se selecciona retrospectivamente la que más convenga para declarar el desempeño de producción.

La imputación y codificación se ajustan con train dentro del pipeline. No se usa clima futuro realizado y la variante ejecutada permanece Sin_clima. Separar los datos también en las transformaciones evita que la información del test afecte a la estimación de los predictores (scikit-learn, s.f.). Estos controles no certifican las fechas originales de publicación ni descartan por sí solos el sobreajuste al proceso de desarrollo. [N2]

**Cómo informar el tamaño del test.** Se muestran las fechas, casos y semanas objetivo únicas por corte, además de la evaluación acumulada. El porcentaje mensual divide los casos del bloque de test entre los de train y ese bloque; resulta pequeño porque train reúne años y cada bloque pronostica pocas semanas. No describe un reparto global 98/2, ni se suman los train repetidos. Cada horizonte y origen cuenta como un caso; las cantidades H1–H5 no equivalen a volumen independiente. Una proporción fija 80/20 no es un criterio suficiente de calidad ni un objetivo de esta revisión.

**Qué controla el sobreajuste.** La elección y los parámetros se mantienen fijados antes de esta corrida; se conserva regularización, complejidad y semilla; se comparan referencias en los mismos casos y errores fuera del ajuste por horizonte y mes. La comparación train/test usa el mismo ajuste. Un buen error retrospectivo, o un test menor que train, no prueba ausencia de sobreajuste: cambian composición, temporada y dificultad. El criterio para las conclusiones es el resultado observado del panel completo, su estabilidad entre ventanas y sus límites, sin cambiar el modelo para ganar en ese mismo test.

**Entrenamiento «en vivo»: reentrenamiento por lotes, no aprendizaje tallo a tallo.** En operación se propone actualizar al primer origen mensual con objetivos ya cerrados y conservar el ajuste compatible dentro del mes. Cambiar la versión de datos puede invalidar la caché. Actualizar fuentes, entrenar, generar una propuesta y publicarla son pasos separados. La arquitectura operativa debe validar datos y modelo, conservar trazabilidad y permitir volver a la versión anterior; automatizar el entrenamiento no equivale a autorizar automáticamente una publicación (Google Cloud, s.f.). [N3]

El ciclo acordable con la empresa es: validar/versionar fuentes → congelar información al corte → entrenar cuando corresponde → comprobar variables, finitud y totales → revisar la candidata conservando la versión anterior → generar y guardar antes de conocer el resultado → publicar explícitamente → evaluar al cerrar cada semana objetivo. Cada registro conserva origen, objetivo, horizonte, emisión, corte train, versión de datos/modelo y configuración climática. WAPE y sesgo se vigilan por horizonte y producto; una alerta inicia revisión de datos y operación antes de reentrenar. [PENDIENTE: acordar umbrales empresariales de alerta y promoción, latencia de las fuentes y responsable de aprobar cambios.]

La evaluación posterior de una predicción ya emitida puede actualizarse al llegar la producción real sin modificar aquel pronóstico. Las correcciones de las fuentes deben dejar una versión de la evaluación; no se sobrescriben resultados de referencia para aparentar una mejora. El comparador debe distinguir prueba archivada, reconstrucción retrospectiva actualizada y seguimiento de publicaciones anticipadas. La comprobación con el mismo corte del jueves del ingeniero continúa pendiente.
'''
    text=text.replace('### 4.3. Comparación con el ingeniero',methodology+'\n\n### 4.3. Comparación con el ingeniero',1)
    text=text.replace('### 5.1. Resultado del modelo semanal seleccionado frente al ingeniero',
        '### 5.1. Referencia histórica del modelo semanal seleccionado frente al ingeniero',1)
    text=text.replace('Esta es la comparación principal del **Boosting sin clima seleccionado en el cuaderno 19**:',
        'Esta es la referencia histórica conservada del **Boosting sin clima seleccionado en el cuaderno 19**; la comprobación ampliada con fuentes locales actuales se presenta en 5.1.3. Su configuración es:',1)
    source_table=table(['Fuente limpia','Registros','Hasta'],[[r.fuente,number(r.registros,0),r.hasta] for r in sources.itertuples()])
    horizon_rows=[]
    for h in ['1','2','3','4','5','Total']:
        m=recent.loc[recent.metodo.eq('19_mensual_sin_clima')&recent.horizonte.eq(h)].iloc[0]
        e=recent.loc[recent.metodo.eq('Ingeniero')&recent.horizonte.eq(h)].iloc[0]
        horizon_rows.append([('H'+h) if h!='Total' else 'H1–H5',number(m.casos,0),number(m.semanas_objetivo,0),
            number(m.WAPE)+' / '+number(e.WAPE),number(m.sesgo_pct)+' / '+number(e.sesgo_pct)])
    horizon_table=table(['Horizonte','Casos comunes','Semanas objetivo','WAPE (%) modelo / ingeniero','Sesgo (%) modelo / ingeniero'],horizon_rows)
    winners=[];engineer_winners=[]
    for h in ['1','2','3','4','5']:
        m=recent.loc[recent.metodo.eq('19_mensual_sin_clima')&recent.horizonte.eq(h)].iloc[0]
        e=recent.loc[recent.metodo.eq('Ingeniero')&recent.horizonte.eq(h)].iloc[0]
        if m.WAPE<e.WAPE:winners.append('H'+h)
        elif e.WAPE<m.WAPE:engineer_winners.append('H'+h)
    interpretation=('En este panel el modelo mensual tiene menor WAPE en '+(', '.join(winners) or 'ningún horizonte')+
        '; el ingeniero tiene menor WAPE en '+(', '.join(engineer_winners) or 'ningún horizonte')+'. '
        'El sesgo se contrasta por separado: una menor magnitud neta no implica por sí sola menor error absoluto. '
        'Esta conclusión corresponde a la extensión y no sustituye los resultados del panel original.')
    frozen=metrics.loc[metrics.periodo.eq('extension_desde_S37')&metrics.horizonte.eq('Total')&(
        metrics.metodo.eq('19_congelado_03ago')|metrics.comparacion.eq('19_mensual_sin_clima')&metrics.metodo.ne('Media4'))]
    labels={'19_mensual_sin_clima':'Boosting 19: actualización mensual','19_congelado_03ago':'Boosting 19: ajuste del 03/08 congelado','Ingeniero':'Estimado nominal del ingeniero'}
    policy_table=table(['Protocolo','Método','Casos','MAE','RMSE','WAPE (%)','Sesgo (%)'],[
        ['Mensual' if r.comparacion=='19_mensual_sin_clima' else 'Congelado',labels[r.metodo],number(r.casos,0),number(r.MAE),number(r.RMSE),number(r.WAPE),number(r.sesgo_pct)] for r in frozen.itertuples()])
    split_table=table(['Corte','Train: primer objetivo','Train: último objetivo','Test: orígenes','Casos train / test','% train / test'],[
        [str(r.corte)[:10],str(r.train_objetivo_desde)[:10],str(r.train_objetivo_hasta)[:10],
         str(r.test_origen_desde)[:10]+' a '+str(r.test_origen_hasta)[:10],
         number(r.train_casos,0)+' / '+number(r.test_casos,0),number(r.train_pct_casos)+' / '+number(r.test_pct_casos)] for r in splits.itertuples()])
    full=recent.loc[recent.metodo.ne('Media4')]
    all_metrics_table=table(['Método / horizonte','MAE','RMSE','MAPE* (%)','WAPE (%)','Dentro ±8 %*','Sesgo (%)'],[
        [('Modelo mensual' if r.metodo!='Ingeniero' else 'Ingeniero')+' / '+r.horizonte,
         number(r.MAE),number(r.RMSE),number(r.MAPE_positivos),number(r.WAPE),number(r.dentro_8_pct),number(r.sesgo_pct)] for r in full.itertuples()])
    new_section=f'''

### 5.1.3. Comprobación ampliada con datos locales y política de actualización

El cuaderno 26 se ejecuta sobre la copia `{summary['snapshot']}`. Se usa el histórico validado de producción, una descarga WebFlor archivada hasta el 27/10, el clima recibido más reciente y el plano S42. La evaluación puede repetirse sin conexión a la empresa porque las fuentes están archivadas; el cuaderno no escribe en SQL. La persistencia de las fuentes limpias en el esquema EP se ejecuta aparte y conserva la base previa hasta validar la carga. El ETL verifica los hashes y conserva los tallos en la agregación semanal. Las nuevas entradas no se interpretan como prueba de una nueva superioridad: primero se auditan, se construyen variables con el mismo procedimiento y se ejecuta la configuración fijada.

{source_table}

La reconstrucción reúne {number(summary['casos_evaluados'],0)} casos de predicción, {summary['origenes_evaluados']} orígenes y {summary['semanas_objetivo']} semanas objetivo distintas desde {summary['objetivo_desde']} hasta {summary['objetivo_hasta']}. Hay {number(summary['casos_pareados'],0)} casos con pareja nominal del ingeniero. Cada objetivo debe terminar antes de la fecha de análisis, 28/10; una semana en curso no se evalúa por disponer de algunos días de corte.

**Evaluación 2026 completa sobre las fuentes reconstruidas.** La siguiente tabla reúne referencia y extensión; sus casos son los mismos para el modelo y el ingeniero. La comparación posterior se muestra después para distinguir la estabilidad reciente del balance acumulado. No se interpreta la diferencia con la cifra archivada como efecto aislado de una única mejora, pues cambiaron las fuentes y el intervalo.

{annual_table}

**Resultado posterior a S36, sobre los mismos casos.** El período se define por semana objetivo: incluye los pronósticos emitibles desde orígenes anteriores para esos objetivos, manteniendo H1–H5. No se duplican ni reasignan horizontes para completar una semana sin archivo nominal.

{horizon_table}

{interpretation}

![Figura 20. WAPE y sesgo por horizonte en la extensión posterior a S36, mismos casos nominales. Fuente: cuaderno 26, ejecución local.](../Datos_analiticos_proyecto/validacion_temporal_20261028/figuras/extension_horizontes.png)

**Contraste del reentrenamiento.** El ajuste congelado al 03/08 conserva una separación fija frente a todos los objetivos de la extensión. El mensual incorpora únicamente objetivos ya terminados antes de cada nuevo corte. Las métricas siguientes comparan ambos protocolos con el ingeniero en sus mismos casos; no se usa esta tabla para volver a seleccionar parámetros.

{policy_table}

**Particiones reproducibles del modelo mensual.** La fecha de objetivo identifica el lunes: el cierre se obtiene sumando siete días. Cada train debe cerrar a más tardar en su corte. Las filas de meses distintos reutilizan historia y no se suman para formar una partición global.

{split_table}

**Detalle de métricas del panel posterior.** El asterisco conserva la restricción a reales positivos para MAPE y ±8 %. Los conteos por horizonte están en la tabla anterior; el archivo de resultados mantiene también el saldo neto en tallos y todos los indicadores por caso.

{all_metrics_table}

La comparación del modelo sobre todos los casos, incluidos los que no tienen estimado nominal, se guarda aparte. La auditoría `auditoria_semanas.csv` identifica semanas sin pareja. S01 inicia el 29/12/2025 y se identifica por año ISO. La ausencia de H1 nominal en una semana no se resuelve tomando un archivo posterior como si hubiera sido emitido a tiempo. Estas restricciones afectan el panel comparado, no significan que se haya eliminado producción de la base.

La tabla de entrenamiento y prueba de cada ajuste, con MAE, RMSE, WAPE, MAPE, ±8 % y sesgo, está en `train_test_por_ajuste.csv`; el cuaderno los expone y permite recalcularlos desde las predicciones. El pronóstico local del origen 26/10 se guarda aparte como simulación retrospectiva, con su fecha real de cálculo ({summary['fecha_corrida']}) y el corte de evaluación del 28/10 identificados por separado. No es una publicación anticipada y no se evalúan sus semanas todavía incompletas.

**Interpretación y límites.** El modelo mensual obtiene {number(rm.WAPE)} % de WAPE frente a {number(re.WAPE)} % del ingeniero en la extensión. El signo y magnitud del sesgo se informan sin convertirlos en una corrección automática. Se informa cada horizonte porque el agregado puede ocultar dificultades. El panel es más reciente y más amplio que la referencia original, pero sigue siendo retrospectivo; septiembre fue revisado previamente y no se ha certificado la disponibilidad histórica de cada archivo. El conjunto informativo del lunes puede diferir del jueves del ingeniero. Una mayor cantidad de datos no elimina estas limitaciones ni demuestra ausencia de sobreajuste. [E26]
'''
    marker='### 5.2.'
    pos=text.index(marker);text=text[:pos]+new_section+'\n\n'+text[pos:]
    train_test=pd.read_csv(OUT/'train_test_por_ajuste.csv')
    last_cut=train_test.corte.max();last=train_test.loc[train_test.corte.eq(last_cut)]
    latest_table=table(['Partición / corte','Casos','MAE','RMSE','WAPE (%)','Sesgo (%)'],[
        [r.particion+' / '+str(r.corte)[:10],number(r.casos,0),number(r.MAE),number(r.RMSE),number(r.WAPE),number(r.sesgo_pct)] for r in last.itertuples()])
    text=text.replace('### 5.5. Entrenamiento y evaluación del mismo ajuste',
        '### 5.5. Entrenamiento y evaluación del mismo ajuste\n\nLa comprobación actualizada del cuaderno 26 conserva las siguientes métricas del último corte mensual. El test reúne todos sus casos con real, no sólo parejas del ingeniero; su tamaño no se confunde con el acumulado de semanas evaluadas.\n\n'+latest_table+'\n\nA continuación se conservan, como referencia histórica, los diagnósticos de agosto y los modelos diarios de la edición anterior. No se presentan como el último ajuste de la aplicación.',1)
    text=text.replace('### 5.4. Interpretación de variables del modelo seleccionado',
        '### 5.4. Interpretación de variables del modelo seleccionado\n\nEste diagnóstico conserva la evaluación archivada del cuaderno 19; no se recalculó la importancia de variables con las semanas nuevas del cuaderno 26. Sus gráficos explican el ajuste histórico y no cuantifican aportes en la extensión de 5.1.3.',1)
    text=text.replace('### 5.6. De dónde proviene el error: del producto a las semanas críticas',
        '### 5.6. De dónde proviene el error: del producto a las semanas críticas\n\nEsta descomposición y sus figuras conservan el panel nominal de referencia hasta S36. La extensión del cuaderno 26 se informa aparte en 5.1.3 y en `errores_producto.csv`; no se atribuyen a esas semanas nuevas las trayectorias ni las explicaciones históricas siguientes.',1)
    conclusion=f' La reconstrucción del cuaderno 26 aporta {summary["semanas_objetivo"]} semanas objetivo distintas: en 2026 completo el WAPE es {number(annual_model.WAPE)} % para el modelo y {number(annual_engineer.WAPE)} % para el ingeniero sobre {number(annual_model.casos,0)} casos comunes. En el tramo posterior a S36 el WAPE mensual es {number(rm.WAPE)} % frente a {number(re.WAPE)} % del ingeniero y los sesgos son {number(rm.sesgo_pct)} % y {number(re.sesgo_pct)} %. Esta comprobación amplía la evidencia técnica sin certificar aún equivalencia del corte informativo ni desempeño prospectivo.'
    pos=text.index('### 7.4.');text=text[:pos].rstrip()+conclusion+'\n\n'+text[pos:]
    refs='''

[E26] `Notebooks/Analisis/26_validacion_temporal_actualizada_y_operacion.ipynb`; resultados, cortes, fuentes y verificación en `Datos_analiticos_proyecto/validacion_temporal_20261028/`. Evaluación reproducible sobre fuentes archivadas, configuración del 19 conservada.

[N1] Hyndman, R. J., y Athanasopoulos, G. (2021). *Forecasting: Principles and Practice* (3.ª ed.), sección 5.10. OTexts. https://otexts.com/fpp3/tscv.html

[N2] scikit-learn developers. (s.f.). *Common pitfalls and recommended practices*. Documentación oficial, apartado de fuga de información. Consulta: 28 de octubre de 2026. https://scikit-learn.org/stable/common_pitfalls.html

[N3] Google Cloud. (s.f.). *MLOps: Continuous delivery and automation pipelines in machine learning*. Cloud Architecture Center. Consulta: 28 de octubre de 2026. https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
'''
    text=text.replace('## Anexo A.',refs+'\n\n## Anexo A.',1)
    # La figura nueva se inserta después de la 13; conservar numeración corrida.
    text=regex.sub(r'Figura (\d+)',lambda m:'Figura '+str(14 if int(m[1])==20 else int(m[1])+1 if 14<=int(m[1])<=19 else int(m[1])),text)
    (FOLDER/(NAME+'.md')).write_text(text,encoding='utf-8')
    generator=(FOLDER/'generar_documento_v7.py').read_text(encoding='utf-8')
    generator=generator.replace('Documento_LaGaitana_v7_revision_profesor_20261028',NAME).replace('Revision_v7','Revision_v8').replace('Versión 7','Versión 8')
    generator=generator.replace('Word de la revisión v7','Word de la revisión v8')
    (FOLDER/'generar_documento_v8.py').write_text(generator,encoding='utf-8')
    exporter=(FOLDER/'exportar_revision_v7_pdf.py').read_text(encoding='utf-8').replace('Documento_LaGaitana_v7_revision_profesor_20261028',NAME).replace('Revision_v7','Revision_v8')
    exporter=exporter.replace('5.1. Resultado','5.1. Referencia')
    (FOLDER/'exportar_revision_v8_pdf.py').write_text(exporter,encoding='utf-8')
    (REV/'resumen_cambios.json').write_text(json.dumps({'documento':NAME,'fuentes':sources.to_dict('records'),
        'evaluacion':summary,'verificaciones':checks,'modelo_mensual_nuevo_WAPE':rm.WAPE,
        'ingeniero_nuevo_WAPE':re.WAPE,'modelo_mensual_nuevo_sesgo':rm.sesgo_pct,
        'ingeniero_nuevo_sesgo':re.sesgo_pct,'version_anterior_conservada':True},ensure_ascii=False,indent=2),encoding='utf-8')
    pending=list(dict.fromkeys(regex.findall(r'\[PENDIENTE:\s*(.*?)\]',text,regex.S)))
    (REV/'PENDIENTES_v8.md').write_text('# Pendientes de la versión 8\n\n'+'\n\n'.join(f'{i}. {" ".join(item.split())}' for i,item in enumerate(pending,1))+'\n',encoding='utf-8')
    (REV/'CAMBIOS_v8.md').write_text('''# Cambios de la versión 8

- Se conserva la versión 7 y sus resultados históricos, objetivos literales y conclusiones por objetivo.
- Se incorporan las fuentes reconstruidas y verificadas del cuaderno 26 y su evaluación ejecutada hasta la última semana completa.
- Se distinguen entrenamiento, selección de 2025, referencia original de 2026, extensión posterior y publicaciones anticipadas.
- Se documentan fechas, porcentajes y casos por ajuste mensual, contraste con el ajuste congelado, métricas del mismo ajuste y límites de la evaluación retrospectiva.
- Se incorporan WAPE, sesgo y demás métricas reales del nuevo panel sin volver a elegir hiperparámetros. El desarrollo diario conserva su carácter preliminar y sus resultados anteriores.
- Se explica el ciclo operativo de reentrenamiento por lotes, versionamiento, revisión y publicación explícita. Se mantiene pendiente comprobar igualdad del corte del jueves y validación empresarial.
- Se conserva el formato del escrito: tablas monocromas, gráficos en color y figuras numeradas consecutivamente.

La evidencia numérica queda en `resumen_cambios.json`, `verificacion_final.json` y en los archivos ejecutados del cuaderno 26. Los marcadores aún abiertos se reúnen en `PENDIENTES_v8.md`.
''',encoding='utf-8')
    print(NAME)

if __name__=='__main__':main()
