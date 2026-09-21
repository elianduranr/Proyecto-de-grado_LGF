"""Ejecuta el notebook 05 completo con el mismo Python del entorno activo."""
from pathlib import Path
import os
import sys
import json
import tempfile
import nbformat
from nbclient import NotebookClient

root=Path(__file__).resolve().parents[1]
path=root/'Notebooks/05_MCA_2026.ipynb'
notebook=nbformat.read(path,as_version=4)
with tempfile.TemporaryDirectory(prefix='kernel_mca_') as directory:
    kernel=Path(directory)/'kernels/mca_entorno'
    kernel.mkdir(parents=True)
    (kernel/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],
                                                'display_name':'Python entorno tesis','language':'python'}),encoding='utf-8')
    os.environ['JUPYTER_PATH']=directory+os.pathsep+os.environ.get('JUPYTER_PATH','')
    os.environ['IPYTHONDIR']=str(Path(directory)/'ipython')
    def progress(cell,cell_index):
        print(f'Celda {cell_index}: '+''.join(cell.source).splitlines()[0][:100],flush=True)
    client=NotebookClient(notebook,timeout=1200,kernel_name='mca_entorno',
                          resources={'metadata':{'path':str(root/'Notebooks')}},on_cell_execute=progress)
    try:
        client.execute()
    finally:
        nbformat.write(notebook,path)
    # Exportar una lectura HTML estática con las mismas salidas calculadas.
    from nbconvert import HTMLExporter
    exporter=HTMLExporter()
    html,_=exporter.from_notebook_node(notebook)
    out=root/'Notebooks/informes/mca_gaitana/analisis_mca_gaitana.html'
    out.write_text(html,encoding='utf-8')
    print('Notebook ejecutado y HTML exportado:',out,flush=True)
