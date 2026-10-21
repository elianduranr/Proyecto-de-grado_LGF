"""Actualizar cifras y figuras del escrito a partir de notebooks ya ejecutados.

Ejecutar desde la raíz, después de la cadena de la guía. No entrena modelos.
La comparación de octubre usa la copia conservada antes de corregir los cruces;
no debe confundirse con el experimento histórico de actualización del clima.
"""
from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import nbformat

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'Trabajo escrito'
DATA = ROOT / 'Datos_analiticos_proyecto'
PROY = ROOT / 'Notebooks/Proyecciones Teoricas Propias/resultados_todos_los_anios'
REV = DATA / 'revision_cruces_20261019'
ANTES = REV / 'antes'
MODEL = DATA / 'modelo_con_proyecciones_teoricas'
CLIMA = DATA / 'revision_clima_finca'
DIARIO = DATA / 'modelo_diario'
FIG = DOC / 'Figuras_resultados'
KEY = ['finca', 'producto', 'color', 'variedad', 'origen', 'semana_objetivo', 'horizonte']

def num(x, digits=2):
    if pd.isna(x): return '—'
    return f'{x:,.{digits}f}'.replace(',', '@').replace('.', ',').replace('@', '.')

def pct(x): return num(100 * x) + ' %'

def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(map(str, r)) + ' |' for r in rows])

def excel(path, sheet): return pd.read_excel(path, sheet_name=sheet)

def metrics(d, col):
    e = d[col] - d.y
    return {'n': len(d), 'WAPE': e.abs().sum() / d.y.sum(), 'sesgo_pct': 100 * e.sum() / d.y.sum(),
            'MAE': e.abs().mean(), 'sesgo': e.mean()}

names = {
    'Sin_clima': 'Boosting sin clima', 'Clima_basico': 'Boosting con clima básico',
    'Clima_ampliado': 'Boosting con clima ampliado y lluvia',
    'Curva_Gaitana_clima': 'Boosting con clima ampliado y curva atribuida a GAITANA',
    'Antes_actualizar_clima': 'Referencia histórica anterior al clima actualizado',
    'ingeniero': 'Ingeniero', 'Boosting_clima': 'Boosting diario reconciliado con selección semanal',
    'Boosting_diario': 'Boosting diario autónomo', 'Boosting_memoria': 'Boosting reconciliado con memoria semanal',
    'Perfil_clima': 'Perfil histórico con selección semanal', 'Perfil_memoria': 'Perfil histórico con memoria semanal',
    'Uniforme_clima': 'Uniforme con selección semanal', 'Uniforme_memoria': 'Uniforme con memoria semanal',
    'Autonomo_antes_clima': 'Autónomo: referencia histórica anterior al clima',
    'Reconciliado_antes_clima': 'Reconciliado: referencia histórica anterior al clima',
    'SARIMA_clima': 'SARIMA reconciliado con selección semanal',
    'SARIMAX_clima': 'SARIMAX reconciliado con selección semanal',
}

def metric_table(d):
    return table(['Método', 'Casos', 'MAE (tallos)', 'WAPE', 'Sesgo (%)'],
                 [[names.get(r.modelo, r.modelo), num(r.n, 0), num(r.MAE), pct(r.WAPE), num(r.sesgo_pct) + ' %']
                  for r in d.itertuples(index=False)])

text = (DOC / 'Desarrollo_del_documento.md').read_text(encoding='utf-8')

def section(start, end, body):
    global text
    a, b = text.index(start), text.index(end, text.index(start) + len(start))
    text = text[:a] + start + '\n\n' + body.strip() + '\n\n' + text[b:]

def paragraph(prefix, replacement):
    global text
    pat = re.compile(r'^' + re.escape(prefix) + r'[^\n]*(?:\n(?!\n)[^\n]+)*', re.M)
    text, count = pat.subn(lambda _: replacement, text)
    if count == 0 and replacement in text: return
    if count != 1: raise ValueError(f'Párrafo esperado una vez: {prefix!r}; encontrados {count}')

# Correspondencias: universo fuente y período reciente, sin confundirlos con la base del modelo.
audit = pd.read_parquet(PROY / 'auditoria_calidad/resumen_recuperacion.parquet')
est = pd.read_parquet(PROY / '2026/estadisticas_auditoria.parquet')
usable = pd.read_parquet(PROY / '2026/estadisticas.parquet')
old_est = pd.read_parquet(ANTES / '2026/estadisticas_auditoria.parquet')
old_usable = pd.read_parquet(ANTES / '2026/estadisticas.parquet')
assert est.id_estadistica.is_unique and len(est) == len(old_est)
assert set(old_usable.id_estadistica).issubset(set(usable.id_estadistica))
source_check = est[['id_estadistica', 'corte']].merge(old_est[['id_estadistica', 'corte']], on='id_estadistica', validate='one_to_one', suffixes=('', '_antes'))
assert np.allclose(source_check.corte, source_check.corte_antes, equal_nan=True)
recent = est.loc[est.fecha_corte.dt.year.eq(2026)]
joined = int(est.estado_union.eq('unica').sum())
recent_joined = int(recent.estado_union.eq('unica').sum())
residual_cuts = recent.loc[recent.estado_union.ne('unica'),'corte'].sum(min_count=1)
total_reported_cuts = recent.corte.sum(min_count=1)
residual_volume_pct = 100 * residual_cuts / total_reported_cuts
status = est.groupby('estado_union').size().rename('Historia de edición 2026').to_frame()
status['Cortes fechados en 2026'] = recent.groupby('estado_union').size()
status = status.fillna(0).astype(int)
status.to_csv(REV / 'correspondencias_2026.csv', encoding='utf-8-sig')
join_table = table(['Estado técnico', 'Historia de edición 2026', 'Cortes fechados en 2026'],
                   [[i, num(r.iloc[0], 0), num(r.iloc[1], 0)] for i, r in status.iterrows()])
audit_table = table(['Edición', 'Utilizables antes del 19/10', 'Utilizables después', 'Adicionales'],
                    [[int(r.anio), num(r.utilizables_antes_revision_oct19, 0), num(r.utilizables_despues, 0), num(r.recuperadas_revision_oct19, 0)] for r in audit.itertuples()])
proc = excel(CLIMA / 'auditoria_finca_curvas.xlsx', 'Procedencia_observaciones')
proc26 = proc.loc[proc.anio.eq(2026)]
gaitana = int(proc26.loc[proc26.finca_inferida.eq('GAITANA'), 'observaciones'].sum())
unattributed = int(proc26.loc[proc26.finca_inferida.isna(), 'observaciones'].sum())
section('### 3.1. Calidad e historia utilizable de los pilotos', '### 3.2. Cómo se obtiene y cómo se lee una curva', f'''
Las camas piloto identifican plantas y ciclos; sus estadísticas registran el corte de esas camas. Se normalizan nombres, espacios y mayúsculas, y se verifica referencia de cama, identidad comercial y ciclo de siembra. Esta correspondencia se mide antes de construir rendimientos por edad. No se utiliza el porcentaje de teoría completa de la base analítica como tasa de éxito de estas uniones. [E9]

La revisión del 19 de octubre conserva los {num(len(est), 0)} registros de estadísticas de la edición 2026 y sus cantidades originales. Hay {num(joined, 0)} correspondencias únicas. Al restringir a cortes fechados en 2026, {num(recent_joined, 0)} de {num(len(recent), 0)} tienen correspondencia única ({pct(recent_joined / len(recent))}). El total de la edición incluye años anteriores; no representa exclusivamente la operación de 2026.

{join_table}

Los estados restantes son controles de referencia, identidad o ciclo, no errores de pronóstico ni edades improductivas. Se mantienen trazables, sin convertirlos en un problema general de la fuente. En los 53 registros fechados en 2026 que siguen pendientes se reportan {num(residual_cuts,0)} tallos en conjunto ({num(residual_volume_pct)} % de los tallos anotados en esas estadísticas); al ser filas semanales repetidas, no representan tallos físicos únicos. Las observaciones utilizables deben además tener plantas positivas, fecha y edad válidas y corte no negativo. Se conservan los ceros registrados: la vista actual contiene {num(len(usable), 0)} observaciones, de las cuales {num(usable.corte.eq(0).sum(), 0)} tienen corte cero.

### 3.1.1. Corrección verificada de nombres y referencias equivalentes

Se encontró una pérdida evitable: la comparación de candidatos incluía campos originales con diferencias de mayúsculas. Así, dos copias de la misma cama y ciclo podían tratarse como alternativas. En el Excel de clavel 2026, las filas 5908 y 5931 de Camas Piloto corresponden a CAROLINE GOLD-26-3, con igual fecha de siembra y 1.194 plantas; sólo cambia la escritura en mayúsculas/minúsculas. Ahora se compara la identidad normalizada y los atributos del ciclo. Se consulta una sola referencia equivalente, conservando las filas fuente y sin duplicar movimientos de corte.

Cuando falta el nombre de variedad en estadísticas, sólo se recupera si la referencia completa dentro del mismo archivo identifica una única combinación comercial compatible con el producto. En la edición 2026 se recuperan así {num(est.identidad_recuperada_por_referencia.sum(), 0)} identidades. No se usa semejanza aproximada de nombres ni se mezclan colores o ciclos.

{audit_table}

Los libros anuales repiten historia: estas recuperaciones no se suman como observaciones únicas del cultivo. La corrección verifica conservación del corte y de todas las observaciones previamente utilizables, incluidas sus plantas, fechas y edades. Diferencias reales de denominador o fecha permanecen pendientes; no se elige un valor arbitrario. El catálogo común de 00 conserva identidad comercial y códigos de procedencia.

### 3.1.2. Procedencia de los pilotos

Las hojas de estadísticas no contienen la finca. La atribución a GAITANA requiere coincidencia de bloque, cama, identidad comercial y fecha de siembra con un plano. En la edición 2026, {num(gaitana, 0)} observaciones utilizables tienen coincidencia atribuible a GAITANA y {num(unattributed, 0)} no tienen esa evidencia. No hay coincidencia inequívoca con ARABELLA. Las cifras describen la procedencia comprobada; no permiten asignar los casos desconocidos a otra finca por descarte. [E14]

Las curvas compartidas del proyecto se mantienen para el alcance actual. La curva atribuida a GAITANA se evalúa como sensibilidad y su diferencia de cobertura o WAPE puede reflejar tanto qué pilotos entran como qué edades quedan representadas. No se interpreta esa comparación aislada como prueba de que una finca deba usar una curva propia.

Las curvas y proyecciones se recalculan antes de reconstruir la base y ajustar los modelos.
''')

