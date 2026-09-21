"""Ejecuta el notebook 03 desde la celda de producción y conserva sus celdas previas."""
from pathlib import Path
import tempfile
import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'Notebooks' / '03_benchmark_estimado_ingeniero.ipynb'
nb = nbformat.read(path, as_version=4)
# La celda 1 importa pandas/numpy/matplotlib. La celda 10 lee el Excel 2026 nuevo.
indices = [1] + list(range(10, len(nb.cells)))
run = nbformat.v4.new_notebook(cells=[nb.cells[i] for i in indices], metadata=nb.metadata)
with tempfile.TemporaryDirectory() as td:
    temp = Path(td) / 'ejecucion03.ipynb'
    nbformat.write(run, temp)
    client = NotebookClient(run, timeout=1200, kernel_name='python3', resources={'metadata': {'path': str(ROOT / 'Notebooks')}})
    client.execute(cwd=str(ROOT / 'Notebooks'))
    # Copiar resultados ejecutados a las posiciones originales: la estructura no cambia.
    for original_index, executed_cell in zip(indices, run.cells):
        nb.cells[original_index] = executed_cell
nbformat.write(nb, path)
print('Notebook 03 actualizado desde la celda de producción:', path)
