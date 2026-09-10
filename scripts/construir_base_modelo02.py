"""Regenera derivados de Modelo 02; nunca modifica fuentes originales."""
from pathlib import Path, PureWindowsPath
import re, unicodedata
import numpy as np
import pandas as pd

RAIZ=Path(__file__).resolve().parents[1]; DATOS=RAIZ/"Datos"; SALIDA=DATOS/"modelado"; AUD=SALIDA/"auditoria"
SALIDA.mkdir(parents=True,exist_ok=True); AUD.mkdir(parents=True,exist_ok=True)
CLIMA=["temp_media","temp_min","temp_max","humedad_media","lluvia_acumulada","radiacion_media","et_acumulada"]
LLAVE=["anio_emision","semana_emision","anio_objetivo","semana_objetivo","horizonte","k_producto","k_color","k_variedad"]

def clave(x):
    x="" if pd.isna(x) else str(x); x=unicodedata.normalize("NFKD",x).encode("ascii","ignore").decode()
    return re.sub(r"\s+"," ",x.strip().upper())
def lunes_iso(a,s):
    try:return pd.Timestamp.fromisocalendar(int(a),int(s),1)
    except (ValueError,TypeError):return pd.NaT
def desplazar(a,s,n):
    f=lunes_iso(a,s)+pd.Timedelta(weeks=int(n)); iso=f.isocalendar(); return int(iso.year),int(iso.week),f
def nombre_portable(x):
    t=str(x); return PureWindowsPath(t).name if "\\" in t else Path(t).name
def suma_na(x): return x.sum(min_count=1)

print("1/7 Curvas y disponibilidad temporal")
rc=DATOS/"Curvas por variedad"/"datos preprocesados"/"bases consolidadas"/"base_curvas_relacionada_camas_piloto.parquet"
cc=["archivo_origen","anio_archivo","variedad_original","edad_semanas","flores_planta_semana","estado_match","cama_piloto_original"]
cur=pd.read_parquet(rc,columns=cc); cur["k_variedad"]=cur.variedad_original.map(clave)
cur["edad_semana"]=pd.to_numeric(cur.edad_semanas,errors="coerce").round().astype("Int64")
cur["flores_planta_semana"]=pd.to_numeric(cur.flores_planta_semana,errors="coerce")
cur=cur[cur.estado_match.astype(str).str.startswith("match")&cur.k_variedad.ne("")&cur.edad_semana.between(0,150)&cur.flores_planta_semana.between(0,3)]
ic=pd.read_csv(DATOS/"Curvas por variedad"/"datos preprocesados"/"auditoria"/"inventario_libros.csv")
fc=[c for c in ic if any(x in c.lower() for x in ["fecha","semana","creacion","modificacion"])]
ic.assign(fecha_disponibilidad_encontrada=bool(fc),regla_provisional="anio_archivo <= anio_emision",
          alerta_fuga_temporal=not bool(fc)).to_csv(AUD/"disponibilidad_temporal_curvas.csv",index=False,encoding="utf-8-sig")
perfiles={}; sp=[]
for a in range(int(cur.anio_archivo.min()),int(cur.anio_archivo.max())+1):
    h=cur[cur.anio_archivo<=a]
    p=h.groupby(["k_variedad","edad_semana"],as_index=False).agg(
        flores_planta_semana=("flores_planta_semana","median"),curva_p25=("flores_planta_semana",lambda x:x.quantile(.25)),
        curva_p75=("flores_planta_semana",lambda x:x.quantile(.75)),observaciones_curva=("flores_planta_semana","size"),
        camas_curva=("cama_piloto_original","nunique")); p["curva_iqr"]=p.curva_p75-p.curva_p25
    perfiles[a]=p; sp.append(p.assign(anio_disponible=a,alerta_disponibilidad_curva="Sin fecha exacta; posible fuga dentro del año"))
pd.concat(sp).to_csv(SALIDA/"perfiles_curva_historicos.csv",index=False,encoding="utf-8-sig"); del cur