base = pd.read_parquet(MODEL / 'base_analitica_proyecciones.parquet')
obs = base.loc[base.y.notna()]
old_base = pd.read_parquet(ANTES / 'modelo_con_proyecciones_teoricas/base_analitica_proyecciones.parquet')
old_obs = old_base.loc[old_base.y.notna()]
assert len(obs) == len(old_obs)
full = int(obs.curva_completa.sum())
old_full = int(old_obs.curva_completa.sum())
age_check = usable.dropna(subset=['fecha_corte', 'fecha_semana_siembra', 'edad']).copy()
age_from_dates = ((age_check.fecha_corte - age_check.fecha_semana_siembra).dt.days // 7).astype(int)
assert age_from_dates.eq(age_check.edad.astype(int)).all()
projected2026 = pd.read_parquet(PROY / '2026/proyecciones_teoricas.parquet')
age_projection_check = projected2026.dropna(subset=['fecha_siembra','semana_proyeccion','edad']).copy()
age_mondays = age_projection_check.fecha_siembra.dt.normalize() - pd.to_timedelta(age_projection_check.fecha_siembra.dt.weekday, unit='D')
age_projected = ((age_projection_check.semana_proyeccion - age_mondays).dt.days // 7).astype(int)
assert age_projected.eq(age_projection_check.edad.astype(int)).all()
coverage_sentence = (f'De {num(len(obs), 0)} casos con producción real observada, en {num(full, 0)} ({pct(full / len(obs))}) '
                     f'hay una referencia teórica aplicable al plano y a todas las edades de sus cohortes; antes de esta revisión eran '
                     f'{num(old_full, 0)} ({pct(old_full / len(old_obs))}). Este indicador describe cuándo se puede usar la referencia directa de curvas; '
                     f'no mide pérdida de producción ni el cruce cama piloto–estadística. En los casos admisibles sin referencia directa, el pronóstico usa producción reciente; los casos que no cumplen los requisitos del modelo permanecen en la base para trazabilidad, pero no reciben pronóstico del modelo.')
reason_labels={
    'curva_completa':'Plano alineado y curva aplicable a todas las cohortes',
    'cohortes_sin_curva':'Plano alineado; una o más edades no están representadas',
    'sin_pareja_comercial_u_objetivo':'No hay pareja de serie comercial y semana objetivo con el plano',
    'sin_snapshot_disponible':'No hay versión de plano elegible para ese origen',
}
reason_counts=obs.motivo_cobertura.value_counts()
coverage_status_table=table(['Estado para la referencia teórica','Casos','Qué significa'],
    [[reason_labels.get(k,k),num(v,0),('Referencia directa calculable.' if k=='curva_completa' else 'La producción observada permanece en la base; la causa describe por qué no aplica la referencia directa.')]
     for k,v in reason_counts.items()])
dino = (PROY / 'eda_edades_sin_cobertura/hallazgos.md').read_text(encoding='utf-8')
dino_lines = [x.strip() for x in dino.splitlines() if x.strip().startswith(('Primera edad', 'Existe un registro', 'A edades', 'La edad 9'))]
dino_text = ('El ejemplo DINO amarillo de GAITANA muestra por qué la aplicación de la curva y el cruce de camas son preguntas distintas. El plano del 13 de julio de 2026 tiene 25 cohortes para el objetivo del 31 de agosto; la curva piloto usada representa 23 de esas edades. Esto no indica que falten las camas ni la producción real: indica que no se asigna una tasa teórica a las otras dos cohortes y el modelo usa su ruta de producción reciente. '
             + ' '.join(dino_lines) + ' No se rellenan esos grupos con cero sin una regla de negocio confirmada.')
section(next(h for h in ('### 3.3. Disponibilidad de la curva por edad en cada semana objetivo', '### 3.3. Alcance empírico de las curvas por edad', '### 3.3. Cuándo aplica la curva empírica por edad') if h in text), '### 3.4. Qué muestran los cinco últimos planos', f'''
Se distinguen tres pasos: vincular cada observación piloto con su cama y ciclo, resumir el rendimiento observado por variedad y edad, y aplicar esos rendimientos a las cohortes del plano en una semana objetivo. La unión identifica correctamente el origen de las observaciones; la curva representa las edades que aparecen en la historia piloto usada para construirla. Son controles distintos y el segundo no indica que se hayan perdido registros reales.

El plano es una fotografía de inventario. La edad de cada grupo se calcula desde el lunes de su semana de siembra hasta el lunes de la semana que se quiere proyectar. Por ejemplo, un grupo de 10 semanas tendrá 15 semanas cinco semanas después; para esa fecha se consulta la curva a edad 15. La fecha del plano determina qué inventario e historia estaban disponibles, pero no sustituye la fecha de siembra al calcular la edad. Se recalculó esta diferencia en los {num(len(usable),0)} cortes utilizables de la edición 2026 y en las {num(len(age_projection_check),0)} filas de proyección con siembra fechada: todas coinciden con las fechas fuente.

Se procesan 292 versiones seleccionadas entre 2021 y 2026 y diez semanas por plano. El horizonte de construcción se distingue de H1–H5 del modelo, definido desde su fecha de emisión. Las curvas se construyen con las 78 semanas de cortes anteriores a cada plano. Para aplicar una curva a un inventario se consulta la edad de cada cohorte en la semana objetivo. El cálculo directo solo se habilita cuando todas esas edades están representadas en la curva; esto delimita el alcance empírico del método, no la presencia de la producción real ni la calidad del cruce. [E2, E9]

{coverage_sentence} El denominador es serie comercial–origen–horizonte; no son camas, plantas ni tallos. La clasificación completa de la base es:

{coverage_status_table}

El cruce piloto–cama–estadística es un control aparte: 99,84 % de los cortes fechados en 2026 tienen correspondencia única. La base analítica conserva la producción real también en los otros estados; cuando el caso es admisible, el modelo usa la ruta de producción reciente si no hay referencia teórica directa. [E3–E4]

La condición de uso directo exige un plano alineado con la serie y la semana objetivo, además de que la curva represente todas las edades de sus grupos de siembra. Si el plano contiene dos grupos y la curva representa la edad del primero, pero no la del segundo, el cruce de camas puede estar bien y la producción real permanecer disponible; simplemente no se usa una suma parcial como total teórico. El modelo conserva como pronosticables los casos que cumplen sus requisitos de historia y usa la ruta basada en producción reciente. Los demás siguen registrados en la base y no forman parte de las predicciones del modelo.

![Esquema metodológico. La curva define una ruta de referencia; la producción real permanece en la base y el respaldo mantiene el pronóstico. Fuente: E3–E4.](Figuras_resultados/flujo_uso_curva_y_ruta_modelo.png)

![Figura 2. Casos en que la curva representa las edades de todas las cohortes; describe el uso de la referencia directa, no pérdida de producción ni tasa de unión de registros. Fuente: E3–E4.](Figuras_resultados/cobertura_teoria_casos.png)

Que una edad no esté representada por un corte piloto no significa que falte el registro de producción del plano, ni permite asumir que la planta producía cero. El EDA distingue ceros registrados, edades anteriores al rango empírico, huecos entre edades representadas y edades posteriores. Son situaciones sobre el alcance de la curva; solo una regla agronómica confirmada permitiría asignar un cero teórico. El notebook 02 muestra estas situaciones y el ejemplo DINO. Un rendimiento cero que sí fue registrado se conserva como tal.

{dino_text}

La implicación para el modelo es concreta: se ajusta la referencia teórica cuando puede calcularse completa; en los demás casos se utiliza producción reciente como referencia. No se considera la falta de soporte por edad un error de pronóstico. El error sólo se calcula al comparar una predicción numérica válida con la producción observada.
''')
text=text.replace('### 3.3. Disponibilidad de la curva por edad en cada semana objetivo', '### 3.3. Cuándo aplica la curva empírica por edad')

# Errores de teoría y asociaciones motivadoras, recalculados desde la base vigente.
pairs = obs.loc[obs.curva_completa].copy()
pairs['error_real_menos_teoria'] = pairs.y - pairs.teoria_modelo
eda_rows = []
for h, d in pairs.groupby('horizonte'):
    eda_rows.append([f'H{int(h)}', num(len(d), 0), num(d.error_real_menos_teoria.mean()), pct(d.error_real_menos_teoria.abs().sum() / d.y.sum())])
theory_eda = table(['Horizonte', 'Casos donde la curva representa todas las cohortes', 'Error medio real − teoría (tallos)', 'WAPE descriptivo'], eda_rows)
explore = pairs.loc[(pairs.semana_objetivo + pd.Timedelta(days=7)).le(pd.Timestamp('2025-07-07'))].copy()
signals = ['produccion_lag1', 'cambio_reciente', 'media_4']
assoc = []
groups = ['finca', 'producto', 'color', 'variedad', 'horizonte']
for k, g in explore.groupby(groups):
    for v in signals:
        z = g[[v, 'error_real_menos_teoria']].dropna()
        if len(z) >= 20 and z[v].nunique() > 1 and z.error_real_menos_teoria.nunique() > 1:
            assoc.append({'h': k[-1], 'variable': v, 'rho': z[v].corr(z.error_real_menos_teoria, method='spearman')})
assoc = pd.DataFrame(assoc)
assoc_summary = assoc.groupby(['h', 'variable']).agg(series=('rho', 'size'), mediana=('rho', 'median')).reset_index()
assoc_wide = assoc_summary.pivot(index='variable', columns='h', values='mediana')
assoc_rows = [[{'produccion_lag1':'Producción de la semana anterior', 'cambio_reciente':'Cambio entre las dos últimas semanas', 'media_4':'Promedio de cuatro semanas'}[v],
               num(assoc_wide.loc[v].get(1, np.nan), 3), num(assoc_wide.loc[v].get(5, np.nan), 3)] for v in signals]
assoc_table = table(['Señal conocida al origen', 'Mediana H1', 'Mediana H5'], assoc_rows)
section('### 3.6. Dónde se separan la teoría y la producción registrada', '### 3.7. Clima, error de volumen y desplazamiento del corte', f'''
El error se define como producción real menos teoría; un valor negativo significa que la teoría quedó por encima de lo registrado. El WAPE de abajo es descriptivo para casos completos y no debe equipararse al modelo: cambian período y población. [E4]

{theory_eda}

La diferencia orienta a corregir la referencia teórica donde puede calcularse y a utilizar producción reciente donde falte soporte. Contar producción observada en esas series es posible porque el panel se construye desde los registros reales; que exista esa semana para evaluar no garantiza que la curva empírica contenga todas las edades del inventario.

### 3.6.1. Por qué se probaron rezagos y tendencias

Antes de entrenar se midió si señales de producción conocidas al origen se asociaban con el error posterior de la teoría. Se calcula Spearman dentro de serie comercial y horizonte, para objetivos cerrados antes del 7 de julio de 2025 y al menos veinte pares; luego se toma la mediana entre series. [E4]

{assoc_table}

La asociación mayor de la semana previa en H1 motivó probar memoria reciente. No indica cuánto mejorará el pronóstico ni establece causalidad. En 12 y 15 se comprueba su utilidad comparando predicciones en cortes temporales; las entradas diarias se agregan después como un bloque en 14. Las señales largas y conteos se comparan por bloques, porque el EDA no justifica individualmente cada variable.''')

# Resultados semanales: selección previa, mismos casos y comparación con la ejecución previa.
pred = pd.read_parquet(CLIMA / 'comparacion_clima_curvas_2026.parquet')
strict = pred.loc[pred.grupo_comparacion.eq('principal')].copy()
if strict.empty:
    # El vocabulario del panel se lee de la tabla de diagnóstico ya validada por 20.
    keys = pd.read_parquet(DATA / 'eda_origen_error/casos_error_comparables.parquet', columns=KEY)
    strict = pred.merge(keys, on=KEY, validate='one_to_one')
assert not strict.duplicated(KEY).any()
chosen = pred.modelo_seleccionado.unique()
assert len(chosen) == 1
chosen = chosen[0]
names['Seleccion_pre2026'] = 'Selección previa: ' + names[chosen]
old_pred = pd.read_parquet(ANTES / 'revision_clima_finca/comparacion_clima_curvas_2026.parquet')
compare = strict.merge(old_pred[KEY + ['Seleccion_pre2026', 'y']], on=KEY, suffixes=('', '_antes'), validate='one_to_one')
assert len(compare) == len(strict) and np.allclose(compare.y, compare.y_antes)
rows, comparisons = [], []
for h, d in list(compare.groupby('horizonte')) + [('Conjunto', compare)]:
    a, b, e = [metrics(d, c) for c in ['Seleccion_pre2026_antes', 'Seleccion_pre2026', 'ingeniero']]
    rows.append([f'H{int(h)}' if h != 'Conjunto' else h, num(len(d), 0), pct(a['WAPE']), pct(b['WAPE']), pct(e['WAPE']), num(b['sesgo_pct']) + ' %', num(e['sesgo_pct']) + ' %'])
    comparisons.append({'horizonte': h, 'casos': len(d), 'WAPE_antes': a['WAPE'], 'WAPE_actual': b['WAPE'], 'WAPE_ingeniero': e['WAPE'], 'sesgo_antes_pct': a['sesgo_pct'], 'sesgo_actual_pct': b['sesgo_pct'], 'sesgo_ingeniero_pct': e['sesgo_pct']})
comparison = pd.DataFrame(comparisons)
comparison.to_csv(REV / 'comparacion_semanal_antes_despues.csv', index=False, encoding='utf-8-sig')
horizon_table = table(['Horizonte', 'Casos', 'WAPE antes del 19/10', 'WAPE actual', 'WAPE ingeniero', 'Sesgo actual', 'Sesgo ingeniero'], rows)
summary = excel(CLIMA / 'resultados_clima_curvas.xlsx', 'Resumen')
summary = summary.loc[~summary.modelo.eq('Seleccion_pre2026')]
validation = excel(CLIMA / 'resultados_clima_curvas.xlsx', 'Validacion_pre2026')
current, engineer, previous = [metrics(compare, c) for c in ['Seleccion_pre2026', 'ingeniero', 'Seleccion_pre2026_antes']]
h1 = compare.loc[compare.horizonte.eq(1)]
h1_current, h1_engineer = metrics(h1, 'Seleccion_pre2026'), metrics(h1, 'ingeniero')
intervals = excel(CLIMA / 'resultados_clima_curvas.xlsx', 'Incertidumbre')
interval = intervals.loc[intervals.modelo.eq('Seleccion_pre2026') & intervals.referencia.eq('ingeniero')].iloc[0]
bias_definition = 'Sesgo = 100 × suma(predicción − real) / suma(real). Positivo indica sobreestimación; negativo, subestimación. Errores opuestos se compensan en el sesgo, pero se suman en el WAPE. Se informan ambos sobre los mismos casos.'
weekly_body = f'''La revisión mantiene algoritmos, variables, cortes temporales y reglas de selección. Cambian la historia de pilotos recuperada y las curvas derivadas; se reconstruyen las referencias y se reentrenan los modelos. La selección con validación anterior a 2026 es **{names[chosen]}**. Se conserva al evaluar 2026; no se escoge el menor error mirando al ingeniero. [E16]

{metric_table(summary)}

La tabla siguiente compara la ejecución guardada antes del 19 de octubre con la recalculada sobre los mismos {num(len(compare), 0)} casos. Esa fecha identifica una revisión del proyecto, no un nuevo período de test. La referencia histórica anterior al clima de la tabla anterior corresponde a otro experimento y no se confunde con este antes/después.

{horizon_table}

{bias_definition}

**H1 por separado:** {num(len(h1), 0)} casos, WAPE del modelo {pct(h1_current['WAPE'])} frente a {pct(h1_engineer['WAPE'])} del ingeniero. Sesgo {num(h1_current['sesgo_pct'])} % frente a {num(h1_engineer['sesgo_pct'])} %. La diferencia de WAPE es {num(100 * (h1_engineer['WAPE'] - h1_current['WAPE']))} puntos a favor del modelo cuando es positiva.

En conjunto, el modelo obtiene {pct(current['WAPE'])}, frente a {pct(engineer['WAPE'])} del ingeniero. La ventaja es {num(interval.ventaja_pp)} puntos, con intervalo exploratorio de 95 % [{num(interval.p025)}; {num(interval.p975)}]. El desglose permite reconocer dónde gana cada método. No se interpreta una diferencia retrospectiva pequeña como superioridad estable.

El conjunto agrega casos de pronóstico: una misma semana objetivo puede aparecer desde distintos orígenes y horizontes. El denominador no representa producción física única. El ingeniero se utiliza sólo como referencia de evaluación.

![Figura 9. Comparación semanal de clima y curva atribuida a GAITANA, sobre mismos casos. Fuente: E16.](Figuras_resultados/clima_modelos_horizonte.png)

![Figura 10. Sesgo por horizonte de las alternativas y del ingeniero. Fuente: E16.](Figuras_resultados/clima_sesgo_horizonte.png)

![Figura 11. Cambio de la predicción al incorporar clima; cambiar y mejorar no son lo mismo. Fuente: E16.](Figuras_resultados/clima_movimiento_estimado.png)

Las hojas Rutas_curvas y Teorias_mismos_casos distinguen cambio de referencia y cambio de ruta. Restringir pilotos puede cambiar el soporte por edad; una diferencia de WAPE no certifica un mecanismo fisiológico ni identifica la finca de los pilotos desconocidos.'''
section('### 5.1. Precisión semanal: efecto del clima y comparación con el ingeniero', '### 5.2. Precisión diaria y coherencia semanal con el clima actualizado', weekly_body)
# Sustituir sólo la tabla de validación dentro de su sección metodológica.
a = text.index('La validación anterior a 2026 produce esta comparación;')
b = text.index('Una diferencia pequeña entre candidatos', a)
text = text[:a] + 'La validación anterior a 2026 produce esta comparación; no es el test frente al ingeniero:\n\n' + metric_table(validation) + '\n\n' + text[b:]

# Recalcula el recorrido 12→14→15 que precede al benchmark final.
initial = excel(MODEL / 'resultados_modelo_teorico.xlsx', 'Metricas_casos_comunes')
common12 = int(initial.n.min())
initial_names = {'Ultimo_valor':'Último valor real: referencia de persistencia', 'Media4':'Media4: promedio real de cuatro semanas',
    'Teoria_sin_ajuste':'Teoría cruda, sin corrección', 'Ajuste_media4_sin_planos':'Boosting que corrige Media4, sin teoría',
    'Modelo_teorico':'Boosting que corrige la teoría con memoria y clima', 'Teorico_sin_memoria':'Mismo boosting, sin memoria real',
    'Teorico_sin_clima':'Mismo boosting, sin clima', 'Ridge_ajuste_teoria':'Ridge: corrección lineal regularizada de teoría',
    'Modelo_teorico_historia':'Boosting teórico con proyecciones anteriores'}
initial_table = table(['Modelo y referencia', 'Casos', 'WAPE'],
    [[initial_names.get(r.modelo,r.modelo), num(r.n,0), pct(r.WAPE)] for r in initial.itertuples()])
sys_df = excel(MODEL / 'resultados_modelo_teorico.xlsx', 'Metricas_sistema')
sys_table = table(['Sistema y referencia', 'Casos', 'WAPE'],
    [[('Curva para todas las cohortes + respaldo de producción reciente' if r.modelo == 'Sistema_teoria_con_respaldo' else 'Boosting sobre Media4'), num(r.n,0), pct(r.WAPE)] for r in sys_df.itertuples()])
feat_df = excel(MODEL / 'resultados_features_diarias_2026.xlsx', 'Resumen')
feat_names = {'Sistema_anterior':'Sistema antes de añadir señales diarias', 'Sistema_diario':'Boosting semanal con 28 señales recientes de corte y clima',
    'Ajuste_relativo_diario':'Corrección relativa de Media4 en escala logarítmica', 'Boosting_diario_MAE':'Boosting con pérdida absoluta y rutas exploratorias', 'ingeniero':'Ingeniero'}
feat_table = table(['Experimento 14', 'Casos', 'WAPE'], [[feat_names.get(r.metodo,r.metodo),num(r.n,0),pct(r.WAPE)] for r in feat_df.itertuples()])
exp_df = excel(MODEL / 'resultados_experimentos_horizontes.xlsx', 'Resumen')
exp_names = {'Antes_calidad':'Referencia anterior (usa otra configuración y clima)', 'Separado':'Boosting agrupado H1–H2 y H3–H5',
    'Memoria_larga':'Boosting separado con memoria productiva de hasta 12 semanas', 'Revisiones':'Boosting con proyecciones previas',
    'Combinacion':'Mezcla fijada con validación anterior a 2026', 'Sistema_diario':'Boosting con señales diarias de 14', 'ingeniero':'Ingeniero'}
exp_table = table(['Experimento 15', 'Casos', 'WAPE'], [[exp_names.get(r.metodo,r.metodo),num(r.n,0),pct(r.WAPE)] for r in exp_df.itertuples()])
walk = f'''Los resultados de 12 preguntan si puede corregirse una referencia con información pasada. En los mismos casos donde la curva representa las edades de todas las cohortes se comparan reglas sencillas, boosting y Ridge. Los nombres describen qué referencia y qué bloque recibe cada ajuste. [E5]

{initial_table}

El sistema completo conserva una ruta de pronóstico para todos los casos admisibles. Cuando la curva no representa todas las edades, se usa la ruta basada en producción reciente. En 12 se evalúa el sistema completo por separado:

{sys_table}

El experimento 14 añadió señales de corte diario y clima diario a un boosting semanal. Como entran conjuntamente, la comparación no aísla el efecto de cada señal:

{feat_table}

En 15 se agruparon horizontes, se añadió historia productiva larga y se probaron versiones anteriores de la teoría. Los pesos se fijaron con validación temporal previa a 2026:

{exp_table}

«Sin memoria» significa que el modelo no recibe rezagos productivos, aunque sí aprende de casos históricos. Las proyecciones previas son versiones anteriores del plano para la misma semana objetivo. La referencia “Antes” conserva otra configuración y clima, por lo que no aísla el efecto de esta revisión. La selección final por validación temporal se informa aparte en 5.1.'''
section('### Recorrido de resultados antes de la selección vigente', '### 5.1. Precisión semanal: efecto del clima y comparación con el ingeniero', walk)

daily = excel(DIARIO / 'resultados_diarios_clima.xlsx', 'Resumen')
daily_old = excel(ANTES / 'modelo_diario/resultados_diarios_clima.xlsx', 'Resumen').set_index('modelo')
daily_index = daily.set_index('modelo')
daily_body = f'''(En revisión: desarrollo preliminar y siguientes pasos.)

El componente diario conserva sus modelos y usa los nuevos totales semanales. El autónomo pronostica cada día con producción reciente, calendario y clima pasado; el reconciliado distribuye el total semanal mediante pesos de boosting. El perfil histórico y el reparto uniforme son referencias. Se emiten siete días desde el lunes sin usar reportes de esa semana. [E17]

{metric_table(daily)}

Antes de esta revisión, el reconciliado con la selección semanal tenía WAPE {pct(daily_old.loc['Boosting_clima', 'WAPE'])}; tras reconstruir curvas y modelos, {pct(daily_index.loc['Boosting_clima', 'WAPE'])}. El autónomo obtiene {pct(daily_index.loc['Boosting_diario', 'WAPE'])}. La comparación se realiza sobre días reportados; un día sin registro no se convierte en cero. Todos los repartos coherentes conservan su total semanal.

![Figura 12. Precisión diaria sobre mismos días reportados. Fuente: E17.](Figuras_resultados/diario_clima_actualizado.png)

La sensibilidad a semanas con siete reportes se conserva en Semanas_completas del Excel de diario 05. Su composición difiere del panel general y no puede usarse su completitud futura para elegir método al emitir. No existe aquí un benchmark diario del ingeniero ni un umbral operativo validado.'''
section('### 5.2. Precisión diaria y coherencia semanal con el clima actualizado', '### 5.3. Piloto SARIMA/SARIMAX', daily_body)
a = text.index('### 5.3. Piloto SARIMA/SARIMAX')
b = text.index('### 5.4.', a)
part = text[a:b]
part = re.sub(r'(?m)^\| Método[^\n]*\n(?:\|[^\n]*\n)+', lambda _: metric_table(excel(DIARIO / 'resultados_diarios_clima.xlsx', 'Piloto_SARIMA')) + '\n', part)
text = text[:a] + part + text[b:]

# Actualiza la explicación de importancia por permutación con la última ejecución.
perm = excel(MODEL / 'interpretacion_modelo_semanal.xlsx','Bloques')
perm_rows=[]
for (group,ruta),g in perm.groupby(['grupo','ruta']):
    r=g.loc[g.aumento_WAPE_pp.abs().idxmax()]
    perm_rows.append([f'{group} / {ruta}',r.variable,num(r.n,0),num(r.aumento_WAPE_pp)])
perm_table=table(['Grupo de horizonte / ruta','Bloque con mayor cambio','Casos evaluados','Cambio WAPE (pp)'],perm_rows)
section('### 5.4. Interpretación de variables del modelo seleccionado', '### 5.5. Entrenamiento y evaluación del mismo ajuste', f'''El notebook 16 vuelve a calcular el ajuste del 3 de agosto y permuta bloques de entradas para observar cuánto cambia el WAPE. Esto no es SHAP, no es un porcentaje de producción y no mide un efecto causal. El cambio por permutación puede ser grande con pocos casos o variables relacionadas; se presenta con el tamaño del grupo. [E12]

Como la selección semanal fijada es Sin_clima, esa alternativa no recibe variables meteorológicas. La importancia climática no es cero: se evalúa por los contrastes de modelos de 19.

{perm_table}

![Figura 13. Importancia por bloques de la alternativa semanal seleccionada. Fuente: E12.](Figuras_resultados/importancia_bloques_semanal.png)

![Figura 14. Variables con mayor cambio al permutarlas dentro de cada grupo. Fuente: E12.](Figuras_resultados/importancia_variables_semanal.png)

Las entradas con información redundante pueden sustituirse entre sí y la permutación puede crear combinaciones poco habituales. El grupo donde la curva representa todas las cohortes es menor que el universo completo; sus resultados se leen con cautela y no se usan para cambiar la selección retrospectivamente.''')

# Train y test del último ajuste ejecutado.
weekly_split = excel(CLIMA / 'resultados_clima_curvas.xlsx', 'Ultimo_ajuste')
weekly_split = weekly_split.loc[weekly_split.split.isin(['train','test'])]
weekly_rows=[]
for model in ['Sin_clima','Clima_basico','Clima_ampliado','Curva_Gaitana_clima']:
    tr=weekly_split.loc[weekly_split.modelo.eq(model)&weekly_split.split.eq('train')].iloc[0]
    te=weekly_split.loc[weekly_split.modelo.eq(model)&weekly_split.split.eq('test')].iloc[0]
    weekly_rows.append([names.get(model,model),pct(tr.WAPE),pct(te.WAPE),num(tr.n,0),num(te.n,0)])
weekly_split_table=table(['Modelo semanal','WAPE train','WAPE test mismo corte','Casos train','Casos test'],weekly_rows)
daily_split=excel(DIARIO / 'resultados_diarios_clima.xlsx','Train_test_ultimo_ajuste')
daily_labels={'Boosting_diario':'Boosting diario autónomo','Uniforme_clima':'Reparto uniforme con selección semanal',
    'Perfil_clima':'Perfil histórico con selección semanal','Boosting_clima':'Boosting reconciliado con selección semanal'}
diary_rows=[]
for model,label in daily_labels.items():
    tr=daily_split.loc[daily_split.modelo.eq(model)&daily_split.split.eq('train')].iloc[0]
    te=daily_split.loc[daily_split.modelo.eq(model)&daily_split.split.eq('test')].iloc[0]
    diary_rows.append([label,pct(tr.WAPE),pct(te.WAPE),num(tr.n,0),num(te.n,0)])
diary_split_table=table(['Modelo diario','WAPE train','WAPE test mismo corte','Casos train','Casos test'],diary_rows)
section('### 5.5. Entrenamiento y evaluación del mismo ajuste', '### 5.6. De dónde proviene el WAPE: productos, colores y variedades', f'''El inventario 17 conserva los distintos cortes. Aquí se compara train con test del corte del 3 de agosto de 2026 para las mismas configuraciones; también se informa cuántos casos contiene cada partición. El ingeniero es una referencia evaluada, no un modelo entrenado en el proyecto. [E13, E16, E17]

{weekly_split_table}

{diary_split_table}

El ingeniero no tiene un train de nuestro algoritmo. SARIMA/SARIMAX dentro de muestra excluyen la inicialización del filtro y no equivalen a pronósticos emitidos día a día. Una diferencia entre train histórico y un mes de test también refleja composición y dificultad del periodo; no prueba por sí sola fuga ni ausencia de sobreajuste.''')

# Reemplaza el resumen editorial que conservaba cifras anteriores.
paragraph('El proyecto pronostica semanalmente tallos reportados en GAITANA',
    f'''El proyecto pronostica semanalmente tallos reportados en GAITANA con curvas de rendimiento por edad, producción reciente y clima. La integración corregida recuperó registros de camas piloto con diferencias de escritura y reconstruyó las proyecciones y modelos. {coverage_sentence} En {num(len(compare),0)} casos emparejados, el WAPE semanal es {pct(current['WAPE'])} frente a {pct(engineer['WAPE'])} del ingeniero. El detalle por horizonte y sesgo aparece en resultados.''')
# Resumen para lectura: tablas actuales y cambio de esta revisión, sin selección por test.
summary_text = '# Modelos de pronóstico: revisión de correspondencias del 19 de octubre de 2026\n\n'
summary_text += 'Los modelos semanales aprendidos son variantes de HistGradientBoostingRegressor: árboles que corrigen una referencia usando información disponible al emitir. El ingeniero es el benchmark, no una entrada del modelo. La selección previa a 2026 es ' + names[chosen] + '.\n\n'
summary_text += '## Semanales\n\n' + metric_table(summary) + '\n\n' + horizon_table + '\n\n' + bias_definition
summary_text += f"\n\n## H1 por separado\n\nWAPE modelo **{pct(h1_current['WAPE'])}**, ingeniero **{pct(h1_engineer['WAPE'])}**. Sesgo modelo **{num(h1_current['sesgo_pct'])} %**, ingeniero **{num(h1_engineer['sesgo_pct'])} %**. Mismos {num(len(h1), 0)} casos.\n\n"
summary_text += f"El WAPE conjunto pasa de {pct(previous['WAPE'])} a {pct(current['WAPE'])} tras la revisión de cruces. Corregir la integración no garantiza mejorar todas las métricas: se informan los resultados obtenidos.\n\n"
summary_text += '## Diarios\n\n(En revisión: desarrollo preliminar y siguientes pasos.)\n\n' + metric_table(daily)
summary_text += f"\n\nReconciliado: {pct(daily_old.loc['Boosting_clima', 'WAPE'])} antes → {pct(daily_index.loc['Boosting_clima', 'WAPE'])} ahora. Autónomo: {pct(daily_index.loc['Boosting_diario', 'WAPE'])}. SARIMA/SARIMAX se comparan sólo en su piloto de tres series, no con este panel completo.\n\n"
summary_text += '## Cuándo se aplica directamente la curva\n\n' + coverage_sentence + '\n\n' + f'En los otros estados de la base hay {num(reason_counts.get("cohortes_sin_curva",0),0)} casos donde alguna edad de cohorte no está representada por la curva, {num(reason_counts.get("sin_pareja_comercial_u_objetivo",0),0)} sin pareja de serie/objetivo con un plano y {num(reason_counts.get("sin_snapshot_disponible",0),0)} sin plano elegible. La producción real permanece en las 211.001 filas observadas. En cortes fechados en 2026 hay {num(recent_joined, 0)} correspondencias únicas de {num(len(recent), 0)} ({pct(recent_joined / len(recent))}); este porcentaje es una auditoría separada entre registros piloto, cama, identidad y ciclo.\n\n'
summary_text += '## Entrenamiento y test\n\nNo hay división aleatoria. Se entrena con semanas objetivo terminadas antes del corte, se selecciona en noviembre–diciembre de 2025 y se evalúa 2026 con reentrenamiento mensual. El inventario 17 y las hojas Ultimo_ajuste de 19 y Train_test_ultimo_ajuste de diario 05 permiten comparar train y test del mismo ajuste. Son resultados retrospectivos.\n\n'

# El diagnóstico de error se regenera desde las mismas predicciones de 19.
error_text = (DATA / 'eda_origen_error/hallazgos_origen_error.md').read_text(encoding='utf-8')
summary_text += '## Origen del error\n\n' + error_text[error_text.index('Mismos casos'):]
old_summary = (ROOT / 'resumen_modelos_pronostico.md').read_text(encoding='utf-8')

# Descomposición vigente del error y discusión asociada a las predicciones actuales.
error_text = (DATA / 'eda_origen_error/hallazgos_origen_error.md').read_text(encoding='utf-8')
section('### 5.6. De dónde proviene el WAPE: productos, colores y variedades', '## 6. Discusión: calidad, clima y distribución del error', f'''
El notebook 20 descompone los mismos casos estrictos usados en la comparación semanal. Los aportes se expresan en puntos del WAPE total: error absoluto del grupo dividido por el volumen real de todo el panel. Así se distinguen grupos con una tasa alta de error de los grupos que más pesan por volumen. No se cambió el modelo a partir de este diagnóstico. [E18]

{error_text[error_text.index('## H1: productos'):error_text.index('## Cómo interpretar')]}

Los gráficos detallados se mantienen junto al Excel diagnóstico: productos, colores, variedades, meses, rutas y semanas. Son hipótesis para revisar los episodios con operaciones; por sí solos no identifican una causa agronómica ni un error en el registro.

![Figura 15. Aporte de los productos al WAPE. Fuente: E18.](Figuras_resultados/error_aporte_productos.png)

![Figura 16. Diferencia de WAPE por producto y horizonte. Fuente: E18.](Figuras_resultados/error_producto_horizonte.png)

![Figura 17. Trayectorias de variedades foco en H1. Fuente: E18.](Figuras_resultados/error_variedades_foco_h1.png)
''')

section('## 6. Discusión: calidad, clima y distribución del error', '## 7. Conclusiones y continuidad', f'''
La corrección de nombres recuperó observaciones reales de camas piloto sin crear cortes. En los registros de 2026, casi todas las estadísticas fechadas en ese año tienen una correspondencia única con cama, variedad y ciclo. Las correspondencias ambiguas que persisten corresponden a referencias concretas con más de una cama candidata y valores de plantas distintos; se identifican para revisión puntual. Esa auditoría no debe confundirse con el soporte de edades de la curva.

La base analítica conserva las semanas de producción real y añade la referencia derivada de los planos. La curva empírica representa las edades observadas en los pilotos utilizados. Si una cohorte pide otra edad, el sistema conserva el caso y usa la ruta basada en producción reciente. Es una condición metodológica de aplicación de la curva; no significa que se haya perdido producción ni que las camas no se hayan cruzado.

En el modelo semanal, WAPE actual es {pct(current['WAPE'])} y el ingeniero {pct(engineer['WAPE'])}; H1 es {pct(h1_current['WAPE'])} y {pct(h1_engineer['WAPE'])}, respectivamente. El error firmado agregado del modelo es {num(current['sesgo_pct'])} % del volumen real. Se informa junto con WAPE porque errores positivos y negativos se compensan en el sesgo. La diferencia observada procede de una evaluación retrospectiva y no asegura el mismo resultado en periodos nuevos.

El EDA climático y los experimentos temporales no establecen por sí solos una relación causal. El clima de estación no representa necesariamente cada invernadero y la curva compartida no certifica igualdad agronómica entre fincas. La atribución a GAITANA sólo se hace cuando hay coincidencia verificable con plano.

La distribución diaria sigue en revisión. El modelo autónomo obtiene {pct(daily_index.loc['Boosting_diario', 'WAPE'])}; el reparto reconciliado con la selección semanal, {pct(daily_index.loc['Boosting_clima', 'WAPE'])}. El primero pronostica cada día y el segundo reparte un total semanal: resuelven preguntas distintas. No hay una comparación diaria con el ingeniero.
''')

paragraph('La cadena se recalculó desde la corrección de correspondencias:', f'''La cadena se recalculó desde la corrección de correspondencias: camas piloto, curvas, proyecciones teóricas, base semanal, EDA y modelos. {coverage_sentence} El pronóstico semanal seleccionado por validación temporal tiene {pct(current['WAPE'])} WAPE en 2026 y el ingeniero {pct(engineer['WAPE'])}; H1: {pct(h1_current['WAPE'])} y {pct(h1_engineer['WAPE'])}. El reparto diario reconciliado obtiene {pct(daily_index.loc['Boosting_clima', 'WAPE'])}. Son resultados retrospectivos.''')

# Actualiza la comparación de planos alineando semanas objetivo comunes.
five = excel(PROY / 'comparacion_ultimos_5_planos.xlsx', 'Semanas_comunes')
week = pd.Timestamp('2026-08-17')
five_row = five.loc[pd.to_datetime(five.semana_proyeccion).eq(week)].iloc[0]
cols = [c for c in five if c != 'semana_proyeccion']
v29, v33 = float(five_row[cols[0]]), float(five_row[cols[-1]])
tab3233 = excel(PROY / 'comparacion_ultimos_5_planos.xlsx', 'Comparacion_32_33')
row3233 = tab3233.loc[pd.to_datetime(tab3233.semana_proyeccion).eq(week)].iloc[0]
paragraph('Para la semana objetivo que comienza el 17/08/2026,',
          f'Para el objetivo del 17/08/2026, el total teórico parcial pasa de {num(v29, 0)} tallos en el plano 29 a {num(v33, 0)} en el plano 33. Entre los planos 32 y 33 cambia {num(row3233.diferencia_33_menos_32, 0)} tallos ({num(row3233.cambio_pct)} %). Las cinco versiones se alinean por objetivo común; no se interpreta la última como más precisa sin contrastarla con producción real.')

# Reconstruye las dos figuras que dependían de curvas/cobertura recalculadas.
FIG.mkdir(exist_ok=True)
fig, ax = plt.subplots(figsize=(9, 4.5))
c = obs.groupby('horizonte').curva_completa.agg(['sum', 'count'])
(100 * c['sum'] / c['count']).plot.bar(ax=ax, color='#24766f', rot=0)
ax.set(xlabel='Horizonte de pronóstico', ylabel='Casos con todas las edades representadas (%)', title='Cuándo la curva puede calcular el total teórico del plano')
ax.set_xticklabels([f'H{int(float(x.get_text()))}' for x in ax.get_xticklabels()]); ax.grid(axis='y', alpha=.2); fig.tight_layout()
fig.savefig(FIG / 'cobertura_teoria_casos.png', dpi=170); plt.close(fig)

# Diagrama metodológico: la disponibilidad de curva es una condición para elegir
# referencia, no un filtro que elimine observaciones reales de la base analítica.
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
fig, ax = plt.subplots(figsize=(13, 7.2))
ax.set_xlim(0, 13); ax.set_ylim(0, 8); ax.axis('off')
def box(x, y, w, h, title, body, color):
    patch = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.04,rounding_size=0.12',
                           linewidth=1.6, edgecolor=color, facecolor='white')
    ax.add_patch(patch)
    ax.text(x+w/2, y+h*0.68, title, ha='center', va='center', fontsize=11, weight='bold', color='#183b56')
    ax.text(x+w/2, y+h*0.34, body, ha='center', va='center', fontsize=9, color='#263746', wrap=True)
def arrow(a, b, label=None, color='#536b7a'):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=14, linewidth=1.5, color=color))
    if label: ax.text((a[0]+b[0])/2, (a[1]+b[1])/2+0.12, label, ha='center', fontsize=9, color=color, weight='bold')
