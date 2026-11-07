"""Execute a trusted, frozen notebook in an isolated snapshot, never a user upload."""
import ast
import json
import os
import sys
from pathlib import Path


class ConfigureRebuild(ast.NodeTransformer):
    def __init__(self, value):
        self.value = value

    def visit_Assign(self, node):
        if any(isinstance(t, ast.Name) and t.id == 'RECALCULAR_DESDE_EXCEL' for t in node.targets):
            node.value = ast.Constant(self.value)
        return node


class SerialXmlReaders(ast.NodeTransformer):
    def visit_Call(self,node):
        self.generic_visit(node)
        if isinstance(node.func,ast.Name) and node.func.id=='ThreadPoolExecutor':
            for keyword in node.keywords:
                if keyword.arg=='max_workers':keyword.value=ast.Constant(1)
        return node


class WorkspaceRoot(ast.NodeTransformer):
    def visit_Assign(self,node):
        if any(isinstance(target,ast.Name) and target.id=='ROOT' for target in node.targets):
            node.value=ast.Name(id='_ETL_ROOT',ctx=ast.Load())
        return node


class ProductionWindowReader(ast.NodeTransformer):
    def visit_Assign(self,node):
        self.generic_visit(node)
        if any(isinstance(t,ast.Subscript) and isinstance(t.value,ast.Name) and t.value.id=='df'
               and isinstance(t.slice,ast.Constant) and t.slice.value=='fila_excel' for t in node.targets):
            # El filtro conserva el índice original; la traza debe señalar la fila
            # del Excel archivado y no la posición después de retirar una ventana.
            node.value=ast.parse('df.index.to_numpy()+2',mode='eval').body
        return node

    def visit_Call(self,node):
        self.generic_visit(node)
        if (isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name)
            and node.func.value.id=='pd' and node.func.attr=='read_excel'):
            node.func=ast.Name(id='_production_read_excel',ctx=ast.Load())
        return node


class BatchEstimateXml(ast.NodeTransformer):
    def visit_FunctionDef(self,node):
        if node.name!='leer_estimado_cache':return node
        node.decorator_list.append(ast.Name(id='_cached_estimate_reader',ctx=ast.Load()))
        for statement in ast.walk(node):
            if not isinstance(statement,ast.With):continue
            expression=statement.items[0].context_expr
            if (isinstance(expression,ast.Call) and isinstance(expression.func,ast.Attribute)
                and expression.func.attr=='open' and expression.args
                and isinstance(expression.args[0],ast.Name) and expression.args[0].id=='records'):
                statement.body=ast.parse('filas.extend(_estimated_rows(libro, records, ns, columnas, compartidos, pos_tipo, valor, texto))').body
        return node


def main():
    notebook, workspace, rebuild = sys.argv[1:]
    os.environ['MPLBACKEND'] = 'Agg'
    os.chdir(workspace)
    import matplotlib.pyplot as plt
    import IPython.display
    IPython.display.display = lambda *args, **kwargs: None
    plt.show = lambda *args, **kwargs: plt.close('all')
    document = json.loads(Path(notebook).read_text(encoding='utf-8'))
    from .xml_estimates import estimated_rows,cache_reader
    from .config import STORAGE
    import hashlib
    notebook_hash=hashlib.sha256(Path(notebook).read_bytes()).hexdigest()
    full_root=str(Path(workspace).resolve())
    if os.name=='nt' and not full_root.startswith('\\\\?\\'):
        full_root='\\\\?\\'+full_root
    namespace = {'__name__': '__main__','_ETL_ROOT':Path(full_root),'_estimated_rows':estimated_rows,
                 '_cached_estimate_reader':cache_reader(STORAGE/'etl_cache',notebook_hash)}
    production=Path(notebook).stem=='05_limpieza_produccion_real'
    if production:
        from .production_windows import reader
        namespace['_production_read_excel']=reader(Path(full_root))
    for i, cell in enumerate(document['cells']):
        if cell['cell_type'] != 'code':
            continue
        print(f'Celda {i}: {Path(notebook).stem}', flush=True)
        tree = ast.parse(''.join(cell['source']), filename=notebook)
        # lxml iterparse across Python threads causes severe GIL contention on Windows.
        # Scheduling only: identical functions, values, file order and assertions.
        tree = SerialXmlReaders().visit(tree)
        tree = BatchEstimateXml().visit(tree)
        tree = WorkspaceRoot().visit(tree)
        if production:tree=ProductionWindowReader().visit(tree)
        if rebuild in ('true', 'false'):
            tree = ConfigureRebuild(rebuild == 'true').visit(tree)
        exec(compile(ast.fix_missing_locations(tree), notebook, 'exec'), namespace)
        plt.close('all')


if __name__ == '__main__':
    main()
