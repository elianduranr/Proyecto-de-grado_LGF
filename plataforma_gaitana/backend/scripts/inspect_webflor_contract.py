"""Consulta de sólo lectura: revisar el límite temporal del reporte sin secretos."""
from app.webflor import connect
with connect() as conn:
    cursor=conn.cursor()
    definition=cursor.execute("SELECT OBJECT_DEFINITION(OBJECT_ID(N'Reporte.InformeCorteInvVariedad'))").fetchval()
    if definition:
        for line in definition.splitlines():
            if any(word in line.lower() for word in ['getdate','fechainicial','fechafinal','between']):print(line.strip())
    else:print('Definición no accesible con la cuenta de lectura.')
    print('Fecha actual del servidor:',cursor.execute('SELECT CAST(GETDATE() AS date)').fetchval())
    conn.rollback()