box(.35, 5.95, 2.5, 1.25, '1. Registros piloto', 'Corte observado + referencia\nde cama y ciclo', '#3b82a0')
box(3.45, 5.95, 2.75, 1.25, '2. Cruce de identidad', 'Cama + variedad + ciclo\n2026: 99,84 % único', '#3b82a0')
box(6.8, 5.95, 2.75, 1.25, '3. Curva empírica', 'Rendimiento por variedad\ny edad, con historia piloto', '#3b82a0')
arrow((2.85,6.58),(3.45,6.58)); arrow((6.2,6.58),(6.8,6.58))
ax.text(10.0, 6.58, 'Este control verifica el cruce.\nNo es el 21,83 %.', ha='left', va='center', fontsize=10, color='#3b82a0', weight='bold')
box(.35, 3.7, 2.8, 1.25, 'Base analítica final', '211.001 casos con\nproducción real observada\nserie–origen–horizonte', '#39765b')
box(3.8, 3.7, 2.8, 1.25, 'Edad por cohorte', 'Se calcula con la siembra y\nla semana objetivo del plano', '#39765b')
box(7.1, 3.58, 2.3, 1.5, '¿Referencia aplicable?', '¿Hay plano alineado y\ncurva para todas\nlas edades?', '#bc8428')
arrow((3.15,4.32),(3.8,4.32)); arrow((6.6,4.32),(7.1,4.32)); arrow((8.15,5.95),(8.25,5.08),color='#3b82a0')
box(10.15, 4.55, 2.5, 1.2, 'Sí: curva directa', '46.051 casos (21,83 %)\nEl modelo ajusta esta base', '#39765b')
box(10.15, 2.8, 2.7, 1.5, '¿Pronosticable?', 'Con historia: respaldo de\nproducción reciente\nSin historia: no se predice;\nel real se conserva', '#8b5a8e')
arrow((9.4,4.52),(10.15,5.05),'Sí','#39765b'); arrow((9.4,4.15),(10.15,3.5),'No','#8b5a8e')
ax.text(.45, 1.42, 'Qué significa: 21,83 % indica cuándo hay plano alineado y la curva representa todas las edades de sus cohortes.',
        ha='left', fontsize=11, weight='bold', color='#183b56')