print("2/7 Planos y pronóstico teórico")
inv=pd.read_csv(DATOS/"Plano de Siembras"/"datos preprocesados"/"auditoria"/"inventario_bases_semanales.csv")
inv=inv[~inv.estado.astype(str).str.startswith("error")].copy(); inv["prioridad"]=inv.version.astype(str).str.contains("actualizado",case=False).astype(int)
inv=inv.sort_values(["anio","semana","prioridad","salida"]).drop_duplicates(["anio","semana"],keep="last").query("anio>=2023")
pron=[]; dups=[]; rd=[]
for num,foto in enumerate(inv.itertuples(index=False),1):
    nom=nombre_portable(foto.salida); ruta=DATOS/"Plano de Siembras"/"datos preprocesados"/"bases semanales"/str(int(foto.anio))/nom
    if not ruta.exists(): raise FileNotFoundError(ruta)
    s=pd.read_csv(ruta,low_memory=False); m=s.duplicated(keep=False)
    if m.any(): dups.append(s[m].assign(anio_foto_aud=int(foto.anio),semana_foto_aud=int(foto.semana),archivo_plan_aud=nom))
    rd.append([foto.anio,foto.semana,nom,len(s),int(m.sum()),int(s.duplicated().sum())]); s=s.drop_duplicates().copy()
    for c in ["producto","color","variedad"]: s[f"k_{c}"]=s[c].map(clave)
    s["plantas"]=pd.to_numeric(s.plantas,errors="coerce"); s["edad_base"]=pd.to_numeric(s.edad,errors="coerce")
    s["k_cama_fisica"]=s.finca.map(clave)+"|"+s.invernadero.map(clave)+"|"+s.nro_cama.astype(str)
    s=s[(s.plantas>0)&s.edad_base.notna()&s.k_variedad.ne("")]; perfil=perfiles[max(x for x in perfiles if x<=int(foto.anio))]
    for h in range(1,6):
        q=s.copy(); q["semanas_adelante"]=h-1; q["edad_objetivo"]=(q.edad_base+h-1).round().astype("Int64")
        q=q.merge(perfil,left_on=["k_variedad","edad_objetivo"],right_on=["k_variedad","edad_semana"],how="left",validate="many_to_one")
        q["tallos_teoricos_cama"]=q.plantas*q.flores_planta_semana; q["plantas_con_curva"]=q.plantas.where(q.flores_planta_semana.notna(),0)
        q["edad_x_plantas"]=q.edad_objetivo*q.plantas; q["curva_x_plantas"]=q.flores_planta_semana*q.plantas; q["iqr_x_plantas"]=q.curva_iqr*q.plantas
        for lo,hi,n in [(0,25,"plantas_edad_0_25"),(26,50,"plantas_edad_26_50"),(51,75,"plantas_edad_51_75"),(76,10000,"plantas_edad_76_mas")]: q[n]=q.plantas.where(q.edad_objetivo.between(lo,hi),0)
        ao,so,lun=desplazar(foto.anio,foto.semana,h-1)
        a=q.groupby(["k_producto","k_color","k_variedad"],as_index=False).agg(
          plantas=("plantas","sum"),segmentos_plan=("k_cama_fisica","size"),camas_plan_unicas=("k_cama_fisica","nunique"),
          edad_x_plantas=("edad_x_plantas","sum"),edad_min=("edad_objetivo","min"),edad_max=("edad_objetivo","max"),edad_desviacion=("edad_objetivo","std"),
          plantas_con_curva=("plantas_con_curva","sum"),curva_x_plantas=("curva_x_plantas",suma_na),iqr_x_plantas=("iqr_x_plantas",suma_na),
          tallos_teoricos=("tallos_teoricos_cama",suma_na),observaciones_curva=("observaciones_curva","sum"),camas_curva=("camas_curva","sum"),
          plantas_edad_0_25=("plantas_edad_0_25","sum"),plantas_edad_26_50=("plantas_edad_26_50","sum"),plantas_edad_51_75=("plantas_edad_51_75","sum"),plantas_edad_76_mas=("plantas_edad_76_mas","sum"))
        a["edad_media_ponderada"]=a.edad_x_plantas/a.plantas; a["flores_planta_media_ponderada"]=a.curva_x_plantas/a.plantas_con_curva.replace(0,np.nan)
        a["curva_iqr_media_ponderada"]=a.iqr_x_plantas/a.plantas_con_curva.replace(0,np.nan); a["cobertura_curva_pct"]=100*a.plantas_con_curva/a.plantas
        a["anio_emision"],a["semana_emision"],a["anio_objetivo"],a["semana_objetivo"],a["lunes_objetivo"]=int(foto.anio),int(foto.semana),ao,so,lun
        a["horizonte"],a["semanas_adelante"],a["archivo_plan"]=h,h-1,nom; a["alerta_disponibilidad_curva"]="Sin fecha exacta; posible fuga dentro del año"; pron.append(a)
    if num%50==0: print(f" {num}/{len(inv)}")
