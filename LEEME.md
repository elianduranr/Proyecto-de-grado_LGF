# Proyecto de grado 2

El flujo vigente es: fuentes originales → cinco limpiezas → bases limpias → base analítica → EDA/benchmark → features → primeros modelos.

Empieza por [GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md](GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md). Para el diseño del estudio, lee [METODOLOGIA.md](METODOLOGIA.md).

- Excel originales: `Datos/`, sin modificar.
- Limpiezas 01–05: `Notebooks/Limpieza data, Notebooks y Scripts/`.
- Complemento SQL: `Notebooks/Extracción SQL/02_webflor_complemento_necesario.ipynb`, local por defecto.
- Base, EDA, features y modelos: `Notebooks/Analisis/`, 06 → 07 → 08 → 09.
- Salidas oficiales: ocho Parquet en `Datos_analiticos_proyecto/`.

Se conserva la lógica de recuperación del ingeniero: archivo exacto o siguiente disponible del mismo año, con solicitud y procedencia separadas. La limpieza de producción conserva su imputación de Tipo Corte, marcada como retrospectiva. El benchmark hace unión estricta y recuperación 1:1 por variedad.

Los notebooks originales recuperados son referencia de esa lógica, no otra cadena de exportaciones para ejecutar. No se usan scripts auxiliares para ocultar las transformaciones.

Reejecutar reemplaza cada salida oficial. No hay versiones por corrida, backups automáticos ni exportaciones intermedias. El entorno es `entorno_tesis`. 09 compara modelos bajo supuestos temporales explícitos; no selecciona un ganador operativo ni consulta SQL. La hipótesis central es utilizar producción reciente para ajustar las semanas siguientes.