ax.text(.45, .92, 'No significa que solo se unió ese porcentaje ni que se perdió producción. La base conserva los reales; algunos casos sin historia suficiente no reciben predicción.',
        ha='left', fontsize=10, color='#263746')
ax.text(.45, .42, 'Es normal que una curva observacional no represente cada edad. Entre los casos admisibles, el modelo cambia de referencia cuando la curva no aplica.',
        ha='left', fontsize=10, color='#263746')
fig.tight_layout(); fig.savefig(FIG / 'flujo_uso_curva_y_ruta_modelo.png', dpi=180, bbox_inches='tight'); plt.close(fig)

curves = pd.read_parquet(PROY / '2026/curvas.parquet')
curve_key = 'COMERCIAL|SOLOMIO|WHITE|ARD'
group = curves.loc[curves.clave_curva.eq(curve_key)].copy()
last_date = group.fecha_plano.max()
c = group.loc[group.fecha_plano.eq(last_date)].sort_values('edad')
fig, axes = plt.subplots(2,1,figsize=(9,6),sharex=True)
axes[0].plot(c.edad, c.rendimiento_curva, marker='o', color='#24766f')
axes[0].set(ylabel='Tallos por planta', title=f'Solomio Ard · curva y soporte · plano {pd.Timestamp(last_date):%d/%m/%Y}')
axes[0].grid(alpha=.2)
axes[1].bar(c.edad,c.n_observaciones,color='#d7a63d')
axes[1].set(xlabel='Edad desde la semana de siembra (semanas)',ylabel='Observaciones de cama–semana')
axes[1].grid(axis='y',alpha=.2); fig.tight_layout(); fig.savefig(FIG / 'curva_y_soporte.png', dpi=170); plt.close(fig)

