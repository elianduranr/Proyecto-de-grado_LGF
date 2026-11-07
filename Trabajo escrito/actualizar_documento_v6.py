"""Edición metodológica v6: orden, separación semanal/diaria y menos repetición."""
from pathlib import Path
import re

path = Path(__file__).with_name("Desarrollo_del_documento.md")
text = path.read_text(encoding="utf-8")

text, n = re.subn(
    r"## Resumen\n.*?\nPalabras clave:",
    """## Resumen

Este trabajo desarrolla un pronóstico semanal de tallos reportados para GAITANA y, como tarea aparte aún en revisión, explora la distribución diaria de H1. El modelo semanal seleccionado antes de evaluar 2026 es HistGradientBoosting sin clima: usa un ajuste para H1–H2 y otro para H3–H5, con los mismos parámetros, y corrige la teoría o la media de cuatro semanas según corresponda. En 16.325 comparaciones, obtiene 19,36 % de WAPE frente a 19,71 % del ingeniero; gana en H1–H2 y en el total, mientras el ingeniero gana en H3–H5. Los resultados son retrospectivos. El pronóstico diario tiene evaluaciones exploratorias y aún no cuenta con una comparación equivalente contra el ingeniero.

Palabras clave:""",
    text, count=1, flags=re.S)
assert n == 1

weekly_methods = """### 4.2.1. Modelos semanales probados y por qué se compararon

La teoría de la curva es una referencia productiva, no el pronóstico final por sí sola. Se estima como punto de partida cuando representa las edades de todas las cohortes del plano. El modelo aprende la diferencia entre producción real y teoría; cuando la curva no representa todas las edades, aprende una corrección sobre Media4. Así se conservan dos rutas interpretables y cada caso usa la referencia que sí aplica.

HistGradientBoosting se probó porque sus árboles pueden aprender relaciones no lineales entre memoria, producto y horizonte. Ridge sirve de contraste lineal regularizado. Las referencias simples y las ablaciones muestran si el aprendizaje y cada bloque de variables aportan algo frente a reglas más sencillas. La secuencia completa es:

| Cuaderno / modelo | Qué hace | Entradas principales | Decisión o conclusión |
| --- | --- | --- | --- |
| 12 · `Ultimo_valor`, `Media4`, `Teoria_sin_ajuste` | Repite el último dato, promedia cuatro semanas o usa la curva sin corregir. | Una referencia cada vez. | Puntos de comparación sencillos para todos los H1–H5. |
| 12 · `Ajuste_media4_sin_planos` | Boosting estima real−Media4 y suma la corrección a Media4. | Identidad comercial, calendario, memoria real y clima disponible; no recibe teoría. | Respaldo para casos sin curva aplicable. |
| 12–13 · `Modelo_teorico` / `Sistema_teoria_con_respaldo` | Boosting estima real−teoría; si la curva no aplica, el sistema usa el ajuste de Media4. | Identidad, horizonte/calendario, rezagos y tendencias reales, clima y variables de curva en la ruta teórica. | Arquitectura de dos rutas; no promedia ambas referencias. |
| 12 · `Ridge_ajuste_teoria`, `Teorico_sin_memoria`, `Teorico_sin_clima` | Ridge prueba una corrección lineal; las otras dos variantes quitan memoria o clima. | Mismo problema con una diferencia controlada por variante. | Contrastes para medir no linealidad y aporte de cada bloque. |
| 12 · `Modelo_teorico_historia` | Añade revisiones de teorías anteriores para la misma semana objetivo. | Teoría actual, variables semanales y versiones previas. | Prueba si los cambios entre planos agregan señal. |
| 14 · Boosting semanal con señales de corte diario | Mantiene el objetivo semanal y añade 28 resúmenes de corte/clima recientes. | Ventanas 3/5/7/14 días, rezagos, conteos, dispersión, EMA y tendencias. | Prueba si una trayectoria diaria creciente o decreciente anticipa el total semanal. No es el modelo diario. |
| 15 · Boosting con memoria larga y grupos | Añade memoria de hasta 12 semanas, dispersión/conteos y prueba H1–H2 separado de H3–H5. | Producción histórica y, en una variante, teorías previas. | Motiva el uso de dos grupos de horizontes; pesos fijados con validación de 2025. |
| 19 · **Boosting sin clima, selección anual** | Dos grupos de HistGradientBoosting corrigen teoría o Media4: H1–H2 y H3–H5. | Memoria semanal/diaria y de 12 semanas, identidad/calendario y teoría cuando aplica; sin clima. | Ganador anual entre variantes propias, elegido antes de evaluar 2026. Detalle de variables y parámetros en 4.2.5. |
| 22–24 · Modelos separados por horizonte | Entrena un modelo por cada H1, H2, H3, H4 y H5; ajusta `max_iter` con validación temporal. | Variables semanales, memoria y teoría; clima sólo si hay cobertura suficiente. | Experimento distinto del ganador anual. La validación eligió 80 iteraciones en H1, H2 y H5, y 40 en H3 y H4. |
| 25 · Ensamble reciente con especialización por producto | Conserva el grupo H1–H2 para H1 y el modelo H2 separado. En H3–H5, para Minicarnation y Carnation combina un modelo entrenado sólo con ese producto y horizonte con el modelo general del mismo horizonte. Otros productos conservan el general. | Producción previa, calendario, teoría y proyecciones anteriores si aplican; el clima no estaba disponible en esta corrida. | Experimento reciente de 1.226 casos; no reemplaza la selección anual. La mezcla y sus parámetros se explican en 5.1.1. |

La palabra “especializado” en el cuaderno 25 significa que el ajuste H3 de Minicarnation, por ejemplo, se entrena sólo con la historia de Minicarnation en H3. No es una familia distinta de algoritmo: sigue siendo HistGradientBoosting. En la mezcla se pondera esa predicción especializada y el modelo general por horizonte; el peso se determina con validación anterior, no con el ingeniero ni con las semanas recientes de evaluación.

"""
text, n = re.subn(
    r"### 4\.2\.1\..*?\n.*?\n### 4\.2\.2\.",
    weekly_methods + "\n### 4.2.2.", text, count=1, flags=re.S)
