"""Revisión editorial con métricas recalculadas de predicciones ya archivadas.

No entrena modelos ni modifica los insumos ni la versión 6. Ejecutar desde la raíz.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent.parent
DOC=ROOT/'Trabajo escrito'
DATA=ROOT/'Datos_analiticos_proyecto'
OUT=DOC/'Revision_v7';OUT.mkdir(exist_ok=True)
ASSETS=OUT/'Figuras';ASSETS.mkdir(exist_ok=True)
NAME='Documento_LaGaitana_v7_revision_profesor_20261028'
sources={};audit=[];tables={};pending=[]


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def track(path):
    path=Path(path);sources[path.relative_to(ROOT).as_posix()]=digest(path)
    return path


def load(relative,sheet=None):
    path=track(DATA/relative)
    if sheet:return pd.read_excel(path,sheet_name=sheet)
    if path.suffix=='.csv':return pd.read_csv(path)
    return pd.read_parquet(path)


def number(value,decimals=2):
    if value is None or pd.isna(value):return '[PENDIENTE: dato no archivado]'
    return f'{value:,.{decimals}f}'.replace(',','@').replace('.',',').replace('@','.')


def md_table(headers,rows):
    def clean(value):return str(value).replace('|',' / ').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(map(clean,headers))+' |',
                      '| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(map(clean,row))+' |' for row in rows])+'\n'


def score(frame,col,y='y'):
    d=frame.dropna(subset=[y,col]);real=d[y].to_numpy(float);pred=d[col].to_numpy(float)
    assert np.isfinite(real).all() and np.isfinite(pred).all()
    error=pred-real;den=real.sum();positive=real>0
    return dict(n=len(d),MAE=float(np.abs(error).mean()) if len(d) else None,
                RMSE=float(np.sqrt(np.mean(error**2))) if len(d) else None,
                WAPE_pct=float(100*np.abs(error).sum()/den) if den else None,
                sesgo_medio=float(error.mean()) if len(d) else None,
                sesgo_neto=float(error.sum()),sesgo_pct=float(100*error.sum()/den) if den else None,
                real_total=float(den),n_positivos=int(positive.sum()),n_reales_cero=int((real==0).sum()),
                MAPE_pct=float(100*np.mean(np.abs(error[positive])/real[positive])) if positive.any() else None,
                dentro_8_pct=float(100*np.mean(np.abs(error[positive])<=.08*real[positive])) if positive.any() else None)


METRIC_HEADERS=['Método','Casos','MAE (tallos)','RMSE (tallos)','MAPE*','WAPE','Dentro ±8 %*','Sesgo (%)']
def metric_row(label,m):
    return [label,number(m['n'],0),number(m['MAE']),number(m['RMSE']),number(m['MAPE_pct'])+' %',
            number(m['WAPE_pct'])+' %',number(m['dentro_8_pct'])+' %',number(m['sesgo_pct'])+' %']


def register(stage,label,m,frame=None,source='',split='evaluación',**extra):
    row=dict(etapa=stage,modelo=label,particion=split,fuente=source,**m,**extra)
    if frame is not None:
        for col in ['origen','semana_objetivo','fecha']:
            if col in frame:
                row[col+'_desde']=str(frame[col].min())[:10];row[col+'_hasta']=str(frame[col].max())[:10]
    audit.append(row)
    return row


def metric_table(stage,frame,methods,y='y',source='',split='evaluación'):
    rows=[]
    for label,col in methods:
        m=score(frame,col,y);register(stage,label,m,frame,source,split)
        rows.append(metric_row(label,m))
    result=md_table(METRIC_HEADERS,rows)
    tables[stage]=result
    return result


def from_aggregates(stage,d,source):
    rows=[]
    for _,r in d.iterrows():
        m=dict(n=int(r.n),MAE=float(r.MAE),RMSE=float(r.RMSE),WAPE_pct=float(r.WAPE)*100,
               sesgo_medio=float(r.sesgo),sesgo_pct=float(r.sesgo_pct),sesgo_neto=float(r.sesgo*r.n),real_total=None)
        label=str(r.modelo)+' · '+str(r.get('split','evaluación'))
        register(stage,label,m,source=source,split=str(r.get('split','evaluación')))
        rows.append([label,number(m['n'],0),number(m['MAE']),number(m['RMSE']),number(m['WAPE_pct'])+' %',
                     number(m['sesgo_medio']),number(m['sesgo_pct'])+' %'])
    return md_table(['Método / partición','Casos','MAE (tallos)','RMSE (tallos)','WAPE','Sesgo medio (tallos)','Sesgo (%)'],rows)


def subsection(text,start,end,replacement):
    a=text.index(start);b=text.index(end,a)
    return text[:a]+replacement.rstrip()+'\n\n'+text[b:]


def replace_table(text,header,new):
    pattern=re.escape(header)+r'[^\n]*\n(?:\|[^\n]*\n)+'
    text,n=re.subn(pattern,lambda _:new,text,count=1)
    assert n==1,header
    return text


# 1. Paneles históricos: conservar las poblaciones y no mezclar corridas.
base='modelo_con_proyecciones_teoricas/'
f12=load(base+'evaluacion_casos_comunes.parquet')
labels12={
 'Ajuste_media4_sin_planos':'Boosting sobre Media4, sin teoría','Media4':'Media4',
 'Modelo_teorico':'Boosting teórico con memoria y clima','Modelo_teorico_historia':'Boosting teórico con revisiones',
 'Ridge_ajuste_teoria':'Ridge sobre teoría','Teoria_sin_ajuste':'Teoría sin ajuste',
 'Teorico_sin_clima':'Boosting teórico sin clima','Teorico_sin_memoria':'Boosting teórico sin memoria',
 'Ultimo_valor':'Último valor real'}
rows=[]
for name,label in labels12.items():
    g=f12.loc[f12.modelo.eq(name)];m=score(g,'prediccion');assert m['n']==2107
    register('12 · casos comunes',label,m,g,base+'evaluacion_casos_comunes.parquet')
    rows.append(metric_row(label,m))
t12=md_table(METRIC_HEADERS,rows)
fs=load(base+'evaluacion_sistema.parquet')
ts=metric_table('12 · sistema',fs,[('Boosting sobre Media4','pred_previo'),('Teoría aplicable y respaldo','prediccion')],source=base+'evaluacion_sistema.parquet')
f14=load(base+'comparacion_features_diarias_2026.parquet');f14=f14.loc[f14.grupo_comparacion.eq('principal_estricta_nominal')]
t14=metric_table('14 · panel histórico',f14,[('Corrección relativa diaria','Ajuste_relativo_diario'),('Boosting con pérdida absoluta, exploratorio','Boosting_diario_MAE'),('Sistema anterior a señales diarias','Sistema_anterior'),('Boosting con señales diarias','Sistema_diario'),('Ingeniero','ingeniero')],source=base+'comparacion_features_diarias_2026.parquet')
f15=load(base+'experimentos_horizontes_2026.parquet');f15=f15.loc[f15.grupo_comparacion.eq('principal_estricta_nominal')]
t15=metric_table('15 · panel histórico',f15,[('Referencia antes de calidad y clima','Antes_calidad'),('Combinación fijada antes de 2026','Combinacion'),('Memoria larga','Memoria_larga'),('Revisiones de teoría','Revisiones'),('Agrupado H1–H2 / H3–H5','Separado'),('Sistema diario del 14','Sistema_diario'),('Ingeniero','ingeniero')],source=base+'experimentos_horizontes_2026.parquet')
assert len(f14)==len(f15)==15838

# 2. Selección anual y comparación nominal corregida.
review='revision_clima_finca/'
fv=load(review+'validacion_clima_pre2026.parquet')
methods19=[('Boosting sin clima','Sin_clima'),('Clima básico','Clima_basico'),('Clima ampliado y lluvia','Clima_ampliado'),('Clima ampliado y curva atribuida a GAITANA','Curva_Gaitana_clima')]
tv=metric_table('19 · validación 2025',fv,methods19,source=review+'validacion_clima_pre2026.parquet',split='validación de selección')
fa=load(review+'comparacion_clima_curvas_2026.parquet');fa=fa.loc[fa.grupo_comparacion.eq('principal_estricta_nominal')].copy()
assert len(fa)==16325 and np.allclose(fa.Sin_clima,fa.Seleccion_pre2026)
ta=metric_table('19 · anual estricto',fa,methods19+[('Ingeniero','ingeniero')],source=review+'comparacion_clima_curvas_2026.parquet')
annual_rows=[]
for h,g in fa.groupby('horizonte'):
    for label,col in [('Modelo H'+str(int(h)),'Seleccion_pre2026'),('Ingeniero H'+str(int(h)),'ingeniero')]:
        m=score(g,col);register('19 · por horizonte',label,m,g,review+'comparacion_clima_curvas_2026.parquet')
        annual_rows.append(metric_row(label,m))
tah=md_table(METRIC_HEADERS,annual_rows)
cut=load(review+'train_test_clima_por_corte.parquet')
last=cut.loc[cut.corte.eq(pd.Timestamp('2026-08-03'))&cut['split'].isin(['train','test'])&cut.fase.eq('evaluacion_2026')].copy()
ttrain=from_aggregates('19 · ajuste agosto',last,review+'train_test_clima_por_corte.parquet')

# 3. Ensayos recientes: mismo horizonte no significa misma población ni diseño.
exp='experimentos_actualizacion_20261020/'
f21=load(exp+'validacion_semanas_nuevas.parquet')
t21=metric_table('21 · semanas recientes',f21,[('Modelo general del ensayo 21','prediccion'),('Ingeniero','ingeniero')],y='y_eval',source=exp+'validacion_semanas_nuevas.parquet')
f22=load(exp+'predicciones_modelos_horizonte.parquet')
g22=f22.loc[f22.experimento.eq('Agrupado H1-H2/H3-H5')]
h22=f22.loc[~f22.experimento.eq('Agrupado H1-H2/H3-H5')]
t22=metric_table('22 · general',g22,[('Agrupado original del 22','prediccion'),('Ingeniero','ingeniero')],y='y_eval',source=exp+'predicciones_modelos_horizonte.parquet')
t22+=metric_table('22 · cinco ajustes',h22,[('Cinco modelos separados del 22','prediccion')],y='y_eval',source=exp+'predicciones_modelos_horizonte.parquet')
f23=load(exp+'predicciones_n_menos_1.parquet')
t23=''
for variant,g in f23.groupby('variante'):
    t23+='**'+variant+' · sólo se evalúan los productos que permanecen.**\n\n'
    variant_rows=[]
    for method,part in g.groupby('metodo_experimento'):
        m=score(part,'prediccion','y_eval');register('23 · '+variant+' · '+method,method,m,part,exp+'predicciones_n_menos_1.parquet')
        variant_rows.append(metric_row(method,m))
    common=g.loc[g.metodo_experimento.eq('General (mismos casos)')]
    m=score(common,'ingeniero','y_eval');register('23 · '+variant+' · experto','Ingeniero',m,common,exp+'predicciones_n_menos_1.parquet')
    variant_rows.append(metric_row('Ingeniero',m))
    t23+=md_table(METRIC_HEADERS,variant_rows)+'\n'
fg=load(exp+'24_predicciones_agrupado.parquet');fh=load(exp+'24_predicciones_horizontes.parquet')
key=['finca','producto','color','variedad','origen','semana_objetivo','horizonte']
f24=fh.merge(fg[key+['prediccion']].rename(columns={'prediccion':'agrupado'}),on=key,validate='one_to_one')
f24['hibrida']=f24.prediccion.where(f24.horizonte.ne(1),f24.agrupado)
f24['hibrida_cal']=f24.pred_corregida.where(f24.horizonte.ne(1),f24.agrupado)
t24=metric_table('24 · tuning y calibración',f24,[('Agrupado, tuning noviembre','agrupado'),('Separados, tuning noviembre','prediccion'),('Separados y calibración diciembre','pred_corregida'),('H1 agrupado y H2–H5 separados','hibrida'),('H1 agrupado y H2–H5 calibrados','hibrida_cal'),('Ingeniero','ingeniero')],y='y_eval',source=exp+'24_predicciones_horizontes.parquet + 24_predicciones_agrupado.parquet')
f25=load(exp+'25_predicciones_candidato_sin_ingeniero.parquet')
t25=metric_table('25 · candidato final',f25,[('General agrupado','pred_agrupado'),('General separado por H','pred_separado'),('H1 agrupado y H2–H5 separados','pred_hibrida'),('Especializado sin mezcla','pred_especializado'),('Ensamble de modelos propios','pred_candidato'),('Ingeniero','ingeniero')],y='y_eval',source=exp+'25_predicciones_candidato_sin_ingeniero.parquet')
assert len(f21)==len(g22)==len(h22)==len(f24)==len(f25)==1226
recent_rows=[]
for h,g in f25.groupby('horizonte'):
    same=g[key+['y_eval']].merge(f24[key+['y_eval']],on=key,validate='one_to_one',suffixes=('_25','_24'))
    assert len(same)==len(g) and np.allclose(same.y_eval_25,same.y_eval_24)
    for label,col in [('Modelo H'+str(int(h)),'pred_candidato'),('Ingeniero H'+str(int(h)),'ingeniero')]:
        m=score(g,col,'y_eval');register('25 · por horizonte',label,m,g,exp+'25_predicciones_candidato_sin_ingeniero.parquet')
        recent_rows.append(metric_row(label,m))
t25h=md_table(METRIC_HEADERS,recent_rows)
recent_scope=md_table(['Horizonte','Casos','Semanas objetivo representadas'],[
    ['H'+str(int(h)),number(len(g),0),', '.join(pd.Timestamp(v).strftime('%d/%m/%Y') for v in sorted(g.semana_objetivo.unique()))]
    for h,g in f25.groupby('horizonte')])
product_tuning=load(exp+'25_tuning_producto_horizonte_noviembre.csv')
weight_tuning=load(exp+'25_tuning_ensamble_modelos_noviembre.csv')
param_best=product_tuning.sort_values(['WAPE_noviembre_pct','max_iter']).groupby(['producto','horizonte'],as_index=False).first()
weight_col=next(c for c in weight_tuning if c.startswith('WAPE'))
weight_best=weight_tuning.sort_values([weight_col,'peso_modelo_especializado']).groupby(['producto','horizonte'],as_index=False).first()
assert weight_best.groupby('horizonte').peso_modelo_especializado.nunique().eq(1).all()
assert weight_best.groupby('horizonte').peso_modelo_especializado.first().to_dict()=={3:1.0,4:1.0,5:.75}
(OUT/'parametros_especialistas_verificados.csv').write_text(param_best.to_csv(index=False),encoding='utf-8-sig')
(OUT/'pesos_ensamble_verificados.csv').write_text(weight_best.to_csv(index=False),encoding='utf-8-sig')

# 4. Diario: conservar la población común de cada tarea.
daily='modelo_diario/'
fd=load(daily+'predicciones_diarias_clima_2026.parquet')
dm=[('Autónomo anterior al clima','Autonomo_antes_clima'),('Boosting reconciliado, selección semanal','Boosting_clima'),('Boosting autónomo','Boosting_diario'),('Boosting reconciliado, memoria semanal','Boosting_memoria'),('Perfil histórico, selección semanal','Perfil_clima'),('Perfil histórico, memoria semanal','Perfil_memoria'),('Reconciliado anterior al clima','Reconciliado_antes_clima'),('Uniforme, selección semanal','Uniforme_clima'),('Uniforme, memoria semanal','Uniforme_memoria')]
dc=fd.dropna(subset=['tallos']+[c for _,c in dm]);assert len(dc)==22973
td=metric_table('Diario 05 · días comunes',dc,dm,y='tallos',source=daily+'predicciones_diarias_clima_2026.parquet')
sar=load(daily+'piloto_sarima_clima.parquet')
sm=[('Boosting reconciliado','Boosting_clima'),('Boosting autónomo','Boosting_diario'),('Perfil histórico','Perfil_clima'),('SARIMA','SARIMA'),('SARIMAX','SARIMAX'),('SARIMAX reconciliado','SARIMAX_clima'),('SARIMA reconciliado','SARIMA_clima'),('Semana anterior','Semana_anterior'),('Uniforme','Uniforme_clima')]
sc=sar.dropna(subset=['tallos']+[c for _,c in sm]);assert len(sc)==135
tsar=metric_table('Diario 03–05 · piloto',sc,sm,y='tallos',source=daily+'piloto_sarima_clima.parquet')
dtrain=load(daily+'resultados_diarios_clima.xlsx',sheet='Train_test_ultimo_ajuste')
tdtrain=from_aggregates('Diario 05 · ajuste agosto',dtrain,daily+'resultados_diarios_clima.xlsx / Train_test_ultimo_ajuste')
rnn=load(exp+'predicciones_rnn_diaria.parquet')
rm=[('LSTM sin clima / modo automático','RNN_auto'),('LSTM con clima, diagnóstico','RNN_con_clima'),('Último valor disponible','ultimo_valor'),('Media de siete días observados','media7_observada'),('Mismo día, 364 días atrás','mismo_dia_anio_anterior')]
trnn=metric_table('Diario 06 · soporte propio',rnn,rm,source=exp+'predicciones_rnn_diaria.parquet')
rc=rnn.dropna(subset=['y']+[c for _,c in rm])
trnn_common=metric_table('Diario 06 · soporte común',rc,rm,source=exp+'predicciones_rnn_diaria.parquet')
track(ROOT/'Notebooks/Modelo_de_series_diario/06_RNN_profunda_produccion_diaria.ipynb')

# 5. Revisión del texto conservando resultados y fuentes anteriores.
source_text=track(DOC/'Desarrollo_del_documento.md').read_text(encoding='utf-8')
track(DOC/'Documento_LaGaitana_v6.docx')
text=source_text.replace('**Borrador integrado para revisión académica — octubre de 2026**',
 '**Versión 7 para revisión académica — 28 de octubre de 2026**\n\nEsta edición reorganiza el argumento y completa indicadores a partir de predicciones archivadas; no reentrena modelos. Distingue los paneles históricos, el benchmark anual nominal actualizado y los ensayos recientes. Las nuevas cargas del prototipo no se presentan como una nueva validación de la tesis.')
from docx import Document as WordDocument
plan_path=track(ROOT/'Plan de Proyecto/Plan de proyecto_final.docx')
plan_paragraphs=[p.text.strip() for p in WordDocument(plan_path).paragraphs]
og=plan_paragraphs[plan_paragraphs.index('2.1 Objetivo general')+1]
specific_start=plan_paragraphs.index('2.2 Objetivos específicos')+1
specific_end=plan_paragraphs.index('2.3 Alcance de la decisión')
specific=[p for p in plan_paragraphs[specific_start:specific_end] if p]
assert len(specific)==4
objectives="### 1.1. Objetivos del Plan de proyecto y resultados que deben responderlos\n\n"
objectives+="Se retoman literalmente el objetivo general y los cuatro objetivos específicos de Plan de proyecto_final.docx, sección 2.1–2.2. Los resultados y las conclusiones distinguen el desarrollo realizado de la validación organizacional aún pendiente. [E22]\n\n"
objectives+="**Objetivo general (OG).** "+og+"\n\n"
objectives+='\n\n'.join(f'**OE{i}.** {value}' for i,value in enumerate(specific,1))+'\n\n'
objectives+=md_table(['Objetivo','Evidencia y alcance de respuesta'],[
 ['OE1 · Proceso y base histórica','Fuentes, pilotos, curvas, proyecciones, EDA y base analítica; 2–4.1. Conclusión 7.2.'],
 ['OE2 · Desarrollo y comparación de modelos','Modelos semanales y pilotos diarios, métricas y banda ±8 %; 4.2–5.6. Conclusión 7.3. El diario continúa en revisión.'],
 ['OE3 · Salida y señales operativas','Prototipo de consulta, comparación, ajuste y publicación; 4.3.2 y 6.3. Conclusión 7.4. Semáforos de faltante/sobrante sin validación empresarial.'],
 ['OE4 · Validación en entorno operativo','Comparación retrospectiva y protocolo propuesto; 4.3.1 y 6.3. Conclusión 7.5. Piloto e impacto organizacional pendientes.']])
objectives+="\nLa integración del estimado del ingeniero se utiliza como referencia de evaluación y consulta, no como predictor del candidato autónomo. El Plan pide producción exportable y resolución diaria/semanal; esta revisión no da esos alcances por cumplidos sólo por mejorar el error semanal sobre tallos reportados.\n\n"
objectives+="El relato sigue el proceso que hace verificables esos objetivos: establecer el significado de cada fuente, construir referencias por edad, comparar correcciones con información pasada y valorar su uso y sus límites para la organización.\n\n"
text=subsection(text,'### 1.1. Objetivo y preguntas de trabajo','### 1.2.',objectives)
text=text.replace('Primero se examina si los registros se pueden unir sin mezclar ciclos ni duplicar cantidades. Después se reconstruyen curvas y proyecciones con cobertura explícita.',
 'Primero se examina si los registros se pueden unir sin mezclar ciclos ni duplicar cantidades. Después se reconstruyen curvas por edad y proyecciones, distinguiendo cuándo pueden representar todo el inventario del plano.')
text=text.replace('### 3.4. Qué muestran los cinco últimos planos','### 3.4. Qué muestran cinco planos del corte analítico')
text=text.replace('Los cinco últimos planos seleccionados corresponden','Los cinco planos comparados en el corte analítico original corresponden')
text=text.replace('No se valida rellenar ambos grupos con cero. No se rellenan esos grupos con cero sin una regla de negocio confirmada.', 'No se completan esos grupos con cero sin una regla agronómica confirmada.')
coverage_start='La producción real observada se conserva en los 211.001 casos analizados.'
if coverage_start in text:
 a=text.index(coverage_start);b=text.index('\n\n',a)
 text=text[:a]+'''La producción real se conserva en el panel observado. La teoría sólo actúa como referencia de un total cuando las edades de todos los grupos del plano están representadas; en los demás casos admisibles se corrige la producción reciente. Es una decisión de uso de la curva, no un porcentaje de producción perdida ni una tasa de fallas del cruce de camas. [E3–E4]'''+text[b:]

def insert_before(marker,addition):
 global text
 assert marker in text
 text=text.replace(marker,addition.rstrip()+'\n\n'+marker,1)

insert_before('## 3. Análisis exploratorio', '''### 2.4. Decisiones y límites al interpretar las fuentes

Se eligió trabajar con tallos reportados y mantener GAITANA separada de ARABELLA y de GAITANA PPTO. Los movimientos se agregan sólo después de homologar la identidad y verificar la fecha; la repetición de historia en ediciones anuales no representa nuevos cortes. La conservación de cantidades valida la transformación de la fuente, no certifica por sí sola su exactitud agronómica ni su equivalencia con producción exportable.

Las fechas de los archivos y su contenido permiten reconstruir una disponibilidad nominal; no siempre acreditan cuándo se publicó o corrigió cada dato. Por eso los resultados son retrospectivos y condicionados a esa reconstrucción. [PENDIENTE: confirmar con la empresa la equivalencia entre tallos reportados y exportables, y documentar el calendario de publicación/corrección de cada fuente.]''')
insert_before('### 3.3.', '''### 3.2.1. Decisiones y límites de la curva construida

La ventana de 78 semanas, el promedio de rendimientos por observación y el ajuste de extremos de 1,5 rangos intercuartílicos son reglas adoptadas, no parámetros demostrados como óptimos. Cada observación piloto pesa igual aunque cambie el número de plantas. La curva compartida supone que esas observaciones informan sobre las cohortes a las que se aplica; su representatividad espacial, estacional y de manejo no fue validada agronómicamente. No se extrapolan edades ni se convierten ausencias en cero.

La regla que exige representar todas las edades evita presentar una suma parcial como total. Su consecuencia es usar una corrección de producción reciente en parte del inventario, aun cuando los registros reales y las identidades comerciales estén conservados. [PENDIENTE: validación agronómica de edades improductivas y sensibilidad a ventana, ponderación por plantas y tratamiento de extremos.]''')
insert_before('## 4. Diseño del sistema', '''El EDA dejó así una secuencia de decisiones, no una lista de variables elegidas por correlación: respetar el calendario y las identidades, conservar las revisiones de teoría, probar memoria productiva y contrastar el clima sin atribuirle causalidad. El siguiente capítulo convierte esas hipótesis en candidatos comparables y fija cómo se evaluarán antes de discutir sus resultados.''')
insert_before('### 4.2. Metodología', '''### 4.1.2. Supuestos y límites de la base de pronóstico

Se mantienen separados origen, objetivo y horizonte. Una misma semana producida aparece en varios casos de pronóstico, por lo que sumar el objetivo sobre toda la base repetiría volumen. Las variables se calculan con fechas anteriores al origen; el objetivo observado no se imputa y la imputación de predictores usa sólo el entrenamiento. La prueba de perturbación del futuro comprueba el cálculo de las variables, pero no certifica que el archivo histórico hubiera estado publicado sin correcciones en aquel momento.

Los casos sin historia suficiente no entran en el aprendizaje. La ruta por teoría depende de las edades del plano; la ruta por producción reciente depende de su historia observada. Son condiciones diferentes y ninguna autoriza a interpretar una celda vacía como cero. La base de 621.195 filas descrita aquí corresponde a la edición analítica documentada; no se sustituye por los conteos posteriores del prototipo sin repetir y versionar la evaluación.''')
text=text.replace('La ruta de Media4 recibe producto, color, variedad, horizonte y calendario, nueve variables de memoria semanal, 28 resúmenes diarios de producción/clima ya observados y siete señales de memoria larga.',
 'La ruta de Media4 recibe producto, color, variedad, horizonte y calendario, nueve variables de memoria semanal y siete señales de memoria larga. El bloque diario inicial tiene 28 columnas: al retirar las nueve climáticas, la variante seleccionada conserva 19 señales diarias de producción.')
text=replace_table(text,'| Método | Casos | MAE (tallos) | WAPE | Sesgo (%) |',tv)
insert_before('### 4.3. Comparación', '''### 4.2.7. Decisiones y límites de los ajustes semanales

Se aprendió una corrección en tallos y se restringió la predicción final a valores no negativos. Los modelos comparten información entre series mediante identidad comercial; ello facilita aprender con historias desiguales, pero no certifica igual desempeño para variedades nuevas o de bajo volumen. Las ablaciones del 12 mantienen casos comunes; los contrastes de 14 añaden producción y clima diarios conjuntamente, y la referencia anterior a calidad del 15 también conserva otra versión climática. Por tanto, no todas las diferencias aíslan un único cambio.

El 19 se elige en noviembre–diciembre de 2025 y se actualiza mensualmente, con objetivos cerrados antes del corte. Los ensayos recientes 21–25 no son una réplica exacta: reentrenan por origen, usan memoria semanal y hasta seis variables de teoría/revisiones, no los mismos bloques diario y de memoria larga del 19, y limitan el ajuste a una muestra de hasta 5.000 registros pasados por grupo con semilla 42. El número de registros elegibles de sus controles no equivale necesariamente al número efectivamente usado al ajustar. Esta diferencia impide atribuir una mejora sólo a separar horizontes o productos.

En 24 se comparan 40 y 80 iteraciones con 15 hojas en noviembre de 2025; diciembre estima un factor de volumen por horizonte. En 25 se seleccionan parámetros y pesos de especialistas con noviembre. Son búsquedas acotadas, no una optimización exhaustiva. Las ventanas ya fueron examinadas durante desarrollo: hace falta un período nuevo para estimar generalización. [PENDIENTE: evaluación prospectiva de la configuración congelada y análisis de estabilidad de selección entre varias ventanas temporales.]''')
text=text.replace('Ridge sirve de contraste lineal regularizado.',
 'Ridge sirve de contraste lineal regularizado: en 12 se fija alpha = 100, con estandarización de entradas numéricas después de imputación por mediana e indicadores de faltante; las categorías usan one-hot. Estos pasos se ajustan sólo con train. No se realizó una búsqueda exhaustiva de alpha.')
text=text.replace('El modelo diario autónomo aprende el corte de cada día con historia de producción, clima pasado y calendario, sin recibir el pronóstico semanal actual.',
 'El modelo diario autónomo se reentrena por mes con hasta 104 semanas previas y semanas de entrenamiento cerradas. Usa HistGradientBoosting con 80 iteraciones, 15 hojas, tasa 0,08, mínimo 40 casos por hoja, L2 de 1 y semilla 42. Aprende la diferencia entre log(1 + tallos del día) y log(1 + Media4/7), con identidad, calendario del día y señales productivas/climáticas pasadas. Invierte esa transformación y restringe el resultado a no negativo; no recibe el pronóstico semanal actual. El reparto por boosting pondera ese volumen por la frecuencia de reporte suavizada de las ocho semanas previas, (reportes + 0,5)/(días + 1), y normaliza siete pesos; si su suma no es positiva, usa el perfil histórico.')
old='Se informa MAE en tallos, RMSE, WAPE y sesgo, con cortes por horizonte y segmento.'
a=text.index(old);b=text.index('\n\n',a)
text=text[:a]+'''Las métricas se recalculan desde las predicciones archivadas y los objetivos de cada panel, por caso antes de agregar por horizonte o segmento. Se conservan MAE, RMSE, WAPE, sesgo medio en tallos y sesgo porcentual; en esta versión todas las tablas de modelos usan el signo predicción menos real. El anexo técnico conserva también el saldo neto en tallos y la fuente de cada cálculo. Los registros agregados train/test se toman de sus salidas guardadas y se identifican por corte, sin reentrenar. No se promedian los porcentajes de subgrupos para obtener el total. El remuestreo por semana objetivo se mantiene como exploratorio y no transforma los períodos revisados en una prueba prospectiva intacta.'''+text[b:]
text=text.replace('Se conservan MAE, RMSE, WAPE, sesgo medio en tallos y sesgo porcentual;',
 'Se informan MAE, RMSE, MAPE, WAPE/WMAPE, porcentaje dentro de ±8 % y sesgo porcentual, conservando sesgo medio y saldo neto en la auditoría;')
text=text.replace('Los registros agregados train/test se toman de sus salidas guardadas',
 'El WMAPE referido en el Plan se reporta como WAPE con ponderación por volumen. Los indicadores marcados con asterisco (MAPE y dentro de ±8 %) se calculan sólo para reales positivos; sus conteos positivos y ceros se conservan por método en la auditoría, sin imputar un denominador. La banda ±8 % es la referencia inicial del Plan, todavía sujeta a validación empresarial, no un intervalo de incertidumbre. Los registros agregados train/test se toman de sus salidas guardadas')
insert_before('### 4.4. Metodología', '''### 4.3.1. Límite de la comparación con el ingeniero

La primera semana del nombre del archivo define H1; la semana en curso que pueda permanecer en la tabla no cambia ese horizonte. Los casos con archivo posterior al origen o identidad recuperada se separan del panel principal. Se compara la misma combinación comercial, origen nominal, semana objetivo y horizonte, evitando atribuir a un método un caso que el otro no tiene.

Ese emparejamiento no garantiza igualdad del momento de información: el ingeniero envía el jueves anterior y las variables de la simulación semanal utilizan el pasado disponible antes del lunes. Los días intermedios pueden favorecer al modelo. La ventaja observada justifica ensayar su uso, pero no demuestra superioridad con idéntico conjunto informativo ni el reemplazo inmediato del juicio experto. [PENDIENTE: repetir la comparación congelando insumos al jueves de emisión, o acordar una emisión común para ambos métodos y conservar sus marcas de tiempo.]''')
insert_before('### 4.4. Metodología', '''### 4.3.2. Qué parte de la salida analítica está implementada

La salida disponible presenta cantidades originales y ajustadas, contexto temporal, WAPE y sesgo históricos, y permite revisar error por producto, color y variedad. El prototipo conserva generación, ajuste y publicación separados, con trazabilidad de versiones. Esto permite consultar una sugerencia y revisarla, pero no certifica todavía una regla empresarial de decisión. [E21]

Los avisos de actualización de fuentes y los diagnósticos de error retrospectivo no son los semáforos de faltante, normalidad y sobrante previstos en OE3. Para esos semáforos hace falta acordar contra qué referencia comercial se clasifica la predicción y qué acciones corresponden. No se puede usar producción real futura para simular una alerta emitida antes del corte. El umbral ±8 % del Plan sirve aquí para evaluar predicciones ya observadas, no para atribuir una decisión operativa validada.''')
insert_before('## 5. Resultados:', '''### 4.4.1. Supuestos y límites del piloto diario

Los repartos usan pesos no negativos normalizados sobre siete días y conservan el total semanal pronosticado; no corrigen por sí solos un error en ese total. La evaluación se restringe a días con reporte, de modo que no estima todavía el error de todos los días físicos de corte. La frecuencia de registro puede reflejar manejo administrativo. Comparar sólo semanas con siete reportes cambia la población y no permite decidir de antemano qué método emitir.

SARIMA/SARIMAX usan órdenes fijos y tres series seleccionadas por volumen previo; sólo los ajustes convergentes aportan predicciones, y el panel común se reduce a 135 días. La comparación climática usa exógenas rezagadas, no un pronóstico meteorológico. Su resultado no se extrapola a toda la finca ni se compara directamente con el panel diario de 22.973 casos.

### 4.4.2. Extensión LSTM: otra tarea diaria, todavía exploratoria

El cuaderno diario 06 ensaya una LSTM de dos capas de 48 unidades, dropout 0,15 y una salida con capa intermedia de 24 unidades. Recibe secuencias de 28 días, máscaras de observación, calendario cíclico e historia desplazada 364 días; el objetivo se transforma en log(1 + producción/escala), con escala mediana positiva calculada con los registros anteriores a julio de 2026, incluidos los de 2024 disponibles para esa normalización. La estandarización de entradas sí usa el subconjunto train. Se ajusta con Adam (tasa 0,001 y regularización 0,00001), MSE, lotes de 512, recorte de gradiente 1 y hasta 12 épocas, con paciencia de tres épocas. Los objetivos train abarcan desde enero de 2025 hasta antes de julio de 2026; validación, julio–agosto; test, septiembre. Si hay más de 25.000 ejemplos train, se muestrean 25.000 con semilla 42. [E20]

La ventana de entrada se actualiza antes de cada día objetivo con registros diarios reales: es un ensayo de un día adelante, no siete días emitidos simultáneamente al lunes. El modo climático exige al menos 80 % de disponibilidad y un atraso máximo de siete días; la salida archivada utiliza sin clima y conserva con clima como diagnóstico. Los faltantes entran con máscara y no se convierten en producción real cero al evaluar. No se reconcilia este ensayo con el total semanal.

La admisibilidad por cantidad de reportes se revisa sobre la historia completa construida, lo cual puede condicionar retrospectivamente qué series entran. [PENDIENTE: auditar esa selección usando sólo el período previo al corte, guardar predicciones train y validación en tallos y evaluar siete días desde un origen común antes de comparar la LSTM con el reparto semanal.]''')

# Completar las tablas existentes sin sustituir sus paneles históricos.
text=replace_table(text,'| Modelo y referencia | Casos | WAPE |',t12)
text=replace_table(text,'| Sistema y referencia | Casos | WAPE |',ts)
text=replace_table(text,'| Experimento 14 | Casos | WAPE |',t14)
text=replace_table(text,'| Experimento 15 | Casos | WAPE |',t15)
insert_before('### 5.1.1.', '''**Contraste anual completo de las variantes del 19.** Se recalcula sobre los 16.325 casos nominales corregidos, en lugar de reutilizar el Resumen anterior del Excel que conservaba 15.838. La elección sigue siendo la fijada con validación 2025; el menor error de una alternativa en 2026 no cambia esa selección.

'''+ta+'\n**Detalle técnico del seleccionado y del ingeniero, por horizonte.**\n\n'+tah)
insert_before('### 5.2.', '''### 5.1.2. Qué cambió en las semanas recientes y qué no puede concluirse

La ventana reciente contiene tres semanas objetivo en total, pero su representación no es igual por horizonte. H1 se evalúa en una sola semana objetivo; no son tres réplicas de su mejora. Las fechas y cantidades efectivas son:

'''+recent_scope+'''
Se conserva el orden de trabajo. El 21 comprueba un modelo general sobre las nuevas semanas; el 22 compara agrupación y separación por horizonte; el 23 retira productos tanto del entrenamiento como del panel evaluado; el 24 incorpora selección de iteraciones y calibración de sesgo anteriores; el 25 especializa dos productos para H3–H5 y mezcla sólo predicciones propias. La tabla siguiente hace visible el resultado de cada paso, sin trasladar el panel de uno al otro.

**Cuaderno 21: comprobación reciente.**

'''+t21+'\n**Cuaderno 22: separación de horizontes.**\n\n'+t22+'''
**Cuaderno 23: experimento n−1.** El producto retirado también se excluye del test. No se está pronosticando un producto desconocido ni se demuestra mejora para miniclavel al dejar de evaluarlo. Sólo se compara si retirarlo del entrenamiento mejora los productos restantes, contra el general en esos mismos casos.

'''+t23+'\n**Cuaderno 24: tuning y calibración.**\n\n'+t24+'\n**Cuaderno 25: especialización y mezcla final.**\n\n'+t25+'\n**Cuaderno 25 por horizonte, con todas las métricas.**\n\n'+t25h+'''
La calibración multiplicativa aprendida en diciembre no mejoró el conjunto reciente; la mezcla de especialistas redujo modestamente el error del candidato previo, pero no superó al ingeniero en H3–H5 ni en el total. Cambian entrenamiento, variables y semanas representadas frente al ensayo anual. Son resultados de desarrollo, con pocos objetivos recientes; no se presenta su diferencia como una mejora estable ni como una prueba prospectiva independiente.''')
text=replace_table(text,'| Método | Casos | MAE (tallos) | WAPE | Sesgo (%) |',td)
text=replace_table(text,'| Método | Casos | MAE (tallos) | WAPE | Sesgo (%) |',tsar)
insert_before('### 5.4. Interpretación', '''### 5.3.1. Resultado de la LSTM diaria: mantener la comparación en su escala

(En revisión: prueba de un día adelante, distinta del reparto semanal.)

Cada referencia se informa primero en su soporte disponible. No se rellenan sus pronósticos ausentes para aumentar artificialmente el tamaño del test.

'''+trnn+'''
Para compararlas en idénticos días se conserva también la intersección de todos los métodos:

'''+trnn_common+'''
Estos resultados no se incorporan al ranking de los modelos que emiten siete días desde el lunes. La LSTM recibe información diaria más reciente y se evalúa en otras fechas y series. El archivo no conserva predicciones train y validación en la escala final de tallos; el valor de MSE transformado usado para parar no sustituye MAE/RMSE/WAPE en tallos. [PENDIENTE: archivar esas predicciones y sus métricas, y reconciliar un pronóstico de siete pasos con el total semanal en una evaluación temporal nueva.]''')
mr=score(rc,'RNN_auto');mb=score(rc,'media7_observada')
text=text.replace('Estos resultados no se incorporan al ranking',
 f"En los {number(len(rc),0)} días comunes, la LSTM sin clima obtiene WAPE de {number(mr['WAPE_pct'])} %, MAE de {number(mr['MAE'])} y RMSE de {number(mr['RMSE'])} tallos, frente a {number(mb['WAPE_pct'])} % de WAPE de la media de siete días. La mejora en este ensayo es acotada a esa tarea de un día adelante.\n\nEstos resultados no se incorporan al ranking",1)
text=replace_table(text,'| Modelo semanal | WAPE train | WAPE test mismo corte | Casos train | Casos test |',ttrain)
text=replace_table(text,'| Modelo diario | WAPE train | WAPE test mismo corte | Casos train | Casos test |',tdtrain)
text=text.replace('Aquí se compara train con test del corte del 3 de agosto de 2026 para las mismas configuraciones;',
 'Aquí se compara train con test del corte del 3 de agosto de 2026 para las mismas configuraciones; el test mensual incluye todos sus casos evaluables, no sólo los emparejados con el ingeniero;')
insert_before('### 5.6.', '''[PENDIENTE: completar MAPE y porcentaje dentro de ±8 % de los agregados de entrenamiento y de cada corte de evaluación donde no se archivaron predicciones individuales suficientes; no se reconstruyen esos indicadores a partir de MAE/RMSE ni se sustituyen por el test. Las tablas de evaluación con predicciones individuales sí incorporan ambos indicadores.]''')

# Corregir el EDA textual que aún conservaba segmentos del panel anterior.
def error_group_table(frame,columns,limit=None):
    den=frame.y.sum();rows=[]
    for keyvalue,g in frame.groupby(columns):
        keyvalue=keyvalue if isinstance(keyvalue,tuple) else (keyvalue,)
        a=score(g,'Seleccion_pre2026');b=score(g,'ingeniero')
        rows.append([' / '.join(map(str,keyvalue)),len(g),a['WAPE_pct'],b['WAPE_pct'],
                    a['MAE']*len(g)/den*100,b['MAE']*len(g)/den*100,a['sesgo_pct'],b['sesgo_pct']])
    rows.sort(key=lambda row:-row[4])
    if limit:rows=rows[:limit]
    return md_table(['Grupo','Casos','WAPE modelo','WAPE ingeniero','Aporte modelo (pp)','Aporte ingeniero (pp)','Sesgo modelo','Sesgo ingeniero'],
        [[r[0],number(r[1],0),number(r[2])+' %',number(r[3])+' %',number(r[4]),number(r[5]),number(r[6])+' %',number(r[7])+' %'] for r in rows])

error_text='''### 5.6. De dónde proviene el error: del producto a las semanas críticas

El diagnóstico se reconstruye con los mismos 16.325 casos nominales del seleccionado anual. La versión anterior del texto mantenía algunos segmentos con 15.838; aquí las cantidades y porcentajes se sincronizan. El aporte en puntos del WAPE divide el error absoluto del grupo por el volumen real de todo el panel, calculando el error por caso antes de agrupar. No se cambia el modelo a partir de este examen. [E18]

'''
for title,g in [('H1',fa.loc[fa.horizonte.eq(1)]),('H1–H5',fa)]:
    error_text+='**'+title+' · productos.**\n\n'+error_group_table(g,['producto'])+'\n'
    error_text+='**'+title+' · cinco colores con mayor aporte del modelo.**\n\n'+error_group_table(g,['producto','color'],5)+'\n'
    error_text+='**'+title+' · cinco variedades con mayor aporte del modelo.**\n\n'+error_group_table(g,['producto','color','variedad'],5)+'\n'
error_text+='''El volumen de miniclavel hace que concentre buena parte del error absoluto; eso no significa que tenga el mayor WAPE relativo. Clavel presenta dificultades especialmente en anticipaciones largas. Los focos UCHUVA, EPSILON y ACADEMY se conservan como episodios para revisar con operaciones, sin atribuirles causas agronómicas no comprobadas.

![Aporte de los productos al WAPE en el panel nominal actualizado. Fuente: E16 y E18.](Revision_v7/Figuras/error_aporte_productos_v7.png)

![Diferencia de WAPE entre modelo e ingeniero por producto y horizonte, panel nominal actualizado. Fuente: E16 y E18.](Revision_v7/Figuras/error_producto_horizonte_v7.png)

![Trayectorias de UCHUVA, EPSILON y ACADEMY en H1, sobre casos emparejados nominalmente. Fuente: E16 y E18.](Revision_v7/Figuras/error_variedades_foco_v7.png)

El detalle se calcula después de observar el test: orienta hipótesis, no valida un modelo especializado ni permite corregir el pronóstico usando su error ya conocido. Las trayectorias sólo muestran observaciones emparejadas; un espacio no acredita ausencia de producción. La concentración por variedad también depende del volumen y del calendario de registro. [PENDIENTE: contrastar los episodios con siembras, manejo, corte y despacho, y probar cualquier cambio en semanas nuevas.]

Esta desagregación cierra el recorrido técnico: ya no basta con saber que el total mejora; ahora puede identificarse en qué anticipaciones y segmentos persisten los errores. La discusión siguiente traduce esa evidencia en posibilidades para la organización, manteniendo sus límites.
'''
text=subsection(text,'### 5.6.','## 6. Discusión',error_text)

discussion='''## 6. Discusión: qué cambia para La Gaitana y bajo qué condiciones

El resultado principal es una cadena trazable que convierte inventarios y rendimientos piloto en referencias teóricas, las contrasta con producción reciente y emite una corrección semanal. La mejora no surge de considerar la curva una verdad agronómica: surge de tratarla como una referencia empírica y mantener una ruta productiva cuando no puede representar todo el plano. Para la empresa, esto facilita revisar por qué un pronóstico usa teoría o historia y rastrear qué archivo y combinación comercial lo originaron.

### 6.1. Implicaciones para la planeación y la revisión del estimado

La selección anual mejora el WAPE y reduce la subestimación neta frente al ingeniero en H1–H2; allí tiene sentido comenzar una revisión asistida de disponibilidad cercana por producto, color y variedad. En H3–H5 el ingeniero conserva menor WAPE, de modo que la evidencia no respalda reemplazar su estimado en todos los horizontes. Un sesgo menor puede evitar una subestimación persistente del total, pero no elimina los errores locales ni garantiza cumplimiento por variedad.

El diagnóstico por producto permite concentrar la revisión en los grupos que más tallos de error aportan, en vez de priorizar únicamente porcentajes extremos de bajo volumen. La especialización por producto es una hipótesis razonable para las anticipaciones largas, pero el experimento reciente sólo mejora modestamente un candidato propio y no supera al ingeniero en conjunto. No se justifican promesas de ahorro, ventas adicionales, reducción de compras o mejora de servicio: esos efectos no se midieron.

### 6.2. Qué se aprendió del clima y de la resolución diaria

No conservar clima en el seleccionado significa que, bajo estas variables y la validación utilizada, no fue necesario para elegir el mejor candidato previo a 2026. No demuestra que temperatura, radiación o lluvia carezcan de efectos en el cultivo. La medición de estación, los umbrales de disponibilidad, la memoria productiva que puede resumir efectos previos y la ventana temporal limitan esa interpretación.

El componente diario aporta una pregunta diferente: cómo se distribuye el volumen a lo largo de la semana. Un reparto aprendido conserva el total semanal y mejora la referencia uniforme en los días reportados, pero hereda errores del pronóstico semanal. El autónomo puede tener menor error diario sin conservar ese total. La LSTM de un día adelante utiliza otra disponibilidad de información; no constituye aún una mejora validada del proceso semanal a diario.

### 6.3. Transferencia operativa sin confundirla con nueva evidencia predictiva

El prototipo posterior separa recepción, limpieza, generación, ajuste y publicación; conserva versiones y permite comparar WAPE, sesgo y segmentos de error. Esta organización ofrece una vía de uso y auditoría, no una medición de adopción empresarial. El adaptador del 19 reprodujo 584 casos de un origen con diferencia máxima cero; la comprobación es parcial, no certifica toda la historia ni una emisión del jueves. [E21]

La organización deberá fijar quién publica, con qué insumos y con qué criterio se acepta un ajuste. Una evaluación prospectiva debe conservar el pronóstico original y el ajustado antes de conocer los cortes reales. [PENDIENTE: acordar el piloto empresarial, registrar disponibilidad al jueves y medir servicio, ajustes y costos con responsables de operación.]

Estos límites no se agregan sólo al cierre: las secciones anteriores muestran qué decisiones los originan en fuentes, curvas, calendario, aprendizaje, benchmark y resolución diaria. Las conclusiones responden a los objetivos dentro de ese alcance, y la continuidad se propone para las comprobaciones que todavía faltan.
'''
text=subsection(text,'## 6. Discusión','## 7. Conclusiones',discussion)
conclusions='## 7. Conclusiones vinculadas con los objetivos del Plan de proyecto\n\n### 7.1. Respuesta al objetivo general: desarrollo logrado y alcance aún parcial\n\nSe desarrolló y comparó retrospectivamente un sistema semanal por combinación comercial para GAITANA, junto con pilotos diarios. El seleccionado es HistGradientBoosting sin clima del cuaderno 19, con grupos H1–H2/H3–H5 y corrección de teoría o Media4. En 16.325 casos obtuvo WAPE de 19,36 % frente a 19,71 % del ingeniero y sesgo de −2,36 % frente a −9,81 %. Estos resultados responden al componente predictivo del objetivo general; no acreditan todavía todo su alcance de producción exportable diaria/semanal ni una reducción de incertidumbre medida en ventas, compras o poscosecha. Para La Gaitana, aportan una propuesta trazable para revisar disponibilidad cercana, condicionada a confirmar la variable exportable, igualar el momento informativo y evaluar el uso real.\n\n### 7.2. Respuesta a OE1: proceso de estimación y base histórica\n\nSe caracterizaron inventario de plantas, rendimiento piloto, movimientos reales, clima y versiones del estimado; se homologaron identidades y ciclos sin eliminar movimientos legítimos. La edición analítica conserva 621.195 filas y 47 columnas, y la auditoría de cortes de 2026 logró correspondencia única en 32.986 de 33.039 observaciones piloto (99,84 %). Se reconstruyeron rendimientos por planta y edad con 78 semanas previas y diez semanas de proyección por plano, y se alinearon planos 29–33 sobre objetivos comunes. La caracterización y consolidación están documentadas; las nuevas bases operativas no se confunden con esa edición analítica.\n\nPara la organización, esta base permite reconstruir un estimado, localizar excepciones y distinguir revisiones del inventario de cambios reales en el corte. No certifica por sí sola la exactitud agronómica. Siguen pendientes la equivalencia reportado/exportable, las fechas históricas de publicación y la validación de edades improductivas; las edades no representadas no se completan automáticamente con cero.\n\n### 7.3. Respuesta a OE2: modelos comparados y rendimiento técnico\n\nSe compararon referencias simples, Ridge, variantes de boosting, SARIMA/SARIMAX y una LSTM exploratoria. Las tablas recalculan MAE, RMSE, MAPE, WAPE/WMAPE, sesgo y proporción dentro de ±8 % donde existen predicciones individuales. En los agregados de entrenamiento que no conservan esos casos, MAPE y la proporción se dejan pendientes, sin trasladarles resultados del test. La banda es una referencia inicial del Plan, no un nivel de servicio aprobado por la empresa.\n\nEl seleccionado anual mejora H1 (15,53 % frente a 16,93 %) y H2 (17,49 % frente a 19,16 %); el ingeniero conserva menor WAPE en H3–H5. Retirar memoria elevó el WAPE de 19,31 % a 23,26 % en los 2.107 casos del contraste inicial. Sin clima ganó la selección previa a 2026 (21,70 % frente a 21,91 % con clima básico); ello respalda su uso bajo este diseño, no la ausencia de efectos climáticos en la fisiología.\n\nEl ensayo reciente del 25 redujo el WAPE de un candidato propio de 17,80 % a 17,53 %, pero el ingeniero obtuvo 16,34 %. H1 favoreció al candidato (12,28 % frente a 15,23 %), sobre una sola semana objetivo; H2 fue empate práctico (14,96 % frente a 14,98 %). En el diario, el reparto aprendido obtuvo 27,26 % frente a 28,80 % del uniforme en 22.973 días reportados; el autónomo obtuvo 26,72 %, sin garantizar coherencia semanal. SARIMAX usa sólo 135 días comunes y la LSTM es de un día adelante. El objetivo de comparar modelos tiene evidencia, pero la solución diaria consolidada continúa en revisión.\n\nPara La Gaitana, estas comparaciones sustentan priorizar la revisión de H1–H2 y concentrar mejoras en H3–H5 y en los segmentos de mayor error en tallos. No justifican escoger un modelo sólo por un promedio global ni reemplazar el criterio experto para toda anticipación.\n\n### 7.4. Respuesta a OE3: salida analítica y señales para decidir\n\nEl prototipo ofrece consulta histórica, comparación por semana/producto/color/variedad, generación, ajuste y publicación versionada. El diagnóstico permite localizar dónde se concentra el error y conservar la sugerencia original al revisar un estimado. Esto cubre una parte de la salida analítica planteada en OE3 y ofrece soporte para la revisión operativa.\n\nNo se acredita todavía un semáforo empresarial validado de faltante, normalidad o sobrante por variedad-color. Los indicadores retrospectivos de error y los avisos de actualización de fuentes no equivalen a esas señales: para anticiparlas se requiere una referencia comercial o de disponibilidad acordada y umbrales confirmados. OE3 queda parcialmente desarrollado. Su implicación para compras, ventas y poscosecha es una posibilidad por probar, no un efecto demostrado. [PENDIENTE: definir y validar con la empresa la referencia y los umbrales de faltante/normalidad/sobrante, con responsables y acciones por señal.]\n\n### 7.5. Respuesta a OE4: validación operativa e impacto\n\nSe realizó comparación retrospectiva con el ingeniero y comprobación técnica parcial del adaptador, pero no una validación prospectiva completa en un entorno operativo. El cruce nominal no iguala automáticamente la información del jueves del ingeniero con la del lunes del modelo. Tampoco se midieron reducción de desviaciones tras adopción, costos, cumplimiento, compras evitadas ni resultados de ventas o poscosecha. OE4 permanece pendiente en su componente organizacional.\n\nLa evidencia permite diseñar el piloto, no declarar éxito empresarial. La siguiente decisión es congelar el modelo y el calendario de insumos, conservar predicciones originales y ajustadas antes de conocer el corte y acordar qué resultado operativo contará como mejora. El diagnóstico por producto ayuda a enfocar esa prueba sin reinterpretar el test observado como validación nueva.\n\n### 7.6. Continuidad y condiciones para el uso empresarial\n\nLa prioridad es un momento de emisión común con el ingeniero y un período posterior a la selección de modelos. Las mejoras de H3–H5 deberán elegirse con validación anterior y verificarse en otras semanas; el diagnóstico de este test no se reutiliza como prueba de una corrección. En paralelo, se requiere validar unidades climáticas, procedencia piloto, edades improductivas y significado de días sin registro. El alcance sigue restringido a GAITANA; no se generaliza a ARABELLA.\n\nLos pendientes académicos, agronómicos y operativos se reúnen en el anexo C. No se presentan como resultados cumplidos ni la adopción ni el beneficio económico, y la comparación diaria conserva su condición exploratoria.\n'
text=subsection(text,'## 7. Conclusiones','## Referencias de la evidencia',conclusions)
text=text.replace('| E19 | Analisis/21–25 | Semanas recientes, horizontes separados, experimento n−1 y especialistas H3–H5 |',
 '| E19 | Analisis/21–25 | Semanas recientes, horizontes separados, experimento n−1 y especialistas H3–H5 |\n| E20 | Modelo_de_series_diario/06_RNN_profunda_produccion_diaria.ipynb | Ensayo LSTM de un día adelante, validación y límites de comparación |\n| E21 | plataforma_gaitana/backend/app/model19.py y evidencia_regresion_modelo19.json | Adaptador y regresión parcial de 584 casos; no es evaluación prospectiva |')
text=text.replace('Las referencias E1–E19','Las referencias E1–E22')
text=text.replace('no es evaluación prospectiva |','no es evaluación prospectiva |\n| E22 | Plan de Proyecto/Plan de proyecto_final.docx, secciones 2.1–2.2 y 5.4–5.5 | Objetivos originales, métricas previstas, banda inicial ±8 % y señales operativas |')
text=text.replace('Referencia técnica utilizada en la implementación: documentación oficial de SARIMAX de statsmodels, https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html.',
 '[PENDIENTE: integrar y verificar la bibliografía académica del anteproyecto y sus citas en formato APA; las referencias E1–E21 son evidencia interna, no sustituyen esa revisión.]')
text=text.replace('## Anexo. Diccionario de la base analítica común','## Anexo A. Diccionario de la base analítica común')
text+='''

## Anexo B. Trazabilidad técnica de las métricas de esta edición

Las tablas de modelos de esta edición se derivan de las predicciones guardadas, conservando su panel y sus fechas. `Revision_v7/auditoria_metricas_v7.csv` contiene MAE, RMSE, MAPE, WAPE/WMAPE, porcentaje dentro de ±8 %, sesgo medio, saldo neto en tallos, sesgo porcentual, tamaño, conteos de reales positivos/cero y rango temporal de cada comparación. Los indicadores sin predicciones individuales suficientes permanecen sin valor y se declaran pendientes. `Revision_v7/fuentes_y_verificaciones.json` identifica archivos y huellas SHA-256. Las diferencias con tablas de versiones anteriores sólo se actualizan donde se documenta el panel nominal corregido; los experimentos de 15.838 casos se mantienen como historia metodológica.

Los archivos intermedios de reglas que combinaban una salida del ingeniero y un modelo no se usan como evidencia del candidato autónomo final del cuaderno 25. Sus nombres se distinguen de `25_predicciones_candidato_sin_ingeniero.parquet`; los pesos vigentes se verifican en los CSV de tuning de modelos propios, no en `25_pesos_mezcla_h3_h5.csv`, que corresponde a otro ensayo.

No se reestimaron hiperparámetros ni se entrenó un modelo nuevo para esta revisión. Los vacíos de entrenamiento/validación no archivados en escala de tallos se señalan como pendientes en vez de asignarles resultados del test.

## Anexo C. Pendientes identificados para cierre académico y operativo

'''

# Figuras: congelar las utilizadas y numerar por orden de aparición en el nuevo Word.
for match in list(re.finditer(r'!\[(.*?)\]\((.*?)\)',text)):
    original=match.group(2)
    if original.startswith('Figuras_resultados/'):
        src=track(DOC/original);dest=ASSETS/src.name;shutil.copy2(src,dest)
        text=text.replace(']('+original+')',']('+dest.relative_to(DOC).as_posix()+')')
counter=0
def caption(match):
    global counter
    counter+=1
    title=re.sub(r'^(?:Figura\s+\d+[a-z]?|Diagrama\s+[A-Z])\.\s*','',match[1])
    return f'![Figura {counter}. {title}]({match[2]})'
text=re.sub(r'!\[(.*?)\]\((.*?)\)',caption,text)

# Las figuras actualizadas y las auditorías se generan antes de guardar el documento.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'serif','font.size':9})
fig,axes=plt.subplots(1,2,figsize=(8.4,4.3))
for ax,(title,g) in zip(axes,[('H1',fa.loc[fa.horizonte.eq(1)]),('H1–H5',fa)]):
    pairs=[]
    for product,z in g.groupby('producto'):
        pairs.append((product,(z.Seleccion_pre2026-z.y).abs().sum()/g.y.sum()*100,(z.ingeniero-z.y).abs().sum()/g.y.sum()*100))
    pairs=sorted(pairs,key=lambda r:-r[1])[:7];pos=np.arange(len(pairs))
    ax.barh(pos-.17,[r[1] for r in pairs],.34,label='Modelo',color='#800020')
    ax.barh(pos+.17,[r[2] for r in pairs],.34,label='Ingeniero',color='#315f82')
    ax.set_yticks(pos,[r[0] for r in pairs]);ax.invert_yaxis();ax.set_title(title)
    ax.set_xlabel('Aporte al WAPE total (pp)');ax.spines[['top','right']].set_visible(False)
axes[1].legend(frameon=False);fig.tight_layout();fig.savefig(ASSETS/'error_aporte_productos_v7.png',dpi=240);plt.close(fig)
products=fa.groupby('producto').y.sum().sort_values(ascending=False).head(8).index
matrix=np.array([[score(g,'Seleccion_pre2026')['WAPE_pct']-score(g,'ingeniero')['WAPE_pct']
    for h in range(1,6) for g in [fa.loc[fa.producto.eq(p)&fa.horizonte.eq(h)]]] for p in products])
fig,ax=plt.subplots(figsize=(7,4));im=ax.imshow(matrix,cmap='RdBu_r',vmin=-10,vmax=10,aspect='auto')
ax.set_yticks(range(len(products)),products);ax.set_xticks(range(5),['H1','H2','H3','H4','H5'])
for (i,j),value in np.ndenumerate(matrix):ax.text(j,i,f'{value:.2f}',ha='center',va='center',fontsize=8,color='white' if abs(value)>6 else 'black')
fig.colorbar(im,ax=ax,label='WAPE modelo − ingeniero (pp)');fig.tight_layout();fig.savefig(ASSETS/'error_producto_horizonte_v7.png',dpi=240);plt.close(fig)
fig,axes=plt.subplots(3,1,figsize=(7,6),sharex=True)
for ax,variety in zip(axes,['UCHUVA','EPSILON','ACADEMY']):
    g=fa.loc[fa.horizonte.eq(1)&fa.variedad.eq(variety)]
    g=g.groupby('semana_objetivo')[['y','Seleccion_pre2026','ingeniero']].sum().sort_index()
    for col,label,color in [('y','Real','#64806d'),('Seleccion_pre2026','Modelo','#800020'),('ingeniero','Ingeniero','#315f82')]:
        ax.plot(g.index,g[col],label=label,color=color,linewidth=1.2)
    ax.set_ylabel('Tallos');ax.set_title(variety,loc='left');ax.spines[['top','right']].set_visible(False)
axes[0].legend(frameon=False,ncol=3);fig.autofmt_xdate();fig.tight_layout();fig.savefig(ASSETS/'error_variedades_foco_v7.png',dpi=240);plt.close(fig)

# Registrar pendientes sin completar datos no disponibles.
pending=list(dict.fromkeys(re.findall(r'\[PENDIENTE: ([^\]]+)\]',text)))
pending += ['Confirmar la pertinencia de PCA/MCA/PDN con el asesor; no se presentan como etapas ejecutadas.',
            'Archivar métricas train/validación en tallos de los candidatos recientes 21–25 antes de interpretar sobreajuste; sus salidas actuales no conservan todas esas predicciones.',
            'Completar bibliografía, referencias cruzadas, portada institucional y revisión final de formato antes de radicar.']
text+=md_table(['ID','Información o validación pendiente'],[[f'P{i:02}',f'[PENDIENTE: {item}]'] for i,item in enumerate(pending,1)])
pd.DataFrame(audit).to_csv(OUT/'auditoria_metricas_v7.csv',index=False,encoding='utf-8-sig')
checks={'anual_casos':len(fa),'historia_14_15_casos':len(f14),'recientes_casos':len(f25),
        'diario_casos':len(dc),'sarima_casos':len(sc),'rnn_casos':len(rnn),'rnn_comunes':len(rc),
        'figuras':counter,'metricas_registradas':len(audit),'pendientes':len(pending),
        'modelo_seleccionado':'Sin_clima, cuaderno 19','sin_reentrenamiento':True}
manifest={'fecha_revision':'2026-10-28','fuentes_sha256':sources,'verificaciones':checks,
          'regla_error':'prediccion menos real; calculado por caso antes de agregar',
          'objetivos':'OG y cuatro OE transcritos del Plan de proyecto_final.docx, sección 2.1–2.2'}
(OUT/'fuentes_y_verificaciones.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(DOC/(NAME+'.md')).write_text(text,encoding='utf-8')
(OUT/'PENDIENTES_v7.md').write_text('# Pendientes de la versión 7\n\n'+'\n\n'.join(f'{i}. {item}' for i,item in enumerate(pending,1))+'\n',encoding='utf-8')
changes='''# Cambios de la versión 7

Base: Documento_LaGaitana_v6.docx y Desarrollo_del_documento.md, conservados sin sobrescribir.

- Objetivo general y cuatro objetivos específicos transcritos del Plan original, con conclusiones de alcance logrado/parcial/pendiente; no se reemplazan por objetivos nuevos.
- Decisiones, supuestos y limitaciones ubicados en cada etapa, incluyendo calendario jueves/lunes y diferencias del protocolo reciente.
- Métricas técnicas completas desde predicciones archivadas, con paneles y cortes separados; no se reentrenaron modelos.
- Diagnóstico por producto/color/variedad sincronizado con el panel nominal de 16.325 casos, con figuras recalculadas.
- Ensayos recientes: 5.000 registros máximos por ajuste, variables y muestreo distintos del 19; fechas efectivas por horizonte y H1 sobre una sola semana.
- Piloto diario separado; LSTM identificada como un día adelante, sin equipararla a siete días emitidos al lunes.
- Discusión de implicaciones organizacionales sin atribuir beneficios económicos no medidos.
- Figuras numeradas por orden de aparición; estilo sobrio y tablas monocromas. Fuentes y auditoría acompañan esta edición.
'''
(OUT/'CAMBIOS_v7.md').write_text(changes,encoding='utf-8')
print(json.dumps(checks,ensure_ascii=False,indent=2))