# Lleva el resumen de auditoría a un archivo breve y verificable.
residual = est.loc[est.fecha_corte.dt.year.eq(2026) & est.estado_union.ne('unica')].copy()
residual_rows = residual[['estado_union', 'referencia', 'variedad', 'producto', 'color']].drop_duplicates()
residual_rows.to_csv(REV / 'referencias_pendientes_cortes_2026.csv', index=False, encoding='utf-8-sig')
notes = f'''# Revisión de correspondencias y soporte de edad — 19 de octubre de 2026

## Qué revisamos

La estadística de corte de una cama piloto se une a su registro de cama, identidad comercial y ciclo de siembra. Luego se calcula edad en semanas entre la semana de siembra y la semana objetivo. La curva asigna a esa variedad y edad un rendimiento medio observado por planta. Los planos aportan plantas y fechas de siembra; las observaciones piloto aportan rendimientos por edad.

## Correspondencias

- Estadísticas de edición 2026: {num(len(est), 0)} filas originales; {num(joined, 0)} con candidato único después de normalizar escritura y quitar duplicados equivalentes.
- Cortes con fecha en 2026: {num(recent_joined, 0)} de {num(len(recent), 0)} con correspondencia única ({pct(recent_joined / len(recent))}).
- Las 53 filas restantes pertenecen a referencias con candidatas múltiples o identidad incompleta. Al colapsar semanas repetidas quedan {len(residual_rows)} referencias distintas. El CSV adjunto permite revisarlas por referencia. En esas filas se reportan {num(residual_cuts,0)} tallos, aproximadamente {num(residual_volume_pct)} % del corte registrado en las estadísticas de 2026; son filas semanales repetidas, no tallos físicos únicos. Por ejemplo, Navarro-25-57, Farida-25-114A, Lorenzo-22-79 y Zagara-15-172 tienen dos candidatas con datos del ciclo coincidentes; la cantidad de plantas no permite elegir sin confirmación.
- El par Caroline Gold, filas 5908 y 5931 de Camas Piloto del Excel de clavel 2026, era una repetición con diferencias de mayúsculas; se reconoce como una misma cama/ciclo. No se sumaron sus cortes.
- Se recuperaron {num(est.identidad_recuperada_por_referencia.sum(), 0)} nombres ausentes sólo donde la referencia completa del mismo libro indicó una identidad comercial única y compatible con el producto.

## Edades y modelo

Después del recálculo, en {num(full, 0)} de {num(len(obs), 0)} casos observados ({pct(full / len(obs))}) la curva representa las edades de todas las cohortes del plano; antes de esta revisión eran {num(old_full, 0)} ({pct(old_full / len(old_obs))}). El porcentaje describe cuándo se puede usar un total derivado directamente de la curva. No mide pérdida de registros ni éxito del cruce cama–estadística: la producción observada se conserva y los demás casos siguen la ruta de pronóstico basada en producción reciente.

El sistema conserva la ruta basada en la curva cuando representa todas las cohortes y usa producción reciente en los demás casos. La edad no representada no se convierte automáticamente en cero. Las cifras semanales, diarias y diagnósticos por producto se regeneraron con las curvas corregidas; el Word nuevo se construye desde el informe actualizado.
'''
(REV / 'hallazgos_revision.md').write_text(notes, encoding='utf-8')

