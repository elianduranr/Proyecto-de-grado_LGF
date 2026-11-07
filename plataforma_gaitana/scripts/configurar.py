"""Configuración local inicial, sin escribir secretos en archivos versionados."""
from pathlib import Path
import secrets

root=Path(__file__).resolve().parents[1]
env=root/'.env'
if not env.exists():
    text=(root/'.env.example').read_text(encoding='utf-8')
    for name in ['API_ADMIN_TOKEN','API_ENGINEER_TOKEN','API_VIEWER_TOKEN']:
        text=text.replace(name+'=\n',name+'='+secrets.token_urlsafe(32)+'\n')
    env.write_text(text,encoding='utf-8')
    print('Creado .env local. Los tokens se encuentran sólo en ese archivo; no se suben a Git.')
else:print('Se conserva la configuración .env existente.')
(root/'storage').mkdir(exist_ok=True)

