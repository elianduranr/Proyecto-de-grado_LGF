"""Reproduce la entrega académica v9 sin modificar datos/modelos ni pedir VPN."""
from pathlib import Path
import sys,subprocess,json
from revision_v9_config import NAME
F=Path(__file__).resolve().parent;R=F.parent;O=F/'Revision_v9';logs=O/'Logs';logs.mkdir(exist_ok=True)
scripts=['inspeccionar_revision_v9.py','evidencia_revision_v9.py','construir_revision_v9.py','generar_documento_v9.py','exportar_revision_v9_pdf.py','verificar_revision_v9.py','registrar_cumplimiento_v9.py']
for script in scripts:
    print('Ejecutando:',script,flush=True)
    result=subprocess.run([sys.executable,str(F/script)],cwd=R,capture_output=True,text=True,encoding='utf8',errors='replace')
    (logs/(Path(script).stem+'.log')).write_text(result.stdout+'\n'+result.stderr,encoding='utf8')
    if result.returncode:raise RuntimeError(f'{script} falló. Revisar {logs / (Path(script).stem+".log")}')
report=json.loads((O/'verificacion_final.json').read_text(encoding='utf8'))
print(json.dumps({'word':str(F/(NAME+'.docx')),'pdf':str(F/(NAME+'.pdf')),'paginas':report['paginas_pdf'],'verificado':report['passed']},ensure_ascii=False),flush=True)