pd.DataFrame(rd,columns=["anio","semana","archivo","filas_originales","filas_duplicadas_involucradas","duplicados_exactos_eliminados"]).to_csv(AUD/"resumen_duplicados_planos.csv",index=False,encoding="utf-8-sig")
if dups: pd.concat(dups).to_csv(AUD/"duplicados_exactos_planos_detalle.csv",index=False,encoding="utf-8-sig")
teo=pd.concat(pron,ignore_index=True); teo.to_csv(SALIDA/"pronostico_teorico_plan_curvas.csv",index=False,encoding="utf-8-sig")

print("3/7 Versiones del ingeniero")
ce=["archivo_origen","anio_carpeta","semana_inicio_archivo","finca","producto","color","variedad","tipo","anio_objetivo","semana_objetivo","horizonte","tallos"]
ps=[]
for r in (DATOS/"Estimados semanales"/"datos preprocesados"/"archivos").glob("*.csv"):
    try: q=pd.read_csv(r,usecols=ce,low_memory=False); q["archivo_csv"]=r.name; ps.append(q)
    except (ValueError,UnicodeDecodeError): pass
er=pd.concat(ps); er=er[er.finca.map(clave).eq("GAITANA")&er.tipo.map(clave).eq("ESTIMADO")].copy()
for c in ["producto","color","variedad"]: er[f"k_{c}"]=er[c].map(clave)
for c in ["anio_carpeta","semana_inicio_archivo","anio_objetivo","semana_objetivo","horizonte","tallos"]: er[c]=pd.to_numeric(er[c],errors="coerce")
er["tipo_version"]=np.where(er.archivo_origen.str.contains("ajust|corre",case=False,na=False),"ajustada_o_corregida","original_o_sin_marca")
tv=er.groupby(["anio_carpeta","semana_inicio_archivo","archivo_origen","archivo_csv","tipo_version"],as_index=False).agg(tallos_version=("tallos","sum"),filas=("tallos","size"))
multi=tv.groupby(["anio_carpeta","semana_inicio_archivo"]).archivo_origen.transform("nunique")>1; av=tv[multi].copy()
av["diferencia_vs_minimo_emision"]=av.tallos_version-av.groupby(["anio_carpeta","semana_inicio_archivo"]).tallos_version.transform("min"); av["fecha_disponibilidad"]=pd.NaT; av["advertencia"]="Sin timestamp; prioridad provisional"
av.to_csv(AUD/"versiones_estimado_ingeniero.csv",index=False,encoding="utf-8-sig")
er["prioridad_version"]=er.tipo_version.eq("ajustada_o_corregida").astype(int)
la=["archivo_origen","archivo_csv","anio_carpeta","semana_inicio_archivo","anio_objetivo","semana_objetivo","horizonte","k_producto","k_color","k_variedad","prioridad_version"]
est=er.groupby(la,as_index=False).agg(tallos_ingeniero=("tallos","sum")); lv=["anio_carpeta","semana_inicio_archivo","anio_objetivo","semana_objetivo","horizonte","k_producto","k_color","k_variedad"]
est=est.sort_values(lv+["prioridad_version","archivo_origen"]).drop_duplicates(lv,keep="last"); est["alerta_version_ingeniero"]="Sin timestamp; selección provisional"

