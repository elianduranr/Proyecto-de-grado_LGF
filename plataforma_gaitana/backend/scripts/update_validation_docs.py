"""Resumen y ruta de estudio basados exclusivamente en la ejecución comprobada del 26."""
import json,sys,time
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.config import LEGACY,STORAGE

OUT=LEGACY/'Datos_analiticos_proyecto/validacion_temporal_20261028'
assert json.loads((OUT/'verificacion_final.json').read_text(encoding='utf-8'))['passed']
summary=json.loads((OUT/'resumen_ejecucion.json').read_text(encoding='utf-8'))
sql_check=STORAGE/'verification_sql_evaluacion_20261028.json'
if not sql_check.exists():print('Esperando comprobación de persistencia SQL antes de actualizar el estado operativo.',flush=True)
while not sql_check.exists():time.sleep(10)
sql=json.loads(sql_check.read_text(encoding='utf-8'))
assert sql['passed'] and sql['dataset_id']==summary['snapshot']
metrics=pd.read_csv(OUT/'metricas_comparadas.csv',dtype={'horizonte':str})
d=metrics.loc[metrics.periodo.eq('extension_desde_S37')&metrics.comparacion.eq('19_mensual_sin_clima')]
def n(x):return f'{x:.2f}'.replace('.',',')
rows=[]
for h in ['1','2','3','4','5','Total']:
    m=d.loc[d.metodo.eq('19_mensual_sin_clima')&d.horizonte.eq(h)].iloc[0]
    e=d.loc[d.metodo.eq('Ingeniero')&d.horizonte.eq(h)].iloc[0]
    rows.append(f'| {"H"+h if h!="Total" else "Conjunto"} | {int(m.casos)} | {n(m.WAPE)} % | {n(e.WAPE)} % | {n(m.sesgo_pct)} % | {n(e.sesgo_pct)} % |')
annual=pd.read_csv(OUT/'metricas_2026_completo.csv',dtype={'horizonte':str})
annual_rows=[]
for h in ['1','2','3','4','5','Total']:
    m=annual.loc[annual.metodo.eq('19_mensual_sin_clima')&annual.horizonte.eq(h)].iloc[0]
    e=annual.loc[annual.metodo.eq('Ingeniero')&annual.horizonte.eq(h)].iloc[0]
    annual_rows.append(f'| {"H"+h if h!="Total" else "Conjunto"} | {int(m.casos)} | {n(m.WAPE)} % | {n(e.WAPE)} % | {n(m.sesgo_pct)} % | {n(e.sesgo_pct)} % |')
section=f'''## Evaluación ampliada del 28/10/2026 · cuaderno 26

Se conserva **Boosting sin clima del cuaderno 19**: dos grupos H1–H2 y H3–H5; cada uno corrige Media4 o teoría según corresponda. Mismos parámetros, sin nuevo tuneo. Se reconstruyeron las fuentes hasta el corte del 27/10 y se evaluaron **{summary['semanas_objetivo']} semanas objetivo distintas**, desde {summary['objetivo_desde']} hasta {summary['objetivo_hasta']}. La semana en curso no se evalúa como completa.

**Año ISO 2026 completo, comparación nominal sobre los mismos casos:**

| Horizonte | Casos comunes | WAPE modelo | WAPE ingeniero | Sesgo modelo | Sesgo ingeniero |
| --- | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(annual_rows)}

**Panel posterior a S36, comparación nominal sobre los mismos casos:**

| Horizonte | Casos comunes | WAPE modelo | WAPE ingeniero | Sesgo modelo | Sesgo ingeniero |
| --- | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

Sesgo firmado = predicción menos real, dividido por real total. El cuaderno también informa MAE, RMSE, MAPE sobre reales positivos, ±8 %, saldo neto en tallos, métricas train/test del mismo ajuste y contraste con el ajuste congelado al 03/08.

**Separación temporal:** cada ajuste sólo entrena con objetivos terminados antes de su corte mensual; la imputación y codificación se ajustan dentro de train. Una semana de prueba puede incorporarse a un ajuste posterior cuando ya terminó, sin haber sido conocida por el modelo que la pronosticó. No hay reparto aleatorio ni porcentaje global 80/20. Las fechas, casos y porcentajes de cada ajuste están en `particiones_por_corte.csv`.

Esta comprobación es **retrospectiva**: no equivale a publicaciones anticipadas ni vuelve a seleccionar el modelo. La validación 2025 y la referencia original de 2026 se conservan. La comparación con idéntico corte informativo del jueves sigue pendiente. El pronóstico diario conserva su evaluación anterior y sigue en revisión; no se reentrenó en esta actualización.

Archivos: `Notebooks/Analisis/26_validacion_temporal_actualizada_y_operacion.ipynb`, resultados en `Datos_analiticos_proyecto/validacion_temporal_20261028/` e informe `Trabajo escrito/Documento_LaGaitana_v8_validacion_temporal_actualizada_20261028.docx` (también PDF).
'''
path=LEGACY/'resumen_modelos_pronostico.md'
text=path.read_text(encoding='utf-8')
marker='## Evaluación ampliada del 28/10/2026 · cuaderno 26'
historical='## Referencia histórica conservada · evaluación original hasta S36'
if marker in text:
    a=text.index(marker);b=text.index(historical,a);text=text[:a]+text[b:]
