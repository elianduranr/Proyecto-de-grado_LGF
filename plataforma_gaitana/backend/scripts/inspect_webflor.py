"""Read-only discovery of the production report; no report execution or writes."""
import json
from app.config import STORAGE
from app.webflor import connect as connection


def rows(cursor):
    names = [column[0] for column in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def main():
    with connection() as conn:
        cursor = conn.cursor()
        objects = rows(cursor.execute("SELECT o.object_id, s.name AS schema_name, o.name, o.type, o.type_desc, o.modify_date FROM sys.objects o JOIN sys.schemas s ON s.schema_id=o.schema_id WHERE s.name=? AND o.name=?", 'Reporte', 'InformeCorteInvVariedad'))
        if len(objects) != 1:
            raise RuntimeError('No se identificó un único objeto visible Reporte.InformeCorteInvVariedad.')
        obj = objects[0]
        obj['columns'] = rows(cursor.execute('SELECT c.column_id,c.name,t.name AS data_type,c.max_length,c.is_nullable FROM sys.columns c JOIN sys.types t ON t.user_type_id=c.user_type_id WHERE c.object_id=? ORDER BY c.column_id', obj['object_id']))
        obj['parameters'] = rows(cursor.execute('SELECT p.parameter_id,p.name,t.name AS data_type,p.max_length,p.is_output,p.has_default_value FROM sys.parameters p JOIN sys.types t ON t.user_type_id=p.user_type_id WHERE p.object_id=? ORDER BY p.parameter_id', obj['object_id']))
        obj['definition'] = cursor.execute('SELECT OBJECT_DEFINITION(?)', obj['object_id']).fetchval()
        if obj['type'].strip() in ['V', 'U']:
            obj['sample'] = rows(cursor.execute('SELECT TOP (5) * FROM [Reporte].[InformeCorteInvVariedad]'))
        conn.rollback()
    path = STORAGE / 'webflor_discovery.json'
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    print(json.dumps({key: obj[key] for key in ['schema_name', 'name', 'type_desc', 'columns', 'parameters']}, ensure_ascii=False, indent=2), flush=True)
    print('Detalle privado guardado en storage/webflor_discovery.json', flush=True)


if __name__ == '__main__':
    main()