print("4/7 Real, estados y persistencia")
real=pd.read_csv(DATOS/"Producción real"/"datos preprocesados"/"produccion_semanal_gaitana.csv")
for c in ["producto","color","variedad"]: real[f"k_{c}"]=real[f"k_{c}"].map(clave)
real["lunes_real"]=[lunes_iso(a,s) for a,s in zip(real.anio,real.semana)]; real=real.groupby(["anio","semana","lunes_real","k_producto","k_color","k_variedad"],as_index=False).agg(tallos_reales=("tallos_reales","sum")); ultima=real.lunes_real.max()
base=teo.merge(est,left_on=LLAVE,right_on=["anio_carpeta","semana_inicio_archivo","anio_objetivo","semana_objetivo","horizonte","k_producto","k_color","k_variedad"],how="left",validate="many_to_one")
base=base.merge(real,left_on=["anio_objetivo","semana_objetivo","k_producto","k_color","k_variedad"],right_on=["anio","semana","k_producto","k_color","k_variedad"],how="left",validate="many_to_one")
base["estado_objetivo"]=np.select([base.tallos_reales.notna(),base.lunes_objetivo>ultima],["real_observado","semana_futura"],default="sin_registro_en_semana_cerrada")
em=base[["anio_emision","semana_emision","k_producto","k_color","k_variedad"]].drop_duplicates(); em["lunes_emision"]=[lunes_iso(a,s) for a,s in zip(em.anio_emision,em.semana_emision)]
pe=pd.merge_asof(em.sort_values("lunes_emision"),real[["lunes_real","k_producto","k_color","k_variedad","tallos_reales"]].sort_values("lunes_real"),left_on="lunes_emision",right_on="lunes_real",by=["k_producto","k_color","k_variedad"],direction="backward",allow_exact_matches=False).rename(columns={"tallos_reales":"tallos_persistencia","lunes_real":"lunes_persistencia"})
base=base.merge(pe,on=["anio_emision","semana_emision","k_producto","k_color","k_variedad"],how="left",validate="many_to_one"); base["dias_antiguedad_persistencia"]=(base.lunes_emision-base.lunes_persistencia).dt.days
ae=base.groupby(["anio_objetivo","horizonte","estado_objetivo"],as_index=False).agg(filas=("estado_objetivo","size"),volumen_teorico=("tallos_teoricos","sum"),volumen_ingeniero=("tallos_ingeniero","sum")); ae.to_csv(AUD/"estado_objetivo_por_anio_horizonte.csv",index=False,encoding="utf-8-sig")

print("5/7 Clima ISO y rezagos exactos")
cf=pd.read_csv(DATOS/"Clima"/"datos preprocesados"/"clima_semanal_gaitana.csv"); cf["lunes_iso_validado"]=[lunes_iso(a,s) for a,s in zip(cf.anio,cf.semana)]
ci=cf[cf.lunes_iso_validado.isna()].copy(); ci["motivo"]="Año-semana inválido ISO"; ci.to_csv(AUD/"clima_semanas_iso_invalidas.csv",index=False,encoding="utf-8-sig")
c=cf[cf.lunes_iso_validado.notna()].sort_values("lunes_iso_validado").copy(); esp=pd.date_range(c.lunes_iso_validado.min(),c.lunes_iso_validado.max(),freq="7D"); fal=pd.DataFrame({"lunes_faltante":esp.difference(pd.DatetimeIndex(c.lunes_iso_validado))}); fal.to_csv(AUD/"clima_semanas_faltantes.csv",index=False,encoding="utf-8-sig")
um=float(c.mediciones.quantile(.10)); pocas=c[c.mediciones<um].copy(); pocas["umbral_percentil_10"]=um; pocas.to_csv(AUD/"clima_semanas_pocas_mediciones.csv",index=False,encoding="utf-8-sig")
cb=c[["anio","semana","lunes_iso_validado","mediciones"]+CLIMA].copy()
for lag in range(1,5):
    d=cb[["lunes_iso_validado"]+CLIMA].copy(); d["union"]=d.lunes_iso_validado+pd.Timedelta(days=7*lag); d=d.drop(columns="lunes_iso_validado").rename(columns={x:f"{x}_lag{lag}_seguro" for x in CLIMA}); cb=cb.merge(d,left_on="lunes_iso_validado",right_on="union",how="left",validate="one_to_one").drop(columns="union")
