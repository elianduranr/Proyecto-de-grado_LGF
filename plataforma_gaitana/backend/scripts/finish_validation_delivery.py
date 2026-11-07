"""Completar documentación únicamente después de la evaluación ejecutada, sin inventar cifras."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
from app.config import LEGACY,STORAGE

folder=LEGACY/'Trabajo escrito'
out=LEGACY/'Datos_analiticos_proyecto/validacion_temporal_20261028'
baseline={p.name:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
          for p in folder.glob('Documento_LaGaitana_v7_revision_profesor_20261028.*')}
(STORAGE/'v7_before_validation_delivery.json').write_text(json.dumps(baseline,indent=2),encoding='utf-8')
while not (out/'verificacion_final.json').exists():time.sleep(10)
assert json.loads((out/'verificacion_final.json').read_text(encoding='utf-8'))['passed']
thesis_python=LEGACY/'entorno_tesis/Scripts/python.exe'
env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONPATH':str(Path(__file__).resolve().parents[1])}
steps=[(sys.executable,folder/'actualizar_documento_v8.py'),
       (thesis_python,folder/'generar_documento_v8.py'),
       (thesis_python,folder/'verificar_revision_v8.py'),
       (thesis_python,folder/'exportar_revision_v8_pdf.py'),
       (sys.executable,Path(__file__).with_name('update_validation_docs.py'))]
for python,script in steps:
    print('DOCUMENTACIÓN:',script.name,flush=True)
    subprocess.run([str(python),str(script)],cwd=LEGACY,env=env,check=True)
assert all(hashlib.file_digest((folder/name).open('rb'),'sha256').hexdigest()==digest for name,digest in baseline.items())
print('Versión 8 generada, verificada y exportada; versión 7 conservada.',flush=True)
