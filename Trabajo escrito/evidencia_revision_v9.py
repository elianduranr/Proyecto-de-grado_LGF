"""Verifica universos y reconstruye figuras editoriales sin entrenar modelos."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,FancyArrowPatch
sys.stdout.reconfigure(encoding='utf8')
F=Path(__file__).resolve().parent;R=F.parent;O=F/'Revision_v9';G=O/'Figuras';G.mkdir(parents=True,exist_ok=True)
S=R/'plataforma_gaitana/storage/datasets/evaluacion_local_20261028'
P=S/'Notebooks/Proyecciones Teoricas Propias/resultados_todos_los_anios'
D=S/'Datos_analiticos_proyecto';V=R/'Datos_analiticos_proyecto/validacion_temporal_20261028'
facts={};inputs={}
def read(p,columns=None):
    inputs[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
    return pd.read_parquet(p,columns=columns)
b=read(D/'modelo_con_proyecciones_teoricas/base_analitica_proyecciones.parquet')
w=read(D/'modelo_con_proyecciones_teoricas/produccion_clima_semanal.parquet')
e=read(P/'2026/estadisticas_auditoria.parquet');u=read(P/'2026/estadisticas.parquet')
facts['base']={'rows':len(b),'cols':len(b.columns),'observados':int(b.y.notna().sum()),'admisibles_observados':int((b.y.notna()&b.admisible_modelo).sum()),'por_estado':b.loc[b.y.notna(),'motivo_cobertura'].value_counts().to_dict()}
facts['uniones']=e.estado_union.value_counts().to_dict()
facts['uniones_cortes_2026']=e.loc[e.fecha_corte.dt.year.eq(2026),'estado_union'].value_counts().to_dict()
facts['pilotos']={'entrantes':len(e),'unica':int(e.estado_union.eq('unica').sum()),'utilizables':len(u),'otros_filtros':int(e.estado_union.eq('unica').sum()-len(u)),'cero':int(u.corte.eq(0).sum()),'desde':str(u.fecha_corte.min().date()),'hasta':str(u.fecha_corte.max().date())}
facts['semanal']={'rows':len(w),'tallos':float(w.tallos_reales.sum()),'desde':str(w.semana_inicio.min().date()),'hasta':str(w.semana_inicio.max().date())}
shares=w.groupby('producto').tallos_reales.sum().sort_values(ascending=False)
facts['composicion']={str(k):{'tallos':float(v),'pct':float(100*v/shares.sum())} for k,v in shares.items()}
facts['schemas']={}
for p in D.glob('*.parquet'):facts['schemas'][p.stem]={'rows':pq.ParquetFile(str(p)).metadata.num_rows,'cols':pq.ParquetFile(str(p)).schema_arrow.names}
facts['planos_seleccionados']=int(len(read(P/'seleccion_planos.parquet')))
obs=b.loc[b.y.notna()]
cover=obs.groupby('horizonte').agg(casos=('y','size'),directos=('curva_completa','sum')).reset_index();cover['pct']=100*cover.directos/cover.casos
cover.to_csv(O/'soporte_edades_por_horizonte.csv',index=False)
facts['soporte_edades']=cover.to_dict('records')
curves=read(P/'2026/curvas.parquet');c=curves.loc[curves.clave_curva.eq('COMERCIAL|SOLOMIO|WHITE|ARD')].copy();last=c.fecha_plano.max();c=c.loc[c.fecha_plano.eq(last)].sort_values('edad')
facts['ejemplo_curva']={'clave':'COMERCIAL|SOLOMIO|WHITE|ARD','fecha_plano':str(last.date()),'edades':len(c),'edad_min':float(c.edad.min()),'edad_max':float(c.edad.max()),'max_soporte':int(c.n_observaciones.max()),'ejemplo_punto':c.loc[c.n_observaciones.idxmax(),['edad','rendimiento_curva','n_observaciones']].to_dict()}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(7.7,3.1));ax.bar(cover.horizonte,cover.pct,color='#686868',width=.55)
for _,r in cover.iterrows():ax.text(r.horizonte,r.pct+.25,f'{r.pct:.2f} %'.replace('.',','),ha='center',fontsize=9)
ax.set(xlabel='Horizonte semanal del modelo',ylabel='Casos observados con todas\nlas edades representadas (%)',ylim=(15,max(cover.pct)+3),xticks=cover.horizonte,xticklabels=[f'H{int(x)}' for x in cover.horizonte]);ax.grid(axis='y',alpha=.2)
fig.tight_layout();fig.savefig(G/'soporte_edades.png',dpi=220);plt.close(fig)
facts['figura_soporte_eje_min']=15
fig,axes=plt.subplots(2,1,figsize=(7.7,4.2),sharex=True,gridspec_kw={'height_ratios':[1.5,1]})
ages=np.arange(int(c.edad.min()),int(c.edad.max())+1);cc=c.set_index('edad').reindex(ages)
axes[0].plot(ages,cc.rendimiento_curva,marker='o',markersize=2.5,color='#326b79',lw=1)
axes[0].set_ylabel('Tallos por planta');axes[1].bar(c.edad,c.n_observaciones,color='#888888',width=1)
axes[1].set(xlabel='Edad desde la semana de siembra (semanas)',ylabel='Observaciones\npiloto–semana')
for ax in axes:ax.grid(axis='y',alpha=.2)
fig.tight_layout();fig.savefig(G/'curva_soporte.png',dpi=220);plt.close(fig)
def diagram(name,boxes,arrows,size):
    fig,ax=plt.subplots(figsize=size);ax.set(xlim=(0,10),ylim=(0,10));ax.axis('off')
    for x,y,ww,hh,head,body in boxes:
        ax.add_patch(Rectangle((x,y),ww,hh,fill=False,linewidth=1.1,color='black'))
        ax.text(x+ww/2,y+hh*.74,head,ha='center',va='center',fontsize=12,fontweight='bold')
        ax.text(x+ww/2,y+hh*.31,body,ha='center',va='center',fontsize=11,linespacing=1.3)
    for start,end in arrows:ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=13,color='black',lw=1))
    fig.tight_layout(pad=.3);fig.savefig(G/name,dpi=220,bbox_inches='tight');plt.close(fig)
pilot=f"{len(e):,} filas de estadísticas (edición 2026)".replace(',','.')
fmt=lambda n:f'{int(n):,}'.replace(',','.')
diagram('pretratamiento.png',[
(.25,7.6,9.5,1.7,'Unión con cama y ciclo',pilot+f"\n{fmt(facts['pilotos']['unica'])} con pareja única; {fmt(len(e)-facts['pilotos']['unica'])} pendientes de unión"),
(.25,4.7,5.5,1.7,'Observaciones utilizables',f"{fmt(len(u))} filas; incluye {fmt(facts['pilotos']['cero'])} ceros\n{fmt(facts['pilotos']['otros_filtros'])} con pareja única no superan otros filtros"),
(6.15,4.7,3.6,1.7,'Conservación y trazabilidad',f"{fmt(sum(v for k,v in facts['uniones_cortes_2026'].items() if k!='unica'))} pendientes de unión\nentre los cortes de 2026"),
(.25,1.5,9.5,2,'Panel analítico actualizado de GAITANA',f"{len(w):,} series–semana → {len(b):,} casos origen–horizonte\n{b.y.notna().sum():,} con real; {(b.y.notna()&b.admisible_modelo).sum():,} con real e historia admisible".replace(',','.'))],
[((3,7.6),(3,6.4)),((8,7.6),(8,6.4)),((3,4.7),(3,3.5))],(8,4.4))
diagram('metodologia_semanal.png',[
(.25,8.1,9.5,1.5,'Integración temporal y variables','Serie comercial + origen + semana objetivo · H1–H5'),
(.25,5.05,4.4,1.9,'Referencia de curva aplicable','Todas las edades representadas\nAprender: real − teoría'),
(5.35,5.05,4.4,1.9,'Referencia de producción reciente','Media de cuatro semanas previas\nAprender: real − Media4'),
(.25,2.1,9.5,1.8,'Boosting sin clima · configuración seleccionada','Un grupo H1–H2 y otro H3–H5; dos rutas en cada grupo\nIdentidad, calendario, memoria semanal/diaria; teoría sólo en su ruta'),
(.25,.05,9.5,1.25,'Evaluación temporal y comparación','Referencia + corrección, mínimo cero · comparación nominal y por horizonte')],
[((2.5,8.1),(2.5,6.95)),((7.5,8.1),(7.5,6.95)),((2.5,5.05),(2.5,3.9)),((7.5,5.05),(7.5,3.9)),((5,2.1),(5,1.3))],(8,5))
annual=pd.read_csv(V/'metricas_2026_completo.csv');facts['metricas_2026']=annual.to_dict('records')
fig,axes=plt.subplots(1,2,figsize=(8,3.4));colors=['#800020','#39748a']
for method,label,col in zip(['19_mensual_sin_clima','Ingeniero'],['Modelo','Profesional de producción'],colors):
    ss=annual.loc[annual.metodo.eq(method)&annual.horizonte.ne('Total')].copy();x=ss.horizonte.astype(float)
    axes[0].plot(x,ss.WAPE,'o-',label=label,color=col);axes[1].plot(x,ss.sesgo_pct,'o-',color=col,label=label)
for ax,yl in zip(axes,['WAPE (%)','Sesgo firmado (%)']):ax.set(xlabel='Horizonte',ylabel=yl,xticks=range(1,6),xticklabels=[f'H{i}' for i in range(1,6)]);ax.grid(alpha=.2)
axes[1].axhline(0,color='black',lw=.8);fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=2,frameon=False)
fig.tight_layout(rect=(0,.08,1,1));fig.savefig(G/'comparacion_horizontes.png',dpi=220);plt.close(fig)
# Panel de producto reconstruido desde los mismos casos anuales, sin repetir ni cancelar errores al agregar.
pred=read(V/'predicciones_actualizadas.parquet');facts['pred_columns']=list(pred.columns)
common=pred.loc[pred.modelo.eq('19_mensual_sin_clima')&pred.ingeniero.notna()].copy()
facts['modelos_pred']=pred.modelo.unique().tolist()
rows=[]
for product,g in common.groupby('producto'):
    den=g.y.sum();total=common.y.sum()
    rows.append({'producto':product,'casos':len(g),'tallos_reales':float(den),'WAPE_modelo':float(100*(g.prediccion-g.y).abs().sum()/den),'WAPE_referencia':float(100*(g.ingeniero-g.y).abs().sum()/den),'aporte_modelo_pp':float(100*(g.prediccion-g.y).abs().sum()/total),'aporte_referencia_pp':float(100*(g.ingeniero-g.y).abs().sum()/total)})
pd.DataFrame(rows).sort_values('aporte_modelo_pp',ascending=False).to_csv(O/'error_producto_actualizado.csv',index=False)
associations=[]
for h in [1,5]:
    z=b.loc[b.horizonte.eq(h)&b.curva_completa&b.y.notna()&b.semana_objetivo.lt('2025-07-07')].copy();z['error']=z.y-z.teoria_modelo
    for var in ['produccion_lag1','cambio_reciente','media_4']:
        values=[]
        for _,gg in z.groupby(['producto','color','variedad']):
            gg=gg[[var,'error']].dropna()
            if len(gg)>=20 and gg[var].nunique()>1 and gg.error.nunique()>1:values.append(gg[var].corr(gg.error,method='spearman'))
        associations.append({'horizonte':h,'variable':var,'mediana_spearman':float(np.median(values)),'series':len(values)})
pd.DataFrame(associations).to_csv(O/'asociaciones_memoria.csv',index=False)
facts['asociaciones_memoria']=associations
# Redibujar el análisis climático conservado: etiquetas legibles y sin códigos de implementación.
climate=read(R/'Datos_analiticos_proyecto/revision_clima_finca/asociaciones_clima_modelos.parquet')
variables=['temperatura_semana_lag1','temperatura_semana_media4','humedad_semana_lag1','humedad_semana_media4','radiacion_semana_lag1','radiacion_semana_media4']+[f'{v}_media_{n}d' for v in ['temperatura','humedad','radiacion'] for n in [3,5,7]]+['temperatura_media14_clima','temperatura_cambio7_28_clima','humedad_media14_clima','humedad_cambio7_28_clima','radiacion_media14_clima','radiacion_cambio7_28_clima','lluvia_suma7_clima','lluvia_suma28_clima','lluvia_dias7_clima','cobertura_dias7_clima','cobertura_dias28_clima']
assert set(variables)==set(climate.variable.unique()),'Las 26 variables de la figura deben corresponder a las de la fuente.'
labels=['Temp. semana previa','Temp. media 4 sem.','Humedad semana previa','Humedad media 4 sem.','Radiación semana previa','Radiación media 4 sem.']+[f'{v} media {n} días' for v in ['Temp.','Humedad','Radiación'] for n in [3,5,7]]+['Temp. media 14 días','Temp. cambio 7/28 días','Humedad media 14 días','Humedad cambio 7/28 d.','Radiación media 14 días','Radiación cambio 7/28 d.','Lluvia suma 7 días','Lluvia suma 28 días','Días con lluvia en 7 días','Disponibilidad 7 días','Disponibilidad 28 días']
fig,axes=plt.subplots(1,2,figsize=(8.2,9.1),sharey=True)
for ax,reading in zip(axes,['Pares disponibles','Casos comunes']):
    ss=climate.loc[climate.lectura.eq(reading)]
    z=ss.pivot(index='variable',columns='horizonte',values='rho_mediana').reindex(index=variables,columns=range(1,6))
    ax.imshow(z.to_numpy(),vmin=-.3,vmax=.3,cmap='RdBu_r',aspect='auto')
    ax.set(xticks=range(5),xticklabels=[f'H{x}' for x in range(1,6)],yticks=range(26),yticklabels=labels)
    ax.tick_params(labelsize=12);ax.set_title(reading,fontsize=13)
    for yy in range(26):
        for xx in range(5):
            val=z.iloc[yy,xx]
            if pd.notna(val):ax.text(xx,yy,f'{val:.2f}'.replace('.',','),ha='center',va='center',fontsize=11)
    for yy in [5.5,14.5]:ax.axhline(yy,color='black',lw=.8)
fig.subplots_adjust(left=.30,right=.99,top=.96,bottom=.04,wspace=.08)
fig.savefig(G/'clima_asociaciones.png',dpi=220);plt.close(fig)
(O/'datos_verificados.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2,default=str),encoding='utf8')
(O/'fuentes_sha256.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in facts.items() if k not in ['schemas','metricas_2026','composicion']},ensure_ascii=False,indent=2,default=str))
print('SCHEMAS',json.dumps(facts['schemas'],ensure_ascii=False))
