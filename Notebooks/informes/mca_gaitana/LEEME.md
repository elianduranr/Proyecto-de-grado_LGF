# MCA de la producción histórica de GAITANA

La entrega principal es `Notebooks/05_MCA_2026.ipynb`, con las celdas ejecutadas, sus salidas y comentarios interpretativos. El nombre del notebook se conserva, pero la selección inicial incluye los archivos de 2021 a 2026.

En esta carpeta:

- `analisis_mca_gaitana.html`: lectura del notebook con tablas y figuras, sin ejecutar Python.
- `resultados_mca_gaitana.xlsx`: tablas completas de auditoría, categorías, coordenadas, contribuciones, cos², recurrencia y sensibilidad.
- `interpretacion_mca_gaitana.md`: comentarios y conclusiones calculados.
- `parametros.json`: configuración y tamaño de la base del análisis.
- Archivos PNG: figuras para exportar o incluir en documentos.

## Fuentes y alcance

Se leen los Excel de `Datos/Producción real`, incluyendo hojas de continuación reconocidas por sus columnas. Todas las etapas de análisis reciben exclusivamente GAITANA. La base limpia, las cachés y las copias exactas entre fuentes retiradas se guardan en `Datos/modelado/mca_produccion`.

La limpieza toma como referencia la sección de producción del notebook 03: filas vacías, tipos, columnas operativas descartadas e imputación de corte con moda de producto–color–variedad en ±1 semana. Se elimina Sector porque identifica al supervisor; no interviene en ninguna etapa del análisis ni en la conciliación de copias.

La sección 0.2 añade imputación retrospectiva en columnas separadas: misma variedad, producto y color, categoría dominante coincidente entre al menos dos años, 30 donantes por año y acuerdo mínimo de 95 %. Se valida ocultando años completos y se descarta una regla si algún año con 1.000 predicciones no alcanza 90 % de acierto por registros o tallos. En esta ejecución se completan 61.003 grados adicionales; se rechaza trasladar tipos de corte entre años por su bajo acierto. Los faltantes restantes tienen la etiqueta SIN_REFERENCIA en las columnas analíticas, sin borrar filas.

`produccion_gaitana_auditada.parquet`, en la carpeta de datos modelados, conserva las columnas originales, las imputaciones, sus métodos y las alertas. La sección 6.2 ajusta un MCA con grado imputado y SIN_REFERENCIA que incluye todos los registros de la base MCA. Se mantiene el análisis de grados observados como referencia; los grados estimados no se presentan como observaciones confirmadas.

El análisis principal usa producto y color (caso bivariado del MCA). Los ajustes con semana o grado añaden una tercera variable activa. Variedad e invernadero se mantienen como suplementarias, y el detalle comercial compara variedades dentro de cada producto y año.

Se conserva la multiplicidad de registros idénticos dentro de una hoja. Solo se concilian copias idénticas entre fuentes, con su detalle disponible en `solapamientos_retirados.parquet`. La copia de diciembre de 2024 incluida en el libro de 2025 es el solapamiento encontrado en esta ejecución.

La sección 1.1 audita el pico de 2021-S42: 2.282.123 tallos en dos tramos de 16.168 filas de Sheet1. Coinciden 16.125 registros entre tramos (99,73 %), conservando multiplicidades en fecha, producto, color, variedad, invernadero y tallos. Es una posible copia o segunda versión; se conservan ambos tramos y se muestran escenarios sin sustituir el total observado. El Excel de resultados incluye el detalle de 32.336 filas y muestras del archivo original; `detalle_pico_2021.parquet` guarda el mismo detalle.

La semana ISO se proyecta como suplementaria y también se prueba como activa. Se comparan por separado curvas de participación y de volumen semanal. El MCA ordinario trata la semana como nominal: la cronología se interpreta mediante las gráficas y el análisis temporal complementario.

## Ejecución

En el notebook, cambia `ANIOS_ARCHIVO` o `ANIOS_ISO` si quieres acotar el periodo. Dejarlos en `None` mantiene todo el histórico. Ejecuta las celdas en orden. La caché se verifica mediante ruta, tamaño, modificación de las fuentes y versión de las reglas.

Desde la raíz del proyecto también puedes ejecutar:

```powershell
.\entorno_tesis\Scripts\python.exe scripts/ejecutar_notebook05_mca.py
```

Este comando vuelve a ejecutar las celdas actuales y exporta el HTML. `construir_notebook05_mca.py` es el generador de la estructura inicial: reconstruye las celdas y guarda un respaldo temporal, por lo que no es el comando de ejecución habitual.

Validaciones de carga, filtro de finca, conservación, imputación, MCA ponderado y recurrencia:

```powershell
.\entorno_tesis\Scripts\python.exe scripts/validar_mca_produccion.py
```

El entorno utilizado incluye pandas, numpy, scipy, matplotlib, seaborn, openpyxl, lxml, pyarrow, python-calamine, nbformat, nbclient, nbconvert e ipykernel. Calamine acelera la lectura; existe una alternativa XML en el módulo si no está disponible.

## Límites de interpretación

En los archivos actuales falta el grado en 2021 y en parte de 2022; por eso se separan el MCA de toda la producción y el MCA comercial con grado conocido. La semana 6 de 2022 no tiene registros de GAITANA y 2026 llega hasta la semana 35. El contraste de recurrencia utiliza el tramo común contiguo 7–35, sin inventar ceros para las semanas ausentes.

Las asociaciones no identifican causalidad, calidad de flor ni rentabilidad. Los contrastes de desplazamientos semanales son exploratorios y dependen de supuestos de comparabilidad temporal; no sustituyen una validación predictiva en años reservados. Las referencias metodológicas están en el notebook.
