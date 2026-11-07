"""Ejecutar y conservar salidas del cuaderno 26 con el entorno fijado de la app."""
import json
import sys
import time
from pathlib import Path
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager
from app.config import LEGACY,STORAGE

source=STORAGE/'datasets/evaluacion_local_20261028/manifest.json'
while True:
    if source.exists():
        info=json.loads(source.read_text(encoding='utf-8'))
        if info.get('state') in ['validado_local','validado','activo'] and len(set(info.get('completed_stages',[])))==11:break
    time.sleep(10)
path=LEGACY/'Notebooks/Analisis/26_validacion_temporal_actualizada_y_operacion.ipynb'
out=LEGACY/'Datos_analiticos_proyecto/validacion_temporal_20261028';out.mkdir(exist_ok=True)
kernels=out/'kernels';spec=kernels/'gaitana-validacion-local';spec.mkdir(parents=True,exist_ok=True)
(spec/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],
    'display_name':'La Gaitana · entorno validado','language':'python'}),encoding='utf-8')
manager=KernelManager(kernel_name='gaitana-validacion-local',kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernels)]))
nb=nbformat.read(path,as_version=4)
client=NotebookClient(nb,km=manager,timeout=3600,resources={'metadata':{'path':str(LEGACY)}})
try:
    print('Ejecutando cuaderno 26 con fuentes locales validadas.',flush=True)
    client.execute()
finally:
    nbformat.write(nb,path)
    if manager.has_kernel:manager.shutdown_kernel(now=True)
assert (out/'verificacion_final.json').exists()
print((out/'resumen_ejecucion.json').read_text(encoding='utf-8'),flush=True)