assert n == 1

# Eliminar dos resúmenes tabulares repetidos: la matriz anterior ya identifica candidatos,
# y el diccionario detallado de columnas se conserva en el anexo.
text, n = re.subn(
    r"\n\| Nombre de resultados \(12\) \| Algoritmo y referencia \| Información y pregunta \|\n.*?\nLos nueve métodos iniciales se puntúan en casos comunes donde la curva representa todas las edades de las cohortes\. Las ablaciones mantienen la misma población y parámetros, cambiando un bloque\. En cambio, el ajuste Media4 aprende con todos sus casos admisibles; compararlo con el ajuste basado en curva cambia la población de entrenamiento\. El sistema completo se evalúa aparte sobre los casos admisibles, con una ruta para cada situación\.\n",
    "\n",
    text, count=1, flags=re.S)
if n != 1:
    print("Aviso: no se encontró el bloque histórico repetido; se conserva.")

# Precisar la configuración seleccionada y separar del tuning por horizonte.
text, n = re.subn(
    r"### 4\.2\.5\. Modelo semanal seleccionado: arquitectura, variables y parámetros\n.*?\n### 4\.2\.6\. Secuencia temporal de entrenamiento, validación y evaluación",
    """### 4.2.5. Modelo semanal seleccionado: arquitectura, variables y parámetros

El ganador anual es el **Boosting sin clima del cuaderno 19**. No se entrenó un parámetro distinto para cada H. Se ajusta un modelo para H1–H2 y otro para H3–H5; dentro de cada grupo se crean dos regresiones complementarias: una corrige la teoría en los casos donde la curva cubre todas las edades y otra corrige Media4 como respaldo. Cada fila toma sólo la ruta que le corresponde; no se promedian teoría y Media4.

La ruta de Media4 recibe producto, color, variedad, horizonte y calendario, nueve variables de memoria semanal, 28 resúmenes diarios de producción/clima ya observados y siete señales de memoria larga. La ruta teórica recibe ese mismo bloque más `teoria_modelo`, `antiguedad_curva` y `desviacion_reciente_teoria`. Como se eligió la variante sin clima, no entran columnas meteorológicas al modelo final. La imputación numérica usa medianas calculadas en train y las categorías se codifican con indicadores; la cobertura decide la ruta, pero no se entrega al algoritmo como predictor.

Los dos grupos y las dos rutas comparten la misma configuración de HistGradientBoostingRegressor:

| Parámetro | Valor | Interpretación sencilla |
| --- | ---: | --- |
| Tasa de aprendizaje (`learning_rate`) | 0,08 | Cuánto aporta cada árbol nuevo. |
| Iteraciones máximas (`max_iter`) | 80 | Número de etapas de árboles. |
| Hojas máximas por árbol (`max_leaf_nodes`) | 15 | Complejidad permitida a cada árbol. |
| Mínimo por hoja (`min_samples_leaf`) | 40 | Evita reglas basadas en muy pocos casos. |
| Regularización L2 | 1,0 | Penaliza ajustes excesivamente grandes. |
| Parada temprana | No | Usa las 80 iteraciones definidas. |
| Semilla (`random_state`) | 42 | Hace reproducible la ejecución. |

Por tanto, aunque el sistema tenga varios ajustes por grupo y por ruta, **no tiene hiperparámetros distintos entre H1–H2 y H3–H5**. Los parámetros diferentes aparecen en el experimento posterior de modelos separados por horizonte (cuadernos 22–24), no en el ganador anual. Allí se eligieron 80 iteraciones para H1, H2 y H5 y 40 para H3 y H4; se mantuvieron 15 hojas y el resto de la configuración. Esa variante no sustituyó al ganador anual.

### 4.2.6. Secuencia temporal de entrenamiento, validación y evaluación""",
    text, count=1, flags=re.S)