text=text.replace('## Semanales',historical,1)
first,rest=text.split(historical,1)
first=first.replace('benchmark semanal actualizado al 22 de octubre de 2026','evaluación actualizada al 28 de octubre de 2026')
path.write_text(first.rstrip()+'\n\n'+section+'\n\n'+historical+rest,encoding='utf-8')

study='''## Actualización del 28/10/2026: evaluación temporal y operación

Lectura corta: informe v8, 4.2.8 (train/validación/test y reentrenamiento), 5.1.3 (datos y resultados nuevos), 5.5 (train/test del mismo ajuste) y conclusiones por objetivo. Los demás modelos y el diario conservan sus resultados históricos, identificados como tales.

Reproducción de esta actualización:
1. Conservar la copia versionada `plataforma_gaitana/storage/datasets/evaluacion_local_20261028` y su manifiesto; no cambiar originales para repetir resultados.
2. Ejecutar `26_validacion_temporal_actualizada_y_operacion.ipynb` de arriba abajo con el entorno de `plataforma_gaitana/.venv`. Reutiliza las funciones del 19 y no requiere consultar SQL ni WebFlor para calcular los errores.
3. Revisar `fuentes_validadas.csv`, `cortes_entrenamiento.csv`, `particiones_por_corte.csv`, `train_test_por_ajuste.csv`, `auditoria_semanas.csv` y `verificacion_final.json`.
4. Para regenerar el informe: `actualizar_documento_v8.py`, `generar_documento_v8.py`, `verificar_revision_v8.py` y `exportar_revision_v8_pdf.py`, en ese orden. Los tres últimos usan `entorno_tesis` (Word se abre oculto para exportar PDF).

En el visualizador, «Evaluación actualizada · cuaderno 26» conserva las predicciones y recalcula errores contra la última versión validada de real/ingeniero. «Prueba 2026 · cuadernillo 19» mantiene el archivo de referencia. «Entrenamiento» muestra H1 dentro de muestra y «Seguimiento» exige publicaciones anticipadas. Cargar más datos no inventa predicciones para orígenes no evaluados: para ampliarlos se vuelve a ejecutar la evaluación o se conservan nuevas publicaciones.

El comparador identifica con color quién tuvo menor WAPE y permite regresar de variedad a color y producto. La revisión manual de una propuesta conserva por separado el error original y ajustado; no modifica el benchmark nominal del ingeniero.

En «Generar y ajustar», producto → color → variedades permite comparar varias selecciones, cambiar semanas y ocultar curvas. El checklist se guarda en la propuesta: seleccionar no confirma revisión. Marcar revisada registra aceptación o ajuste de las cinco semanas; cambiar cantidades vuelve a dejar pendientes las variedades afectadas. El avance por producto/color sólo se completa al revisar todas sus variedades. La curva por edad utiliza el resultado normalizado existente; el suavizado de la proyección absoluta es únicamente visual.
'''
for relative in ['GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md','BITACORA_REVISION_CONVERSADA.md']:
    p=LEGACY/relative;s=p.read_text(encoding='utf-8');marker='## Actualización del 28/10/2026: evaluación temporal y operación'
    if marker in s:s=s[:s.index(marker)]
    if relative.startswith('GUIA_'):
        s=s.replace('Trabajo%20escrito/Estructura_documento_v4_oct222026.docx','Trabajo%20escrito/Documento_LaGaitana_v8_validacion_temporal_actualizada_20261028.docx')
        s=s.replace('Trabajo%20escrito/Desarrollo_del_documento.md','Trabajo%20escrito/Documento_LaGaitana_v8_validacion_temporal_actualizada_20261028.md')
        s=s.replace('## Resultado actual','## Resultado de referencia conservado · hasta S36')
        s=s.replace('## Qué leer primero','## Evaluación más reciente\n\nEl cuaderno 26 amplía la comprobación temporal hasta '+summary['objetivo_hasta']+'. Ver la sección final de esta guía para resultados, train/test y orden de reproducción. Las cifras de la sección de referencia siguiente pertenecen al panel original.\n\n## Qué leer primero',1) if '## Evaluación más reciente' not in s else s
    p.write_text(s.rstrip()+'\n\n'+study,encoding='utf-8')
