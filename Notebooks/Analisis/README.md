# Base → EDA/benchmark → features → modelos

1. **06_construccion_base_analitica.ipynb** lee limpios y exporta sólo `Datos_analiticos_proyecto/base_analitica.parquet`. Conserva producción como tabla izquierda. Para el ingeniero usa unión estricta y, sólo en pendientes inequívocos, recuperación 1:1 por variedad. Conserva color real/estimado, origen solicitado y archivo efectivamente usado.
2. **07_EDA_base_analitica.ipynb** lee esa base. Analiza cobertura, composición, siembras/edad, clima, rezagos y diferencias frente al ingeniero. Separa referencias recuperadas desde un archivo posterior y distintos métodos de unión. No exporta datasets.
3. **08_features_y_preparacion_modelos.ipynb** lee la misma base. Construye calendario regular, rezagos y ventanas pasadas, casos origen/horizonte y partición temporal en memoria. No entrena ni exporta otra base.
4. **09_modelos_y_comparacion.ipynb** incluye su preparación explícita, entrena Ridge/boosting y compara con baselines en cortes temporales. Prueba el aporte de producción reciente, siembras y clima; muestra una corrección a media4 y una simulación desde el último origen local. No exporta datasets ni declara validada la corrección WebFlor.

Ninguno vuelve a limpiar Excel ni consulta SQL. Las transformaciones están en las celdas, no en módulos propios.

Se excluyen de X el potencial construido con todo el histórico, clima objetivo futuro, Tipo Corte imputado retrospectivamente, estimados sin disponibilidad al origen y WebFlor sin vigencia certificada. Cierre semanal es un supuesto por validar. Para planos se usa el último anterior con disponibilidad supuesta posterior al cierre nominal y a AL1; se prueba una demora adicional. AL1 sirve para validar edad, no certifica publicación.

Una base estructuralmente correcta no implica cobertura completa de predictores ni un modelo ya validado. Consultar la guía y la metodología de la raíz.