# Refresca el resumen climático con el EDA que corresponde a los modelos actuales.
climate_support = excel(CLIMA / 'eda_clima_variables_modelos.xlsx','Soporte_comun')
climate_associations = excel(CLIMA / 'eda_clima_variables_modelos.xlsx','Asociaciones')
h1_support = climate_support.loc[climate_support.horizonte.eq(1)].iloc[0]
h1_associations = climate_associations.loc[(climate_associations.lectura.eq('Casos comunes')) & climate_associations.horizonte.eq(1)]
climate_lookup = h1_associations.set_index('variable').rho_mediana
climate_end = (f'La comparación común de las 26 entradas conserva entre {num(climate_support.porcentaje_conservado.min())} % y '
    f'{num(climate_support.porcentaje_conservado.max())} % de casos según horizonte. H1 mantiene {num(h1_support.casos_comunes,0)} casos de '
    f'{num(h1_support.origenes_comunes,0)} orígenes; {int(h1_associations.series.max())} series cumplen el requisito de pares para resumir asociaciones. '
    f'Las medianas H1 incluyen temperatura semanal previa {num(climate_lookup.get("temperatura_semana_lag1",np.nan),3)}, '
    f'humedad media4 {num(climate_lookup.get("humedad_semana_media4",np.nan),3)} y días con lluvia7 {num(climate_lookup.get("lluvia_dias7_clima",np.nan),3)}. '
    'Son asociaciones exploratorias entre producción real y error de teoría, no una medida de efecto causal ni una selección de variables por sí solas.')