for relative in ['Trabajo escrito/LEEME.md','LEEME.md']:
    p=LEGACY/relative;s=p.read_text(encoding='utf-8')
    note='Edición más reciente: **[Documento_LaGaitana_v8_validacion_temporal_actualizada_20261028.docx]('+('' if relative.startswith('Trabajo') else 'Trabajo%20escrito/')+'Documento_LaGaitana_v8_validacion_temporal_actualizada_20261028.docx)**, con PDF y Markdown del mismo nombre. Incluye la evaluación ejecutada del cuaderno 26, particiones temporales y operación mensual. La v7 se conserva como referencia.'
    if 'Edición más reciente: **[Documento_LaGaitana_v8_' not in s:
        s=s.replace('La versión vigente para revisión del profesor es','La edición anterior para revisión del profesor es',1)
        s=s.replace('### Tesis: versión 7 para revisión académica','### Referencia conservada: versión 7 para revisión académica')
        lines=s.splitlines();lines.insert(2,note+'\n')
        p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
p=LEGACY/'Notebooks/Analisis/README.md';s=p.read_text(encoding='utf-8')
note='\n\n26_validacion_temporal_actualizada_y_operacion.ipynb amplía la evaluación del 19 con fuentes versionadas hasta octubre: fechas y porcentajes por corte, train/validación/test, contraste mensual/congelado, WAPE y sesgo por horizonte y limitaciones. Es el último paso de comprobación semanal; los análisis 20–25 conservan su carácter histórico. No reentrena los modelos diarios.\n'
if '26_validacion_temporal_actualizada_y_operacion.ipynb' not in s:p.write_text(s.rstrip()+note,encoding='utf-8')
p=LEGACY/'plataforma_gaitana/ESTADO_PROTOTIPO.md';s=p.read_text(encoding='utf-8')
marker='## Comprobación actualizada del 28/10/2026'
if marker not in s:
    current=f'''{marker}

Datos activos: `{summary['snapshot']}`, con producción hasta el 27/10. Persistencia SQL EP verificada contra las cinco fuentes limpias: conteos y total de tallos coinciden con Parquet. Evidencia: `storage/verification_sql_evaluacion_20261028.json`.

El cuaderno 26 ejecutado evalúa {summary['semanas_objetivo']} semanas objetivo hasta {summary['objetivo_hasta']}; conserva configuración, separaciones temporales, controles por corte y contraste mensual/congelado. El histórico actualizado usa esa evaluación y las últimas fuentes validadas; la prueba original sigue accesible por separado.

El frontend compila y se aprobaron las pruebas del backend para comparación, actualización de métricas, ajustes, revisión persistente e invalidación de checks afectados. Las verificaciones de navegador registran selección múltiple de variedades, rango de semanas, controles de curvas, navegación de regreso y ausencia de desbordamiento móvil. Evidencia: `storage/verification_review_ui.json` y `storage/verification_comparison_navigation.json`.

La lista siguiente conserva la evidencia del cierre anterior del 26/10; sus cantidades y fechas se interpretan como referencia histórica, no como la fuente activa actual.

'''
    s=s.replace('## Comprobaciones ejecutadas',current+'## Comprobaciones ejecutadas · referencia del 26/10',1)
    s=s.replace('Actualización: 26 de octubre de 2026. Carga inicial y actualización desde WebFlor terminadas; comprobaciones indicadas abajo.',
        'Actualización: 28 de octubre de 2026. Evaluación temporal ampliada, fuentes nuevas activadas en SQL y controles de revisión comprobados.')
    p.write_text(s,encoding='utf-8')
print(section)
