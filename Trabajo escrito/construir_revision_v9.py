"""Compone la revisión del asesor desde prosa editable y evidencia archivada.

No ejecuta ETL, entrenamiento, publicaciones ni cambios de datos. Conserva v8.
"""
from pathlib import Path
import sys,json,re,hashlib
import numpy as np
import pandas as pd
sys.stdout.reconfigure(encoding='utf8')
F=Path(__file__).resolve().parent;R=F.parent;O=F/'Revision_v9'
from revision_v9_config import NAME
V=R/'Datos_analiticos_proyecto/validacion_temporal_20261028'
facts=json.loads((O/'datos_verificados.json').read_text(encoding='utf8'))
audit=pd.read_csv(F/'Revision_v7/auditoria_metricas_v7.csv')
annual=pd.read_csv(V/'metricas_2026_completo.csv')
ext=pd.read_csv(V/'metricas_comparadas.csv');ext=ext.loc[ext.periodo.eq('extension_desde_S37')&ext.comparacion.eq('19_mensual_sin_clima')]
if ext.empty:
    # El campo de comparación sigue el identificador del método calculado.
    raw=pd.read_csv(V/'metricas_comparadas.csv');ext=raw.loc[raw.periodo.eq('extension_desde_S37')&raw.metodo.isin(['19_mensual_sin_clima','Ingeniero'])].drop_duplicates(['metodo','horizonte'])
tables={};figures={};used=[]
def num(v,d=2):
    if v is None or pd.isna(v):return 'No archivado'
    return f'{float(v):,.{d}f}'.replace(',','X').replace('.',',').replace('X','.')
def table(key,caption,headers,rows,note=''):
    clean=lambda x:str(x).replace('|',' / ').replace('\n',' ')
    tables[key]={'caption':caption,'headers':headers,'rows':[[clean(x) for x in row] for row in rows],'note':note}
def metric_table(key,caption,frame,labels=None):
    rows=[]
    for _,r in frame.iterrows():
        is_old='WAPE_pct' in frame.columns
        label=r['modelo'] if is_old else r['metodo'];label=(labels or {}).get(label,label)
        label=label.replace('Ingeniero','Responsable de producción')
        vals=[r['n'] if is_old else r['casos'],r.MAE,r.RMSE,r['MAPE_pct'] if is_old else r.MAPE_positivos,r.WAPE_pct if is_old else r.WAPE,r.dentro_8_pct,r.sesgo_pct]
        rows.append([label,num(vals[0],0)]+[num(v) for v in vals[1:]])
        if is_old:used.append(r.to_dict())
    table(key,caption,['Método','Casos','MAE¹','RMSE¹','MAPE² (%)','WAPE (%)','±8 %² (%)','Sesgo (%)'],rows,'¹ Tallos por caso. ² Sólo reales positivos. Sesgo = pronóstico − real. Fuente: cálculos sobre predicciones archivadas del estudio.')
