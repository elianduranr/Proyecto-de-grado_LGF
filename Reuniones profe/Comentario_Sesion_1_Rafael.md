# Continuidad para la próxima sesión

Actualizado: **20 de agosto de 2026, America/Bogota**.

## Punto de partida

El flujo completo está integrado en un solo notebook autocontenido:

`Notebooks/01_preprocesamiento_y_eda_tesis.ipynb`

Estado verificado de la última ejecución:

- 148 celdas totales;
- 65 celdas de código, todas ejecutadas;
- 0 errores guardados;
- no importa módulos `.py` locales;
- no existe un notebook 02 ni scripts temporales;
- se retiró por completo el análisis denominado “ciclo observable”.

Para ejecutar desde la raíz del proyecto:

```powershell
.\entorno_tesis\Scripts\python.exe -m jupyter nbconvert --to notebook --execute --inplace "Notebooks\01_preprocesamiento_y_eda_tesis.ipynb" --ExecutePreprocessor.timeout=3600 --ExecutePreprocessor.kernel_name=python3
```

La primera extracción de Curvas puede tardar aproximadamente 13 minutos. Si los Excel no cambiaron, el manifiesto reutiliza los 48 CSV limpios y la ejecución completa tarda cerca de 3–4 minutos.

## Trabajo terminado en esta sesión

1. Se incorporaron los 24 Excel de `Datos/Curvas por variedad/<año>/` correspondientes a 2021–2026.
2. Se procesan las hojas `Base de Datos` y `Camas Piloto`. Para Green Ball, `corte semanal` es la hoja longitudinal equivalente a `Base de Datos`.
3. Se detecta automáticamente la fila real de encabezado. Clavel la tiene en la fila 1; Miniclavel y Raffine/Solomio suelen tener una fila numérica auxiliar y el encabezado real en la fila 2.
4. Los libros con nombres de impresión XML inválidos se leen desde copias técnicas reparadas en `_control`; los originales no cambian.
5. Se construyó una cascada auditable de match entre la base longitudinal y las camas piloto.
6. Se verificaron directamente las unidades mediante `Corte Semanal / No. Plantas`.
7. Se creó una curva robusta por variedad y edad usando mediana, media, P25, P75, desviación, observaciones y camas.
8. Se reprodujo la regla `plantas × flores/planta/semana` para las cinco semanas siguientes.
9. Se comparó la réplica contra producción real y contra el estimado histórico del ingeniero.
10. Se actualizaron `CONTEXTO_GENERAL_PROYECTO.md` y los archivos `LEEME.md` de las fuentes afectadas.

## Hallazgos que no deben perderse

### Unión de camas piloto

Sobre 2.347.275 observaciones:

- 78,24 %: `match_exacto_normalizado` por referencia única;
- 5,21 %: `match_referencia_fecha`, útil cuando una referencia fue reutilizada;
- 15,13 %: `ambiguo`; no se expande ni se escoge arbitrariamente;
- 1,42 %: `sin_match`.

La cascada también contempla variedad + bloque + cama, pero solo lo acepta si produce un candidato único. Los matches aproximados no se convierten automáticamente en correspondencias válidas.

### Unidades

- `Corte Semanal`: tallos/semana.
- `Edad`: semanas.
- `Flor/Planta`: flores/planta/semana.
- `No. Plantas`: plantas.
- estimación y producción real: tallos.
- WAPE y cobertura: porcentaje.

En 1.946.600 filas comparables, 99,93 % de `Flor/Planta` coincide con `Corte Semanal / No. Plantas` a tolerancia `1e-8`. La diferencia absoluta mediana es 0.

No usar todavía `Índice Prod`, `Inicio Prod.`, densidad, aprovechamiento ni tallos/m²/año: sus definiciones y factores no están confirmados.

### Estimación a cinco semanas

La réplica usa un único archivo semanal seleccionado de Siembras y una curva construida únicamente con archivos cuyo año es menor o igual al año de emisión. La cobertura mediana es aproximadamente 97,3 % de las plantas.

| Horizonte del proyecto | WAPE réplica | WAPE ingeniero | Sesgo réplica | Sesgo ingeniero |
|---:|---:|---:|---:|---:|
| +1 | 31,43 % | 23,06 % | +1.054 tallos | −603 tallos |
| +2 | 30,63 % | 24,24 % | +923 tallos | −624 tallos |
| +3 | 29,88 % | 24,52 % | +797 tallos | −657 tallos |
| +4 | 29,24 % | 25,26 % | +691 tallos | −640 tallos |
| +5 | 28,72 % | 26,07 % | +608 tallos | −284 tallos |

