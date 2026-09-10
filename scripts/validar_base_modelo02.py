"""Validaciones duras de la base derivada Modelo 02. Sale con error si falla un control."""
from pathlib import Path
import numpy as np
import pandas as pd

RAIZ=Path(__file__).resolve().parents[1]; DATOS=RAIZ/"Datos"; MOD=DATOS/"modelado"; AUD=MOD/"auditoria"
base=pd.read_csv(MOD/"df_modelo_final.csv",low_memory=False,parse_dates=["lunes_objetivo","lunes_emision","lunes_persistencia","ultima_semana_real_cerrada"])
met=pd.read_csv(MOD/"metricas_benchmarks_comunes.csv")
llave=["anio_emision","semana_emision","anio_objetivo","semana_objetivo","horizonte","k_producto","k_color","k_variedad"]
resultados=[]
def check(nombre,cond,detalle):
    resultados.append({"control":nombre,"resultado":"OK" if bool(cond) else "FALLA","detalle":detalle})
    if not bool(cond): raise AssertionError(f"{nombre}: {detalle}")

check("llave_analitica_sin_duplicados",not base.duplicated(llave).any(),f"duplicados={base.duplicated(llave).sum()}")
m=base.tallos_reales.notna()&base.tallos_teoricos.notna()
check("signo_residuo",np.allclose(base.loc[m,"residuo_teorico"],base.loc[m,"tallos_reales"]-base.loc[m,"tallos_teoricos"]),"residuo=real-teórico")
check("horizonte_semanas_adelante",(base.semanas_adelante.eq(base.horizonte-1)).all(),"H1=0 ... H5=4")
check("persistencia_anterior_emision",(base.loc[base.lunes_persistencia.notna(),"lunes_persistencia"]<base.loc[base.lunes_persistencia.notna(),"lunes_emision"]).all(),"nunca usa semana igual o posterior")
ultima=base.ultima_semana_real_cerrada.max()
check("futuras_despues_cierre",(base.loc[base.estado_objetivo.eq("semana_futura"),"lunes_objetivo"]>ultima).all(),str(ultima.date()))
check("cerradas_sin_real",base.loc[base.estado_objetivo.eq("sin_registro_en_semana_cerrada"),"tallos_reales"].isna().all(),"no se imputan ceros")
check("observadas_con_real",base.loc[base.estado_objetivo.eq("real_observado"),"tallos_reales"].notna().all(),"tienen valor observado")
seguros=[c for c in base if c.endswith("_seguro")]; prohibidos=[c for c in base if c.endswith("_objetivo_prohibido")]
check("clima_objetivo_fuera_predictores",not set(seguros)&set(prohibidos),f"seguros={len(seguros)}, prohibidos={len(prohibidos)}")
clima=pd.read_csv(DATOS/"Clima"/"datos preprocesados"/"clima_semanal_gaitana.csv")
def iso(a,s):
    try:return pd.Timestamp.fromisocalendar(int(a),int(s),1)
    except (ValueError,TypeError):return pd.NaT
clima["lunes_validado"]=[iso(a,s) for a,s in zip(clima.anio,clima.semana)]
mapa=clima.dropna(subset=["lunes_validado"]).set_index("lunes_validado").temp_media
emisiones=base[["lunes_emision"]+[f"temp_media_lag{x}_seguro" for x in range(1,5)]].drop_duplicates("lunes_emision")
for lag in range(1,5):
    col=f"temp_media_lag{lag}_seguro"; esperado=(emisiones.lunes_emision-pd.Timedelta(days=7*lag)).map(mapa)
    ok=np.allclose(emisiones[col],esperado,equal_nan=True)
    check(f"lag{lag}_desplazamiento_exacto",ok,f"comparado contra fuente en fecha-{7*lag} días")
check("benchmarks_misma_muestra",met.groupby("horizonte").pares.nunique().eq(1).all(),"curva, ingeniero y persistencia comparten pares")
check("tres_benchmarks",set(met.metodo)=={"curva","ingeniero","persistencia"},str(sorted(met.metodo.unique())))
cortes=pd.read_csv(MOD/"cortes_validacion_temporal.csv")
check("cortes_temporales_definidos",len(cortes)==3,"2024, 2025 y prueba 2026")
for anio in [2024,2025,2026]:
    train=set(map(tuple,base.loc[base.anio_objetivo<anio,["anio_objetivo","semana_objetivo"]].drop_duplicates().to_numpy()))
    val=set(map(tuple,base.loc[base.anio_objetivo.eq(anio),["anio_objetivo","semana_objetivo"]].drop_duplicates().to_numpy()))
    check(f"corte_{anio}_sin_semana_compartida",train.isdisjoint(val),f"train={len(train)}, validación={len(val)}")

salida=pd.DataFrame(resultados); AUD.mkdir(parents=True,exist_ok=True)
salida.to_csv(AUD/"validacion_final.csv",index=False,encoding="utf-8-sig")
print(salida.to_string(index=False)); print("VALIDACIÓN COMPLETA: OK")