table('glosario','Términos operativos utilizados en el estudio',['Término','Significado en este trabajo'],[
['Cama','Unidad física de cultivo identificada dentro de un invernadero.'],['Cama piloto','Cama o referencia seguida para registrar plantas, ciclo y cortes usados en estadísticas de rendimiento.'],['Ciclo de cultivo','Periodo de una siembra identificada, que permite distinguir usos sucesivos de una cama.'],['Plano de siembra','Registro de existencias, ubicación, plantas, variedad y siembra en una fecha de referencia.'],['Cohorte','Grupo de plantas con la misma identidad comercial y fecha de siembra dentro de un plano; puede reunir varias camas.'],['Corte y tallos cortados','Actividad de cosecha y cantidad de tallos que queda registrada; no identifica por sí sola su clasificación exportable.'],['Rendimiento','Cociente entre tallos de un corte piloto y plantas de la observación, expresado en tallos por planta.'],['Curva de rendimiento','Resumen empírico de rendimientos por variedad y edad semanal del cultivo.']])
sources=pd.read_csv(V/'fuentes_validadas.csv').set_index('fuente')
source_desc=[('produccion_real_limpio','Producción reportada','Movimiento de corte','Finca, fecha, producto, color, variedad, grado, lote y tallos.'),('planos_siembra_limpio','Planos de siembra','Fila de inventario por versión','Ubicación, identidad comercial, plantas, área, siembra y edad.'),('curvas_variedad_limpio','Estadísticas piloto consolidadas','Observación piloto–semana','Cama, ciclo, fechas, plantas, tallos y rendimiento; historia entre ediciones.'),('clima_limpio','Clima','Medición de finca e instante','Temperatura, humedad, radiación y lluvia; frecuencia y validez auditadas.'),('estimados_semanales_limpio','Estimados del responsable','Serie–edición–semana objetivo','Cantidades estimadas, origen y horizonte nominal, procedencia y marcas de envío.')]
table('fuentes','Dimensiones de las fuentes depuradas utilizadas',['Fuente','Filas / variables','Periodo observado u objetivo','Nivel y características'],[[name,f"{num(sources.loc[key,'registros'],0)} / {len(facts['schemas'][key]['cols'])}",f"{sources.loc[key,'desde']} a {sources.loc[key,'hasta']}",level+'. '+desc] for key,name,level,desc in source_desc],'Los periodos son de contenido, no fechas de publicación. Las fuentes incluyen más de una finca; la inferencia principal se limita a GAITANA. Fuente: extracción verificada del 28/10/2026.')
definitions={'unica':('Única','Una sola cama y ciclo compatibles; su uso requiere superar los filtros restantes.'),'ambigua':('Ambigua','Más de una pareja compatible; no se elige una por conveniencia.'),'conflicto_ciclo':('Conflicto_ciclo','Candidatos incompatibles con la siembra o ciclo informado.'),'llave_incompleta':('Llave_incompleta','Faltan componentes para identificar la correspondencia.'),'sin_pareja':('Sin_pareja','No se encuentra una referencia compatible en el libro de pilotos.')}
table('estados','Correspondencia de estadísticas con cama y ciclo en la edición 2026',['Estado','Historia de la edición','Cortes fechados en 2026','Interpretación'],[[definitions[k][0],num(facts['uniones'][k],0),num(facts['uniones_cortes_2026'].get(k,0),0),definitions[k][1]] for k in definitions],'Los denominadores son 543.368 y 46.157 filas, respectivamente. La edición incluye cortes de otros años. Fuente: auditoría de correspondencias de la extracción utilizada.')
table('variables','Bloques de predictores y función en el modelo semanal',['Bloque','Contenido y construcción','Configuración seleccionada'],[
['Identidad y calendario','Producto, color y variedad; horizonte y seno/coseno de semana objetivo.','Ambas rutas; la finca principal está delimitada a GAITANA.'],['Memoria semanal (9)','Tres rezagos, Media4, media8, dispersión4, tendencia4−8, cambio reciente y producción a 364 días.','Ambas rutas.'],['Corte diario (19)','Media, suma y conteos en 3/5/7/14 días; dispersión7, rezagos1/7, media exponencial5, tendencias3/5 y días desde reporte.','Ambas rutas; excluye el día de origen.'],['Memoria larga (7)','Media12, dispersión8/12, conteos4/8/12 y tendencia4−12.','Ambas rutas.'],['Referencia teórica (3)','Teoría habilitada, antigüedad del plano y Media4 menos teoría.','Sólo ruta teórica.'],['Clima','Seis resúmenes semanales y nueve diarios; sensibilidad ampliada añade 14/28 días, lluvia y disponibilidad.','Contrastado; excluido del seleccionado.'],['Revisiones de teoría','Dos versiones anteriores para el mismo objetivo y su cambio.','Contrastadas; no entran al seleccionado.']])
table('modelos','Familias y variantes implementadas para el pronóstico semanal',['Papel','Método','Decisión evaluada'],[
['Referencias','Último valor, Media4, teoría sin ajuste','Medir el aporte frente a reglas simples.'],['Contraste lineal','Ridge sobre corrección teórica','Comparar una corrección lineal regularizada.'],['Modelo base de aprendizaje','Boosting sobre teoría o Media4','Aprender real menos referencia, en dos rutas.'],['Ablaciones','Boosting sin memoria o sin clima','Contrastar cada bloque sobre casos comunes.'],['Extensiones','Resúmenes diarios, memoria larga, revisiones teóricas','Examinar señales más recientes y distintas ventanas.'],['Sensibilidades','Corrección relativa, pérdida absoluta y combinación de referencias','Contrastar escala, pérdida y mezcla; no todos aíslan un único cambio.'],['Selección principal','Boosting sin clima, grupos H1–H2/H3–H5','Dos grupos con una ruta de teoría y otra de Media4 en cada uno.'],['Sensibilidad de fuentes','Clima básico, ampliado y curva atribuida a GAITANA','Mantener arquitectura para estudiar clima y procedencia.'],['Experimentos recientes','Un ajuste por horizonte; n−1; propios de producto–horizonte','Examinar especialización y combinación sin predictores del referente.']])
table('parametros','Configuraciones de los métodos de aprendizaje y pilotos',['Método','Parámetros implementados','Alcance del ajuste'],[
['Boosting semanal seleccionado','Tasa 0,08; 80 iteraciones; 15 hojas; mínimo 40 por hoja; L2 = 1; pérdida cuadrática; sin parada temprana; semilla 42.','Mismos valores en ambos grupos y rutas.'],['Ridge','Alpha = 100; mediana e indicador de faltante; estandarización numérica; categorías one-hot.','Contraste fijo; sin búsqueda exhaustiva de alpha.'],['Ajustes por horizonte','80 iteraciones en H1/H2/H5; 40 en H3/H4; 15 hojas; restantes parámetros del boosting principal.','Selección en noviembre de 2025.'],['Modelos de producto H3–H5','Miniclavel: 40 iteraciones; clavel: 80; 15 hojas y restantes valores principales.','Subconjuntos propios y pesos seleccionados en noviembre.'],['Boosting diario autónomo','80 iteraciones; 15 hojas; tasa 0,08; mínimo 40; L2 = 1; semilla 42.','Corrección logarítmica; hasta 104 semanas previas; actualización mensual.'],['SARIMA / SARIMAX','(1,0,1)×(0,1,1,7); log(1+tallos); 365 días previos; SARIMAX con clima rezagado 7 días.','Órdenes fijos; tres series; sólo ajustes convergentes.'],['LSTM','Dos capas de 48 unidades; dropout 0,15; capa intermedia 24; Adam 0,001, regularización 0,00001; MSE; lote 512; gradiente máximo 1.','28 días de entrada; hasta 12 épocas, paciencia 3; máximo 25.000 ejemplos train muestreados con semilla 42.']])
tables['parametros']['rows'].insert(4,['Combinación propia/general','Peso del modelo propio: 1 en H3 y H4; 0,75 en H5. Peso general: complemento a 1.','Sólo clavel/miniclavel. H1 conserva el agrupado y H2 el ajuste H2; otros productos usan el general de su horizonte.'])
table('particiones','Funciones de los periodos y controles de disponibilidad',['Conjunto / protocolo','Periodo','Uso y restricción'],[
['Desarrollo y entrenamiento','Historia desde 2021; entrenamiento anterior a cada corte.','Sólo semanas objetivo terminadas. Transformaciones ajustadas en train.'],['Validación de selección','Noviembre–diciembre de 2025; objetivos cerrados antes de 01/01/2026.','Elección de variante y pesos; no equivale al test de 2026.'],['Prueba retrospectiva ampliada','Año ISO 2026, semanas objetivo 1–43, lunes 29/12/2025 a 19/10/2026.','Configuración fija; ajuste al primer origen de cada mes con resultados ya cerrados.'],['Extensión reciente','Objetivos desde 07/09/2026 (S37) hasta 19/10/2026 (S43).','Mensual y congelado al 03/08 en casos nominales comunes. H1 llega a S42 comparable.'],['Pilotos diarios','Reparto/boosting: orígenes enero–agosto de 2026; LSTM: test septiembre.','Tareas y paneles separados; no son la evaluación semanal ampliada.']])
table('diario_metodo','Procedimientos diarios y diferencias de tarea',['Procedimiento','Entradas y operación','Evaluación'],[
['Autónomo','Boosting estima el día con producción y clima pasados, identidad y calendario. No recibe el total semanal actual.','Días reportados; cantidades diarias sin coherencia semanal impuesta.'],['Reconciliado','Total semanal pronosticado × siete pesos: uniforme, perfil histórico o perfil aprendido.','Mismos días; suma de siete pronósticos igual al total de partida.'],['SARIMA / SARIMAX','Dependencia temporal y ciclo semanal; exógenas rezagadas en SARIMAX.','Tres series, primer origen de cada mes; casos comunes y convergencia.'],['LSTM de un día adelante','Secuencia de 28 días, máscara, calendario e historia a 364 días; actualiza el pasado para cada día.','Septiembre; comparación propia y panel común, sin reconciliación.']])
metric_table('iniciales','Referencias, correcciones y ablaciones en el panel inicial común',audit.loc[audit.etapa.eq('12 · casos comunes')],{'Boosting teórico con memoria y clima':'Boosting teórico con memoria','Boosting sobre Media4, sin teoría':'Boosting sobre Media4'})
metric_table('seleccion','Selección previa a 2026: variantes de clima y procedencia',audit.loc[audit.etapa.eq('19 · validación 2025')])
def horizon_table(key,caption,df):
    rows=[]
    for h in ['1','2','3','4','5','Total']:
        hh=df.loc[df.horizonte.astype(str).isin([h,h+'.0'])];mm=hh.loc[hh.metodo.eq('19_mensual_sin_clima')].iloc[0];ee=hh.loc[hh.metodo.eq('Ingeniero')].iloc[0]
        assert int(mm.casos)==int(ee.casos)
        rows.append(['Conjunto' if h=='Total' else 'H'+h,num(mm.casos,0),f'{num(mm.WAPE)} / {num(ee.WAPE)}',f'{num(mm.sesgo_pct)} / {num(ee.sesgo_pct)}'])
    table(key,caption,['Horizonte','Casos comunes','WAPE modelo / referente (%)','Sesgo modelo / referente (%)'],rows,'El referente es el responsable de producción. Sesgo = pronóstico − real; mismos casos por fila. Fuente: predicciones de la evaluación ampliada.')