La réplica pura sobreestima; el ingeniero tiende a subestimar. El ingeniero probablemente aplica factores adicionales todavía no formalizados.

Advertencia: el Excel histórico denomina `horizonte = 1` a la propia semana de emisión. En el proyecto `+1` significa la semana siguiente. El desfase modal es una semana y la comparación correcta se hace por **semana objetivo**, no por igualdad de la etiqueta numérica.

Que el WAPE de la réplica disminuya con el horizonte no demuestra mejor desempeño a largo plazo: cambia la composición de pares comparables.

## Próximos análisis recomendados

Prioridad 1: construir una evaluación de cohorte fija. Conservar únicamente emisiones y variedades comparables en los cinco horizontes, para evitar que el cambio de composición explique la aparente reducción del WAPE.

Prioridad 2: descomponer la diferencia entre la réplica y el ingeniero:

- factor implícito `estimado_ingeniero / estimado_curva`;
- producto, color, variedad y temporada;
- plantas activas y edad;
- cobertura de curva;
- sobreestimación frente a subestimación;
- posibles factores de aprovechamiento, pérdida o ajustes comerciales.

Prioridad 3: revisar los ambiguos de camas piloto. No revisar millones de filas: resumir primero por referencia y priorizar las que concentran más tallos o más observaciones.

Prioridad 4: comparar variantes de curva sin reemplazar la línea base:

- media frente a mediana;
- curva por variedad-color;
- curva por familia cuando falta variedad;
- ventana temporal reciente;
- exclusión robusta de camas atípicas;
- intervalos P25–P75 y escenarios de incertidumbre.

Prioridad 5: corregir la nomenclatura histórica del benchmark. El notebook anterior usa `WMAPE` para la fórmula estándar de WAPE. Mantener la fórmula, pero elegir una sola etiqueta en textos, columnas y gráficas.

## Preguntas para el ingeniero

1. ¿Qué factores aplica después de multiplicar plantas por flores/planta?
2. ¿La edad del Plano de Siembras usa exactamente la misma convención que la edad de las curvas?
3. ¿La semana de emisión se considera la primera de las cinco semanas estimadas?
4. ¿Cómo resuelve referencias de cama reutilizadas o duplicadas?
5. ¿Qué representa `Índice Prod` y por qué en algunos libros incluye densidad?
6. ¿Cómo se aplican aprovechamiento, mortalidad, descarte y porcentaje exportable?
7. ¿Los archivos anuales son fotografías acumuladas o versiones disponibles desde el inicio del año? Se necesita fecha efectiva para controlar totalmente la fuga temporal.

## Archivos clave

- Contexto: `CONTEXTO_GENERAL_PROYECTO.md`.
- Notebook: `Notebooks/01_preprocesamiento_y_eda_tesis.ipynb`.
- Documentación de Curvas: `Datos/Curvas por variedad/datos preprocesados/LEEME.md`.
- Calidad de match: `Datos/Curvas por variedad/datos preprocesados/auditoria/resumen_calidad_match.csv`.
- Casos problemáticos: `auditoria/observaciones_sin_match_o_ambiguas.csv`.
- Validación de unidad: `auditoria/validacion_unidad_flores_por_planta.csv`.
- Curvas agregadas: `bases consolidadas/curvas_por_variedad_edad.csv`.
- Base relacionada: `bases consolidadas/base_curvas_relacionada_camas_piloto.parquet`.
- Comparación detallada: `bases consolidadas/comparacion_curvas_ingeniero_real_variedad.csv`.
- Métricas: `bases consolidadas/metricas_estimacion_por_horizonte.csv`.

## Precauciones

- No modificar Excel crudos.
- No tratar `ambiguo` como match.
- No interpretar ausencia de curva como cero.
- No sumar distintas versiones del estimado del ingeniero.
- No mezclar la semana de emisión con la semana siguiente.
- No reinstalar un notebook 02: el usuario pidió un único notebook de EDA.
- No crear scripts `.py` para generar comentarios o modificar notebooks. El usuario quiere análisis, interpretación y conclusiones dentro del notebook.
