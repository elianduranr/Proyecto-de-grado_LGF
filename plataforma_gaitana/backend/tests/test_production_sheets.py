"""Protect the production-sheet contract that previously omitted new cuts."""
import ast
import json
import re
from pathlib import Path

import pandas as pd
import pytest


def selector():
    path = (Path(__file__).resolve().parents[3] / 'Notebooks' /
            'Limpieza data, Notebooks y Scripts' / '05_limpieza_produccion_real.ipynb')
    notebook = json.loads(path.read_text(encoding='utf-8'))
    code = '\n'.join(''.join(cell['source']) for cell in notebook['cells'] if cell['cell_type'] == 'code')
    node = next(node for node in ast.parse(code).body
                if isinstance(node, ast.FunctionDef) and node.name == 'seleccionar_hojas_detalle')
    namespace = {'pd': pd, 'HOJAS': {2025: ['BD'], 2026: ['BD']},
                 'texto': lambda value: str(value).strip().upper()}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), namespace)
    return namespace['seleccionar_hojas_detalle']


def test_new_production_detail_is_included_but_pivot_totals_are_not(tmp_path):
    path = tmp_path / 'production.xlsx'
    # Small test fixtures only; never input to the application or its model.
    detail = pd.DataFrame({'FINCA': ['TEST'], 'FECHA CORTE': [pd.Timestamp('2026-10-10')],
                           'PRODUCTO': ['TEST'], 'COLOR': ['TEST'], 'VARIEDAD': ['TEST'], 'TALLOS': [10]})
    with pd.ExcelWriter(path) as writer:
        detail.to_excel(writer, sheet_name='BD', index=False)
        detail.to_excel(writer, sheet_name='Hoja1', index=False)
        pd.DataFrame({'PRODUCTO': ['TEST'], 'SUMA DE TALLOS': [10]}).to_excel(writer, sheet_name='Resumen', index=False)
    with pd.ExcelFile(path) as book:
        assert selector()(book, 2026) == (['BD', 'Hoja1'], ['Hoja1'])
        assert selector()(book, 2025) == (['BD'], [])


def test_missing_historical_detail_sheet_is_rejected(tmp_path):
    path = tmp_path / 'missing.xlsx'
    pd.DataFrame({'TOTAL': [10]}).to_excel(path, sheet_name='Resumen', index=False)
    with pd.ExcelFile(path) as book, pytest.raises(ValueError, match='Faltan hojas de detalle'):
        selector()(book, 2026)


def test_notebook_preview_accepts_incremental_2026_as_first_sorted_file(tmp_path):
    path=tmp_path/'2026_additional.xlsx'
    pd.DataFrame({'FINCA':['TEST'],'TALLOS':[10]}).to_excel(path,sheet_name='BD',index=False)
    notebook_path=(Path(__file__).resolve().parents[3]/'Notebooks'/'Limpieza data, Notebooks y Scripts'/'05_limpieza_produccion_real.ipynb')
    notebook=json.loads(notebook_path.read_text(encoding='utf-8'))
    code=next(''.join(cell['source']) for cell in notebook['cells'] if cell['cell_type']=='code' and 'primero = pd.read_excel' in ''.join(cell['source']))
    namespace={'pd':pd,'re':re,'archivos':[path],'HOJAS':{2026:['BD']},'display':lambda value:None}
    exec(compile(code,str(notebook_path),'exec'),namespace)
    assert namespace['primero'].TALLOS.tolist()==[10]