horizon_table('horizontes','Evaluación ampliada de 2026 por horizonte, configuración seleccionada',annual)
metric_table('global','Métricas conjuntas de la evaluación ampliada de 2026',annual.loc[annual.horizonte.eq('Total')],{'19_mensual_sin_clima':'Modelo semanal seleccionado'})
train=pd.read_csv(V/'train_test_por_ajuste.csv');train=train.loc[train.corte.eq('2026-10-05')].copy();train['metodo']=train.particion.map({'train':'Entrenamiento · 05/10','test':'Prueba · 05/10'})
metric_table('train','Entrenamiento y prueba del mismo ajuste de octubre',train)
horizon_table('extension','Extensión desde la semana 37: mismo modelo y comparación nominal',ext)
products=pd.read_csv(O/'error_producto_actualizado.csv').head(4)
table('productos','Productos con mayor aporte al WAPE en la evaluación ampliada',['Producto','Casos','WAPE modelo / referente (%)','Aporte modelo / referente (pp)'],[[r.producto,num(r.casos,0),f'{num(r.WAPE_modelo)} / {num(r.WAPE_referencia)}',f'{num(r.aporte_modelo_pp)} / {num(r.aporte_referencia_pp)}'] for _,r in products.iterrows()],'Aporte = error absoluto del producto dividido por real de todo el panel; se calcula antes de agregar. Fuente: reconstrucción sobre los 20.283 casos nominales.')
daily=audit.loc[audit.etapa.eq('Diario 05 · días comunes')&audit.modelo.isin(['Boosting autónomo','Boosting reconciliado, selección semanal','Perfil histórico, selección semanal','Uniforme, selección semanal'])]
metric_table('diario','Pronóstico diario: casos comunes de enero–septiembre de 2026',daily,{'Boosting reconciliado, selección semanal':'Boosting reconciliado','Perfil histórico, selección semanal':'Perfil histórico reconciliado','Uniforme, selección semanal':'Uniforme reconciliado'})
metric_table('sarima','Piloto diario de series temporales: 135 días comunes',audit.loc[audit.etapa.eq('Diario 03–05 · piloto')])
metric_table('lstm','Ensayo de un día adelante: septiembre de 2026, soporte propio',audit.loc[audit.etapa.eq('Diario 06 · soporte propio')&audit.modelo.isin(['LSTM sin clima / modo automático','Media de siete días observados','Último valor disponible'])])
# Diccionario: todas las 47 columnas se documentan una sola vez, agrupadas por significado.
dictionary=[
('finca, producto, color, variedad','Identidad de la serie comercial; no agrupa fincas con etiquetas distintas.'),
('origen, horizonte, semana_objetivo','Lunes de H1; anticipación H1–H5; lunes de la semana a estimar.'),
('ultima_semana_utilizada','Última semana histórica de producción usada, anterior al origen.'),
('y','Tallos reportados de la semana objetivo; respuesta observada después, nunca predictor.'),
('produccion_lag1, produccion_lag2, produccion_lag3','Tallos una, dos y tres semanas calendario antes del origen.'),
('media_4, media_8, desv_4','Promedios semanales previos de cuatro/ocho observaciones completas y dispersión de cuatro.'),
('tendencia_4_8, cambio_reciente','Media4 − media8 y último valor − penúltimo valor, en tallos.'),
('observaciones_previas','Cantidad de semanas históricas reportadas; no exige continuidad de toda la historia.'),
('temperatura_semana_lag1, humedad_semana_lag1, radiacion_semana_lag1','Medias de la semana previa a partir de días válidos; unidades conservadas de la fuente.'),
('temperatura_semana_media4, humedad_semana_media4, radiacion_semana_media4','Promedio de cuatro semanas previas válidas; son variables de finca.'),
('fecha_estacional, produccion_52','Fecha objetivo menos 364 días y tallos observados en esa misma serie y fecha semanal.'),
('semana_seno, semana_coseno','Coordenadas circulares de la semana objetivo; sin unidad productiva.'),
('union_finca, union_producto, union_color, union_variedad','Nombres homologados para integrar producción y proyecciones; conserva identidad comercial.'),
('plano, fecha_plano, disponible','Versión del inventario, fecha nominal y fecha supuesta de disponibilidad; no certifica publicación real.'),
('teoria','Aportes teóricos de las cohortes con edad representada para ese objetivo. Puede ser suma parcial.'),
('cohortes, sin_cobertura','Número de grupos de siembra del plano y cuántos carecen de rendimiento para su edad objetivo; no cuentan camas perdidas.'),
('curva_completa, teoria_modelo','Indicador de todas las edades representadas y referencia habilitada como total. Si no aplica, no se sustituye por cero.'),
('teoria_previa_1, teoria_previa_2, revision_teoria','Referencias de dos versiones anteriores para el mismo objetivo; diferencia entre actual y anterior utilizable.'),
('antiguedad_curva, desviacion_reciente_teoria','Semanas desde fecha del plano al origen y Media4 − teoría habilitada; no son edad de planta ni error del mismo periodo.'),
('admisible_modelo','Media4 disponible y al menos 26 semanas reportadas; no identifica train/test ni exige objetivo conocido.'),
('motivo_cobertura','Estado de aplicación: curva total, edades no representadas, sin plano elegible o sin pareja serie–objetivo. No significa producción perdida.')]
actual=set(pd.read_parquet(R/'plataforma_gaitana/storage/datasets/evaluacion_local_20261028/Datos_analiticos_proyecto/modelo_con_proyecciones_teoricas/base_analitica_proyecciones.parquet').columns)
documented={x.strip() for fields,_ in dictionary for x in fields.split(',')};assert documented==actual,(actual-documented,documented-actual)
table('diccionario','Diccionario agrupado de las 47 columnas de la base analítica',['Columna o grupo','Interpretación'],dictionary,'Las variables ampliadas se describen en la metodología; no se confunden con las 47 columnas de esta base. Los valores ausentes no significan cero.')
# Complementos seleccionados: conservar decisiones y algoritmos distintos, evitar repetir el ranking anual.
complement=audit.loc[(audit.etapa.eq('14 · panel histórico'))|(audit.etapa.eq('15 · panel histórico')&~audit.modelo.isin(['Referencia antes de calidad y clima','Sistema diario del 14','Ingeniero']))|(audit.etapa.eq('24 · tuning y calibración'))|(audit.etapa.eq('25 · candidato final')&audit.modelo.isin(['Especializado sin mezcla','Ensamble de modelos propios']))|audit.etapa.str.startswith('23 ·')|(audit.etapa.eq('Diario 06 · soporte común'))].copy()
comp_rows=[]
for _,r in complement.iterrows():
    if r.etapa.startswith('14'):block='Diarias · histórico'
    elif r.etapa.startswith('15'):block='Memoria · histórico'
    elif r.etapa.startswith('23'):block=r.etapa.split(' · ')[1].replace('Sin ','n−1: ')
    elif r.etapa.startswith('24'):block='Horizontes · reciente'
    elif r.etapa.startswith('25'):block='Producto · reciente'
    else:block='LSTM · común'
    label=r.modelo.replace('Ingeniero','Referente').replace('del 14','previo')
    comp_rows.append([block+' / '+label,num(r.n,0),num(r.MAE),num(r.RMSE),num(r.MAPE_pct),num(r.WAPE_pct),num(r.dentro_8_pct),num(r.sesgo_pct)]);used.append(r.to_dict())
