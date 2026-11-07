"""Añade una aclaración de lectura sin ejecutar ni cambiar el código del cuaderno 19."""
from pathlib import Path
import nbformat

root=Path(__file__).resolve().parents[3]
path=root/'Notebooks/Analisis/19_modelos_clima_y_curvas_gaitana.ipynb'
nb=nbformat.read(path,as_version=4)
marker='revision-temporal-cuaderno26'
if not any(c.get('id')==marker for c in nb.cells):
    cell=nbformat.v4.new_markdown_cell('''## Lectura de esta evaluación y su ampliación

Este cuaderno conserva la selección y las predicciones retrospectivas originales. Sus cifras no se sustituyen al recibir fuentes nuevas. **Train de cada ajuste** sólo incluye objetivos terminados antes de su corte; la **validación temporal de noviembre–diciembre de 2025** escogió la variante y la **prueba retrospectiva de 2026** mide resultados fuera de cada ajuste. El proyecto ya ha examinado esos períodos: no se presentan como una prueba prospectiva intacta ni como un reparto aleatorio 80/20.

La ampliación ejecutada, sus fechas y porcentajes por corte, el contraste mensual/congelado y las métricas train/test del mismo ajuste están en [26_validacion_temporal_actualizada_y_operacion.ipynb](26_validacion_temporal_actualizada_y_operacion.ipynb). Ese cuaderno conserva la configuración Sin_clima y distingue la referencia hasta S36 de los objetivos posteriores. Una semana evaluada puede incorporarse al train de un ajuste posterior cuando ya terminó, sin que su respuesta haya sido conocida por el modelo que la predijo.

La aplicación distingue evaluación archivada, evaluación retrospectiva actualizada y seguimiento de publicaciones anticipadas. Cargar fuentes o recalcular errores no convierte un borrador retrospectivo en un pronóstico emitido antes de conocer la cosecha.''')
    cell['id']=marker;nb.cells.append(cell);nbformat.write(nb,path)
    print('Aclaración añadida; código y salidas del 19 conservados.')