assert n == 1

# Aclarar que cortes diarios de 14 son predictores semanales.
text = text.replace("### 4.2.2. Cortes diarios como variables del pronóstico semanal", "### 4.2.2. Variables diarias que alimentan el pronóstico semanal")

# Reemplazar la explicación genérica del modelo reciente por su composición concreta.
text, n = re.subn(
    r"### 5\.1\.1\. Experimento reciente: proteger H1 y H2 y mejorar H3–H5\n.*?\n### 5\.2\. Precisión diaria",
    """### 5.1.1. Ensamble reciente: productos especializados en H3–H5

Este experimento no es el ganador anual. Compara 1.226 pronósticos de GAITANA en tres semanas objetivo recientes. El ingeniero se usa sólo para medir. La palabra “ensamble” describe una mezcla de dos predicciones propias, no una suma de modelos sin regla:

| Horizonte/producto | Qué predice el candidato | Cómo se obtiene el valor final |
| --- | --- | --- |
| H1, todos los productos | Modelo general agrupado H1–H2 | Se conserva directamente. |
| H2, todos los productos | Modelo general separado H2 | Se conserva directamente. |
| H3–H5, productos distintos de Minicarnation y Carnation | Modelo general separado para cada horizonte | Se conserva directamente. |
| H3–H5, Minicarnation y Carnation | Un HistGradientBoosting por producto y horizonte, entrenado sólo con ese producto, más el modelo general separado del horizonte | `predicción final = (1 − peso) × general + peso × especializado`. El peso se eligió con validación previa de noviembre. |

Para las dos variedades comerciales priorizadas se eligieron pesos de 1,00 en H3, 1,00 en H4 y 0,75 en H5. Así, en H3 y H4 se usa la predicción especializada; en H5 se combinan 75 % de la especializada y 25 % de la general. Los pesos son iguales para Minicarnation y Carnation. No se utiliza la predicción del ingeniero para entrenar ni para determinar los pesos.

Los modelos especializados usan HistGradientBoostingRegressor. En la validación previa se eligieron 40 iteraciones para Minicarnation en H3–H5 y 80 iteraciones para Carnation en H3–H5; todos usan 15 hojas. Se mantienen tasa de aprendizaje 0,08, mínimo de 40 casos por hoja, regularización L2 de 1, sin parada temprana y semilla 42. El modelo general por horizonte usa 80 iteraciones en H1/H2/H5 y 40 en H3/H4, con 15 hojas y los mismos valores restantes. La selección de parámetros y pesos ocurrió en noviembre, separada de las tres semanas recientes de evaluación. En esa corrida el clima no estaba disponible en las entradas, así que estos modelos funcionaron sin clima.

| Horizonte | Candidato reciente | WAPE candidato / ingeniero | Sesgo candidato / ingeniero | Lectura |
| --- | --- | ---: | ---: | --- |
| H1 | General agrupado H1–H2 | 12,28 % / 15,23 % | +2,75 % / -7,79 % | Candidato gana WAPE; sobreestima ligeramente. |
| H2 | General separado H2 | 14,96 % / 14,98 % | -0,02 % / -5,80 % | Empate práctico en WAPE; sesgo del candidato casi neutro. |
| H3 | General + mezcla especializada para dos productos | 17,27 % / 16,51 % | -5,85 % / -7,99 % | Ingeniero gana WAPE. |
| H4 | General + mezcla especializada para dos productos | 18,89 % / 16,79 % | -3,96 % / -7,67 % | Ingeniero gana WAPE. |
| H5 | General + mezcla 75/25 para dos productos | 19,76 % / 16,95 % | -7,76 % / -7,86 % | Ingeniero gana WAPE. |
| Total | Ensamble por horizonte/producto | 17,53 % / 16,34 % | -4,22 % / -7,51 % | Ingeniero gana el total. |

El ensamble reduce el WAPE del candidato previo de 17,80 % a 17,53 %, pero todavía no supera al ingeniero en el total ni en H3–H5. La mejora reciente de H1 es clara; H2 es un empate práctico. Esta evaluación breve no desplaza al Boosting sin clima anual.

### 5.2. Precisión diaria""",
    text, count=1, flags=re.S)
assert n == 1

# Quitar tablas históricas añadidas al final que repiten resultados antiguos y se contradicen
# con el panel anual actualizado; los inventarios reproducibles siguen en los notebooks.
text, n = re.subn(
    r"\n### Inventario adicional de algoritmos y referencias\n.*?(?=\n## Anexo\. Diccionario de la base analítica común)",
    "\n",
    text, count=1, flags=re.S)
assert n == 1

path.write_text(text, encoding="utf-8")
print("Documento v6 reorganizado; resumen unificado, metodología semanal/diaria separada y tablas históricas redundantes retiradas.")
