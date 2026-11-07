import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT / '.env')

def resolve(value: str) -> Path:
    p = Path(value)
    return p.resolve() if p.is_absolute() else (PROJECT / p).resolve()

LEGACY = resolve(os.getenv('LEGACY_ROOT', '..'))
STORAGE = resolve(os.getenv('STORAGE_PATH', './storage'))
STORAGE.mkdir(parents=True, exist_ok=True)
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{(STORAGE / "prototipo.db").as_posix()}')
if os.getenv('SQL_SERVER'):
    from sqlalchemy.engine import URL
    DATABASE_URL=URL.create('mssql+pyodbc',username=os.getenv('SQL_USER'),password=os.getenv('SQL_PASSWORD'),
        host=os.getenv('SQL_SERVER'),database=os.getenv('SQL_DATABASE','proyectos'),
        query={'driver':os.getenv('SQL_DRIVER','ODBC Driver 18 for SQL Server'),
               'Encrypt':'yes','TrustServerCertificate':os.getenv('SQL_TRUST_CERTIFICATE','no')}).render_as_string(hide_password=False)
if DATABASE_URL.startswith('sqlite:///./'):
    DATABASE_URL = 'sqlite:///' + (PROJECT / DATABASE_URL[10:]).resolve().as_posix()
DEV_MODE = os.getenv('DEV_MODE', 'true').lower() == 'true'
TOKENS = {os.getenv(name): role for name, role in [
    ('API_ADMIN_TOKEN','administrador'), ('API_ENGINEER_TOKEN','ingeniero'), ('API_VIEWER_TOKEN','consulta')
] if os.getenv(name)}
if not DEV_MODE and not TOKENS:
    raise RuntimeError('Configure tokens de acceso antes de desactivar DEV_MODE.')
CORS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