table('complementos','Contrastes complementarios por bloque, con sus paneles originales',['Bloque / método','Casos','MAE¹','RMSE¹','MAPE² (%)','WAPE (%)','±8 %² (%)','Sesgo (%)'],comp_rows,'¹ Tallos por caso. ² Reales positivos. Los contrastes recientes comprenden objetivos 07–21/09/2026; el panel LSTM común, 01–26/09. Fuente: predicciones archivadas, sin nuevo ajuste.')
figures={
'curva':('Curva empírica y soporte de Solomio–Ard blanco; referencia del plano del 12/10/2026. Fuente: rendimientos piloto depurados.','Revision_v9/Figuras/curva_soporte.png'),
'semanal':('Lógica metodológica del pronóstico semanal seleccionado. Fuente: elaboración propia a partir del procedimiento implementado.','Revision_v9/Figuras/metodologia_semanal.png'),
'pretratamiento':('Pretratamiento y universos de integración. Los bloques piloto y analítico tienen unidades distintas. Fuente: extracción verificada del estudio.','Revision_v9/Figuras/pretratamiento.png'),
'soporte':('Casos observados con referencia teórica total, por horizonte. Eje vertical truncado desde 15 %. Fuente: panel analítico actualizado.','Revision_v9/Figuras/soporte_edades.png'),
'comparacion':('WAPE y sesgo por horizonte: modelo seleccionado y responsable de producción, evaluación ampliada de 2026. Fuente: mismos casos nominales por método.','Revision_v9/Figuras/comparacion_horizontes.png'),
'clima':('Asociaciones entre clima previo y error relativo de teoría: mediana de Spearman entre series, sin unidad. Blancos: asociación no estimable. Fuente: análisis climático exploratorio del estudio.','Revision_v9/Figuras/clima_asociaciones.png')}
ann=annual.loc[annual.horizonte.eq('Total')].set_index('metodo')
values={'pct_soporte':num(100*facts['base']['por_estado']['curva_completa']/facts['base']['observados']),
'pct_mini':num(facts['composicion']['MINICARNATION']['pct']),'pct_clavel':num(facts['composicion']['CARNATION']['pct']),
'rho_h1':num(next(x['mediana_spearman'] for x in facts['asociaciones_memoria'] if x['horizonte']==1 and x['variable']=='produccion_lag1'),3),
'rho_h5':num(next(x['mediana_spearman'] for x in facts['asociaciones_memoria'] if x['horizonte']==5 and x['variable']=='produccion_lag1'),3),
'sesgo_tallos_modelo':num(abs(ann.loc['19_mensual_sin_clima','sesgo_tallos']),0),
'sesgo_tallos_referencia':num(abs(ann.loc['Ingeniero','sesgo_tallos']),0),
'aporte_mini':num(products.loc[products.producto.eq('MINICARNATION'),'aporte_modelo_pp'].iloc[0])}
source=(O/'contenido_academico.md').read_text(encoding='utf8');nt=0;nf=0;registry={}
def expand(m):
    global nt,nf
    kind,key=m.groups()
    if kind=='dato':return values[key]
    if kind=='tabla':
        nt+=1;t=tables[key];bid='tab_'+key;registry[bid]={'number':nt,'kind':'Tabla','caption':t['caption']}
        return f"Tabla {nt}. {t['caption']} {{#{bid}}}\n\n"+'\n'.join(['| '+' | '.join(t['headers'])+' |','| '+' | '.join(['---']*len(t['headers']))+' |']+['| '+' | '.join(row)+' |' for row in t['rows']])+ ('\n\nNota. '+t['note'] if t['note'] else '')
    nf+=1;caption,path=figures[key];bid='fig_'+key;registry[bid]={'number':nf,'kind':'Figura','caption':caption}
    return f'![Figura {nf}. {caption}]({path}) {{#{bid}}}'
text=re.sub(r'\{\{(tabla|figura|dato):([a-z_0-9]+)\}\}',expand,source)
assert '{{' not in text
refs=re.findall(r'@(tab_[a-z_]+|fig_[a-z_]+)',text);assert set(refs)<=registry.keys(),set(refs)-registry.keys()
(F/(NAME+'.md')).write_text(text,encoding='utf8')
(O/'objetos_y_referencias.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf8')
pd.DataFrame(used).drop_duplicates(['etapa','modelo']).to_csv(O/'metricas_historicas_incluidas.csv',index=False)
(O/'tablas_estructuradas.json').write_text(json.dumps(tables,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'fuente':NAME+'.md','tablas':nt,'figuras':nf,'referencias_cruzadas':len(refs),'columnas_diccionario':len(documented),'palabras_aproximadas':len(text.split())},ensure_ascii=False))