paragraph('La comparación común conserva entre 63,53 % y 65,24 % de los casos por horizonte.',climate_end)

# Corrige síntesis en notebooks donde el texto narrativo guardado tenía cifras anteriores.
def edit_markdown(path, edit):
    p=ROOT/path; n=nbformat.read(p,as_version=4); edit(n); nbformat.validate(n); nbformat.write(n,p)

def edit12(n):
    c=n.cells[0]
    marker='**Resultado de las salidas ejecutadas actuales:**'
    base=c.source.split(marker)[0]
    by=initial.set_index('modelo')
    cov=excel(MODEL / 'resultados_modelo_teorico.xlsx','Cobertura')
    sy=sys_df.set_index('modelo')
    c.source=base+marker+'\n\nRecalculado el 19 de octubre: en '+num(common12,0)+' casos, todas las cohortes tenían edades representadas en la curva y se compararon las referencias teóricas; teoría sin ajuste obtiene '+pct(by.loc['Teoria_sin_ajuste','WAPE'])+' WAPE; boosting teórico '+pct(by.loc['Modelo_teorico','WAPE'])+'; con historia '+pct(by.loc['Modelo_teorico_historia','WAPE'])+'; sin clima '+pct(by.loc['Teorico_sin_clima','WAPE'])+'; sin memoria real '+pct(by.loc['Teorico_sin_memoria','WAPE'])+'. El sistema completo, que usa la ruta teórica cuando aplica y la ruta de producción reciente en los demás casos, obtiene '+pct(sy.loc['Sistema_teoria_con_respaldo','WAPE'])+' sobre '+num(sy.loc['Sistema_teoria_con_respaldo','n'],0)+' casos admisibles. No mezclar esta población con el benchmark del notebook 19.'
    replacements={'cuando falta teoría completa':'cuando la curva no representa todas las edades del plano',
                  'cuando no hay teoría completa':'cuando la curva no representa todas las edades del plano',
                  'casos de evaluación con teoría completa':'casos donde la curva representa las edades de todas las cohortes',
                  'sólo con teoría completa':'solo cuando la curva representa todas las cohortes',
                  'solo con teoría completa':'solo cuando la curva representa todas las cohortes',
                  'teoría completa':'curva aplicable a todas las cohortes',
                  'cobertura completa':'aplicabilidad a todas las cohortes'}
    for cell in n.cells:
        if cell.cell_type=='markdown':
            for old,new in replacements.items(): cell.source=cell.source.replace(old,new)

def edit11(n):
    c=n.cells[0]
    c.source=c.source.replace('cobertura, calidad', 'disponibilidad de curva por edad, calidad')
    c.source=c.source.replace('## 1. Calidad, calendario, ceros y cobertura','## 1. Calidad, calendario, ceros y cuándo aplica la curva')
    c.source=c.source.replace('**Lectura de cobertura:** la teoría se añade al panel de producción observada. Una observación real puede existir aunque la curva no tenga rendimiento para una edad de siembra de ese origen. Eso se informa como soporte teórico incompleto y activa el respaldo; no mide el cruce cama–estadística. Las fechas del plano determinan el inventario y la edad se calcula hasta la semana objetivo.', '')
    addition='\n\n**Qué significa el 21,83 %:** se calcula en esta base analítica, sobre 211.001 filas con producción real observada. En 46.051 filas existe un plano emparejado y la curva representa las edades de todas las cohortes, por lo que puede aportar su total teórico. No es porcentaje de camas unidas ni de producción conservada. Las filas reales permanecen en la base. Entre las que cumplen los requisitos de historia del modelo, las que no tienen referencia teórica directa usan producción reciente; las demás no entran a predicción, aunque siguen disponibles para análisis. Es normal que una curva empírica no represente cada edad de cada variedad.'
    if 'Qué significa el 21,83 %:' not in c.source:c.source+=addition
    for cell in n.cells:
        if cell.cell_type=='markdown':
            cell.source=cell.source.replace('## 1. Calidad, calendario, ceros y cobertura','## 1. Calidad, calendario, ceros y cuándo aplica la curva')
        elif cell.cell_type=='code':
            cell.source=cell.source.replace("print('La teoría completa cubre',round(100*observados.curva_completa.mean(),2),'% de casos con producción observada.')", "print('En la base analítica, la curva representa todas las edades de las cohortes en',round(100*observados.curva_completa.mean(),2),'% de casos con producción real observada.')")
            cell.source=cell.source.replace("print('Variedades sin proyección completa:',observados.loc[~observados.curva_completa,'variedad'].nunique())", "print('Variedades con al menos un caso sin referencia teórica directa:',observados.loc[~observados.curva_completa,'variedad'].nunique())")
            cell.source=cell.source.replace("print('El modelo evaluará ajuste de teoría, clima y revisiones sobre casos comunes; los faltantes activan respaldo explícito, no ceros inventados.')", "print('El modelo conserva los casos admisibles: usa la curva cuando representa todas las cohortes y producción reciente como respaldo en los demás.')")
        for out in getattr(cell,'outputs',[]):
            for key in ('text','data'):
                value=out.get(key)
                if isinstance(value,str):
                    value=value.replace('La teoría completa cubre','En la base analítica, la curva representa todas las edades de las cohortes en')
                    value=value.replace('Variedades sin proyección completa','Variedades con al menos un caso sin referencia teórica directa')
                    out[key]=value
                elif isinstance(value,dict):
                    for mime,body in list(value.items()):
                        if isinstance(body,str):
                            value[mime]=body.replace('La teoría completa cubre','En la base analítica, la curva representa todas las edades de las cohortes en').replace('Variedades sin proyección completa','Variedades con al menos un caso sin referencia teórica directa')
    if not any(cell.cell_type=='markdown' and 'Diagrama: de dónde sale el 21,83 %' in cell.source for cell in n.cells):
        n.cells.insert(1,nbformat.v4.new_markdown_cell('''## Diagrama: de dónde sale el 21,83 %

![Flujo de datos piloto, curva empírica y ruta de pronóstico.](../../Trabajo%20escrito/Figuras_resultados/flujo_uso_curva_y_ruta_modelo.png)

El 21,83 % se calcula **en la base analítica final**, no en la tabla de cruces. Su unidad es un caso serie–origen–horizonte con producción real observada. La referencia directa requiere que haya un plano emparejado y que la curva represente todas las edades de sus cohortes. Las observaciones reales permanecen en la base. Si el caso es admisible para el modelo, pero no tiene referencia directa, se pronostica con producción reciente; si no cumple los requisitos de historia, no recibe predicción aunque siga registrado. Es normal que una curva histórica no represente todas las edades; por sí sola no demuestra error de datos.'''))
    reason_note=(f"\n\n**Qué hay en los demás estados:** {num(reason_counts.get('cohortes_sin_curva',0),0)} casos tienen alguna edad de cohorte no representada en la curva; "
                 f"{num(reason_counts.get('sin_pareja_comercial_u_objetivo',0),0)} no tienen pareja de serie/objetivo con un plano; "
                 f"{num(reason_counts.get('sin_snapshot_disponible',0),0)} no tienen un plano elegible. En los tres estados la producción real sigue en la base. "
                 "El último caso no se confunde con el cruce entre estadísticas de pilotos y camas.")
    for cell in n.cells:
        if cell.cell_type=='markdown' and 'Diagrama: de dónde sale el 21,83 %' in cell.source and '**Qué hay en los demás estados:**' not in cell.source:
            cell.source += reason_note

    diagram=next((cell for cell in n.cells if cell.cell_type=='markdown' and 'Diagrama: de dónde sale el 21,83 %' in cell.source),None)
    if diagram is not None:
        diagram.source=f'''## Diagrama: de dónde sale el 21,83 %

![Flujo de datos piloto, curva empírica y ruta de pronóstico.](../../Trabajo%20escrito/Figuras_resultados/flujo_uso_curva_y_ruta_modelo.png)

El 21,83 % se calcula **en la base analítica final**, no en la tabla de cruces. Su unidad es un caso serie–origen–horizonte con producción real observada. La referencia directa requiere un plano emparejado y que la curva represente todas las edades de sus cohortes. La producción real permanece en la base. Si un caso sin referencia directa cumple los requisitos de historia, el modelo lo pronostica con producción reciente; si no los cumple, queda registrado para análisis, pero no recibe predicción. Es normal que una curva empírica no represente todas las edades de cada plano: eso limita cuándo usar esa curva, no indica que falte producción ni que haya fallado el cruce de datos.

**Estados en la base analítica:** {num(reason_counts.get('cohortes_sin_curva',0),0)} casos tienen alguna edad de cohorte no representada en la curva; {num(reason_counts.get('sin_pareja_comercial_u_objetivo',0),0)} no tienen pareja de serie/objetivo con un plano; {num(reason_counts.get('sin_snapshot_disponible',0),0)} no tienen un plano elegible. Cuando existe producción observada, esos registros permanecen. La posibilidad de pronosticar depende aparte de que cada caso cumpla los requisitos de historia. Este porcentaje tampoco mide el cruce entre estadísticas de pilotos y camas.'''