pd.DataFrame([{"registros_fuente":len(cf),"registros_iso_invalidos":len(ci),"semanas_faltantes":len(fal),"umbral_pocas_mediciones":um,"semanas_pocas_mediciones":len(pocas)}]).to_csv(AUD/"resumen_calidad_clima.csv",index=False,encoding="utf-8-sig")
seg=base[["anio_emision","semana_emision","lunes_emision"]].drop_duplicates().copy()
for lag in range(1,5):
    d=cb[["lunes_iso_validado"]+CLIMA].copy(); d["lunes_busqueda"]=d.lunes_iso_validado+pd.Timedelta(days=7*lag)
    d=d.drop(columns="lunes_iso_validado").rename(columns={x:f"{x}_lag{lag}_seguro" for x in CLIMA})
    seg=seg.merge(d,left_on="lunes_emision",right_on="lunes_busqueda",how="left",validate="one_to_one").drop(columns="lunes_busqueda")
seg=seg.drop(columns="lunes_emision")
con=cb[["anio","semana","mediciones"]+CLIMA].rename(columns={"anio":"anio_emision","semana":"semana_emision","mediciones":"mediciones_clima_emision",**{x:f"{x}_emision_condicionado" for x in CLIMA}})
ret=cb[["anio","semana"]+CLIMA].rename(columns={"anio":"anio_objetivo","semana":"semana_objetivo",**{x:f"{x}_objetivo_prohibido" for x in CLIMA}})
base=base.merge(seg,on=["anio_emision","semana_emision"],how="left",validate="many_to_one").merge(con,on=["anio_emision","semana_emision"],how="left",validate="many_to_one").merge(ret,on=["anio_objetivo","semana_objetivo"],how="left",validate="many_to_one")

print("6/7 Residuos, benchmarks y cortes")
base["residuo_teorico"]=base.tallos_reales-base.tallos_teoricos; base["residuo_ingeniero"]=base.tallos_reales-base.tallos_ingeniero; base["residuo_persistencia"]=base.tallos_reales-base.tallos_persistencia
base["cumplimiento_teorico"]=base.tallos_reales/base.tallos_teoricos.replace(0,np.nan); base["pronostico_corregido_formula"]="tallos_teoricos + residuo_predicho"; base["ultima_semana_real_cerrada"]=ultima
base.to_csv(SALIDA/"df_modelo_final.csv",index=False,encoding="utf-8-sig")
fm=[]
for h,g in base.groupby("horizonte"):
    co=g[g.estado_objetivo.eq("real_observado")].dropna(subset=["tallos_teoricos","tallos_ingeniero","tallos_persistencia","tallos_reales"]); cov=100*len(co)/len(g)
    for m,col in [("curva","tallos_teoricos"),("ingeniero","tallos_ingeniero"),("persistencia","tallos_persistencia")]:
        e=co[col]-co.tallos_reales; fm.append([h,h-1,m,len(co),cov,e.abs().mean(),100*e.abs().sum()/co.tallos_reales.abs().sum(),e.mean(),100*e.sum()/co.tallos_reales.sum()])
met=pd.DataFrame(fm,columns=["horizonte","semanas_adelante","metodo","pares","cobertura_comun_pct","MAE_tallos","WAPE_pct","sesgo_tallos","sesgo_pct"]); met.to_csv(SALIDA/"metricas_benchmarks_comunes.csv",index=False,encoding="utf-8-sig")
cortes=pd.DataFrame([["fold_1","2023","2024",False],["fold_2","2023-2024","2025",False],["prueba_final","2023-2025","2026",True]],columns=["corte","anios_entrenamiento","anio_validacion","reservado_prueba_final"]); cortes["regla"]="Separar por año-semana objetivo; sin objetivo compartido"; cortes.to_csv(SALIDA/"cortes_validacion_temporal.csv",index=False,encoding="utf-8-sig")

print("7/7 Resumen")
res=pd.DataFrame([{"filas_finales":len(base),"duplicados_llave_final":int(base.duplicated(LLAVE).sum()),"ultima_semana_real":str(ultima.date()),"clima_iso_invalidos":len(ci),"clima_semanas_faltantes":len(fal),"duplicados_exactos_planos_eliminados":int(pd.DataFrame(rd)[5].sum()),"alerta_curvas_sin_fecha_exacta":True,"alerta_versiones_sin_timestamp":True}]); res.to_csv(AUD/"resumen_revision_modelo02.csv",index=False,encoding="utf-8-sig")
print(res.to_string(index=False)); print(met.to_string(index=False))
