"""Regresión contra predicciones archivadas de un origen mensual del 19."""
import json
import numpy as np
import pandas as pd
from app.model19 import run_forecast
from app.data import KEY,REVIEW,read
from app.config import STORAGE,LEGACY

def main():
    reference=read(REVIEW/'comparacion_clima_curvas_2026.parquet')
    last_month=reference.origen.max().to_period('M')
    origin=reference.loc[reference.origen.dt.to_period('M').eq(last_month),'origen'].min()
    print('Reproduciendo origen',origin,flush=True)
    generated,metadata=run_forecast(str(origin.date()),'Sin_clima',lambda n,m:print(n,m,flush=True),source_root=LEGACY)
    keys=KEY+['origen','semana_objetivo','horizonte']
    expected=reference.loc[reference.origen.eq(origin)]
    joined=expected.merge(generated[keys+['prediction']],on=keys,validate='one_to_one')
    assert len(joined)==len(expected), 'Cambió la población comparable.'
    difference=np.abs(joined.Sin_clima-joined.prediction)
    report={'scope':'Un origen de la evaluación archivada; no certifica todos los cortes',
            'origin':str(origin.date()),'cases':len(joined),'horizons':sorted(joined.horizonte.unique().astype(int).tolist()),'max_absolute_difference':float(difference.max()),
            'mean_absolute_difference':float(difference.mean()),'tolerance_stems':0.000001,
            'passed':bool(np.allclose(joined.Sin_clima,joined.prediction,rtol=0,atol=1e-6)),
            'data_hash':metadata['data_hash'],'adapter_sha256':metadata['adapter_sha256']}
    (STORAGE/'verification_model19.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)
    if not report['passed']:raise SystemExit(1)

if __name__=='__main__':main()