def edit02(n):
    replacements={
        '# 02 — ¿Faltan edades de curva o son plantas que todavía no producen?':'# 02 — ¿Qué edades representa la curva empírica?',
        '## 1. Clasificar las edades sin cobertura en todas las ediciones':'## 1. Edades representadas por las curvas en todas las ediciones',
        '## 2. ¿Qué explica la cobertura de la base analítica?':'## 2. ¿En qué casos se puede usar la referencia directa de curva?',
        '## 4. Exportar la evidencia y leerla sin confundir ausencia con cero':'## 4. Leer el alcance de la curva sin confundirlo con producción perdida',
    }
    for cell in n.cells:
        if cell.cell_type=='markdown':
            for old,new in replacements.items(): cell.source=cell.source.replace(old,new)
            cell.source=cell.source.replace('La segunda parte vuelve a los casos observados de la base y verifica la correspondencia con sus faltantes.', 'La segunda parte vuelve a los casos con producción observada y clasifica qué edades de cohortes no están representadas por la curva; no es una auditoría de pérdida de producción.')
            cell.source=cell.source.replace('Cada caso de pronóstico puede tener varios grupos faltantes y varias causas. Primero verificamos que los grupos reconstruidos igualen `sin_cobertura` de la base. Después se informa una clasificación **excluyente por caso**: todos sus faltantes son tempranos, todos son huecos del rango, todos son edades posteriores, causas mezcladas u otros estados. Solo la primera es candidata a revisar el supuesto de etapa preproductiva; no demuestra producción cero.', 'Este indicador se calcula en la base analítica y marca los casos donde la curva no representa todas las edades de sus cohortes. La clasificación **excluyente por caso** distingue si las edades no representadas son tempranas, huecos interiores, edades posteriores o una mezcla. No cuenta producción perdida ni cruces fallidos. Solo las edades tempranas son candidatas a revisar una posible regla preproductiva; no demuestra que su rendimiento sea cero.')
            cell.source=cell.source.replace('El Excel conserva los denominadores y el soporte; las etiquetas son diagnósticos descriptivos.', 'El Excel conserva los denominadores y detalla qué edades están representadas por la curva; las etiquetas son diagnósticos descriptivos, no pérdidas de producción.')
            cell.source=cell.source.replace('# Resultado del EDA de edades sin cobertura', '# Resultado del EDA del alcance de las curvas por edad')
        for out in getattr(cell,'outputs',[]):
            for key in ('text','data'):
                value=out.get(key)
                if isinstance(value,str):
                    for old,new in replacements.items(): value=value.replace(old,new)
                    value=value.replace('sin cobertura','edad no representada por curva').replace('casos incompletos','casos donde no aplica la referencia directa')
                    out[key]=value
    if '**Lectura correcta:**' not in n.cells[0].source:
        n.cells[0].source += '\n\n**Lectura correcta:** este notebook describe qué edades están representadas en las curvas piloto para las cohortes de cada plano. La producción real se conserva en la base analítica. Cuando no hay referencia directa, las filas admisibles usan la ruta de producción reciente; las que no cumplen los requisitos de historia permanecen en la base, pero no reciben predicción. Esto es un límite normal de una curva empírica y no equivale a pérdida de registros ni a falla general del cruce.'

def edit_reading(n):
    n.cells[0].source=summary_text
    n.cells[4].source=(ROOT/'GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md').read_text(encoding='utf-8')
    c=n.cells[9]
    c.source=c.source.replace('**Lo que decía la proyección teórica:** sumaba **27.916,61 tallos**, pero **2 de las 25 cohortes no tenían cobertura válida**. Por eso `curva_completa` es falso, `motivo_cobertura` es `cohortes_sin_curva` y `teoria_modelo` está vacío. Esa suma parcial no se debe interpretar como una teoría completa ni como el pronóstico final.', '**Lo que permite calcular la curva:** la suma parcial del plano es **27.916,61 tallos**. De sus **25 cohortes**, la curva representa las edades de 23; las otras dos (edades 9 y 16) no tienen tasa teórica asignada en esa curva. El cruce de camas y la producción real no se pierden por esto. Como no se usa una suma parcial como total del plano, `teoria_modelo` queda vacío y, si la fila es admisible, el modelo usa la ruta basada en producción reciente.')
    c=n.cells[9].source.replace('La fila sigue siendo admisible','La fila sigue siendo admisible')
    n.cells[9].source=c
    replacements={
        'Puede ser parcial si faltan grupos por cubrir; no es el pronóstico final del modelo.':'Puede ser parcial si la curva no representa la edad de todas las cohortes; no es el pronóstico final ni se usa como referencia teórica directa.',
        'Cantidad de cohortes sin cobertura válida de proyección; los estados proyectada y siembra_posterior no cuentan como faltantes.':'Cantidad de cohortes cuya edad objetivo no está representada en la curva aplicada. Es un indicador de aplicabilidad de la curva, no de pérdida de filas de producción.',
        'Verdadero cuando existe teoría y sin_cobertura es cero; indica cobertura completa de esa proyección.':'Verdadero cuando la curva representa las edades de todas las cohortes y permite usar el total teórico como referencia del modelo.',
        'Valor de teoria habilitado como base teórica: se conserva si curva_completa es verdadero y queda vacío si la proyección es parcial. No es la predicción final del modelo. En DINO está vacío porque hay dos grupos sin cobertura.':'Valor de teoria habilitado como referencia directa: se conserva si la curva representa todas las cohortes. En DINO queda vacío porque dos edades no están representadas; la producción real permanece y se usa la ruta de respaldo si la fila es admisible.',
        'ambas columnas están vacías porque solo conservan teorías anteriores con cobertura completa.':'ambas columnas están vacías porque solo conservan referencias anteriores aplicables a todas las cohortes.',
        'no exige teoría completa ni y conocido':'no exige que la curva represente todas las cohortes ni y conocido',
        'Explica la cobertura teórica: curva_completa = proyección cubierta; cohortes_sin_curva = quedan grupos sin cobertura válida;':'Indica si la referencia directa de curva se puede aplicar: curva_completa = todas las edades de las cohortes están representadas; cohortes_sin_curva = alguna edad no está representada;'
    }
    for old,new in replacements.items(): n.cells[10].source=n.cells[10].source.replace(old,new)
    n.cells[10].source=n.cells[10].source.replace('Las teorías previas están vacías por cobertura incompleta', 'Las referencias previas no se habilitan porque la curva no representa todas las cohortes')
    n.cells[10].source=n.cells[10].source.replace('el código conserva únicamente valores anteriores con cobertura completa', 'el código conserva únicamente referencias de versiones anteriores aplicables a todas las cohortes')
    n.cells[10].source=n.cells[10].source.replace('**Ejemplo inventado con cobertura completa:**', '**Ejemplo inventado con referencia de curva aplicable a todas las cohortes:**')
    n.cells[10].source=n.cells[10].source.replace('Grupos sin cobertura','Cohortes con edad no representada')
    n.cells[10].source=n.cells[10].source.replace('grupos sin cobertura','cohortes con edad no representada')
    n.cells[10].source=n.cells[10].source.replace('teoría completa','referencia aplicable a todas las cohortes')

def edit15(n):
    c=n.cells[12]
    m=c.source.index('Memoria_larga obtiene') if 'Memoria_larga obtiene' in c.source else -1
    if m>=0:
        c.source=c.source[:m]+f"Memoria_larga obtiene {pct(exp_df.set_index('metodo').loc['Memoria_larga','WAPE'])} en los mismos {num(int(exp_df.set_index('metodo').loc['Memoria_larga','n']),0)} casos del panel principal. La comparación con/sin clima, lluvia y curva local está en 19; la elección sigue fijada por validación anterior a 2026. `Antes_calidad` conserva una ejecución histórica con clima anterior y no aísla el efecto de la auditoría de octubre. Consultar las tablas ejecutadas para los resultados vigentes."

def edit18(n):
    c=n.cells[6]
    marker='**Lectura de la ejecución actual:**'
    if marker in c.source:c.source=c.source.split(marker)[0]+marker+' '+climate_end

def edit20(n):
    c=n.cells[14]
    c.source=error_text

def editannual(n):
    c=n.cells[22]
    c.source='''## Revisión explícita: alcance de las curvas por variedad y edad

La tabla distingue variedades sin historia piloto utilizable de variedades cuya historia sí existe, pero no representa alguna edad del inventario del plano. Una estadística de cama piloto puede estar correctamente cruzada y la producción real conservarse, aunque la curva no se aplique a todas las cohortes de otro inventario. En esos casos el modelo continúa con su ruta basada en producción reciente.

Los controles de calidad (cortes negativos, plantas inválidas, nombres o ciclos pendientes y repeticiones) se informan aparte. Una fila no identificada no se interpreta automáticamente como cero ni como edad improductiva. Los motivos pueden superponerse en la auditoría; no se suman como si fueran categorías excluyentes.

Las listas describen qué edades están representadas por los pilotos en la ventana histórica de 78 semanas para cada plano. No describen producción perdida, ausencia permanente de una variedad ni una falla general de las fuentes. El EDA 02 clasifica edades tempranas, huecos interiores y edades posteriores para revisar su significado agronómico; no convierte ninguna de ellas en cero.'''

edit_markdown('Notebooks/Analisis/12_modelo_ajuste_proyecciones.ipynb',edit12)
edit_markdown('Notebooks/Analisis/11_EDA_proyecciones.ipynb',edit11)
edit_markdown('Notebooks/Analisis/15_calidad_y_mejora_por_horizonte.ipynb',edit15)
edit_markdown('Notebooks/Analisis/18_EDA_clima_y_desfase.ipynb',edit18)
edit_markdown('Notebooks/Analisis/20_EDA_origen_error_modelo_ingeniero.ipynb',edit20)
edit_markdown('Notebooks/Proyecciones Teoricas Propias/02_EDA_edades_sin_cobertura.ipynb',edit02)
edit_markdown('lectura.ipynb',edit_reading)
edit_markdown('Notebooks/Proyecciones Teoricas Propias/Proyecciones_teoricas_todos_los_anios.ipynb',editannual)

# Escribe texto y resumen sólo cuando todas las fuentes se leyeron y verificaron.
(DOC / 'Desarrollo_del_documento.md').write_text(text, encoding='utf-8')
(ROOT / 'resumen_modelos_pronostico.md').write_text(summary_text, encoding='utf-8')
print(f'Informe actualizado; correspondencias únicas 2026: {recent_joined:,}/{len(recent):,}; referencia de curva aplicable: {full:,}/{len(obs):,}; WAPE semanal: {current["WAPE"]:.4%}.')
