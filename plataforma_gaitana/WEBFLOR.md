# Actualización de producción desde WebFlor

WebFlor es una **fuente de lectura**. El destino de la aplicación continúa siendo SQL Server **Proyectos**, esquema **EP**. Las dos conexiones se configuran por separado en el `.env` privado; el ejemplo versionado no contiene credenciales.

## Fuente comprobada

`WF_Gaitana.Reporte.InformeCorteInvVariedad` es un procedimiento con dos parámetros de tipo fecha: `@FechaInicial` y `@FechaFinal`. Su definición consulta `Siembra.CorteInvVariedadView` y limita la fecha inicial a los últimos **45 días**. Por ello hay que conservar las descargas en almacenamiento persistente; no se puede depender de volver a pedir años anteriores al reporte.

Se consultan únicamente días anteriores a la fecha actual del servidor. Se conservan el reporte original en Parquet, la ventana solicitada, la hora de recepción, la comparación de empalme y el Excel de detalle compatible con la limpieza 05. No se ejecuta SQL de escritura en WebFlor ni se importa código desde la fuente.

## Botón «Actualizar desde WebFlor»

1. Parte de la última base activada. Las cargas pendientes de clima, planos o estimados no bloquean la consulta; si WebFlor trae cambios, se procesan junto con ellas. Un archivo completo de producción pendiente sí debe procesarse primero, para no combinar dos reemplazos incompatibles.
2. Descarga los días cerrados disponibles y valida las columnas reales, fechas y cantidades enteras. Conserva ajustes firmados y movimientos repetidos legítimos.
3. Normaliza nombres y archiva las diferencias del período común por finca, día, producto, color y variedad. Compara también los movimientos, su multiplicidad y campos de detalle. Una corrección dentro de la ventana es un motivo para actualizar, no para bloquear el proceso.
4. Sustituye el rango reciente completo, desde la fecha actual del servidor menos 45 días hasta ayer, en una nueva versión. Conserva todo lo anterior al rango. Los movimientos retirados del reporte desaparecen del rango nuevo; los repetidos legítimos se conservan. La ventana más reciente tiene precedencia antes de la limpieza 05. No se modifica un archivo original ni una versión activa.
5. Ejecuta la limpieza 05, base analítica y variables diarias; reutiliza las proyecciones y fuentes independientes que no cambiaron. Verifica conservación de tallos, claves y conteos antes de activar.
6. Deja la base lista para generar una propuesta. **Actualizar no genera ni publica automáticamente un pronóstico.** La publicación continúa siendo otra acción.

Si no cambió ningún movimiento, termina como «sin cambios», aunque se hayan reconsultado ayer y anteayer. Una corrección sí ejecuta el ETL aunque no haya fechas nuevas. Un reporte vacío o que omita una finca presente en el rango guardado no activa el reemplazo. La ausencia de registros de un domingo no se presenta como un cero certificado; se distingue el último día con movimientos del final de la ventana consultada.

## Empalme comprobado el 26 de octubre

La consulta del 11 de septiembre al 25 de octubre devolvió 142.159 registros, con último corte el 24 de octubre. Tras normalizar los nombres, las **4.318 combinaciones** comparables entre el 11 de septiembre y el 10 de octubre coinciden en tallos: diferencia absoluta y neta **0**. Las diferencias aparentes de variedades con «Ñ» desaparecen con la normalización canónica.

La descarga identifica **43.863 registros posteriores al 10 de octubre**: 33.472 y 2.927.823 tallos de GAITANA; 10.391 y 826.656 tallos de ARABELLA. Estos son conteos del reporte consultado, no una afirmación de que ya esté activado: el estado del trabajo y `storage/verification_operational.json` confirman el resultado de la integración completa.

## SQL incremental y versiones

Antes de añadir sólo los registros nuevos a una fuente SQL, se comprueba que las filas históricas del Parquet siguen siendo idénticas, incluidas sus trazas. Si la prueba pasa, se reutilizan los registros existentes y se añaden los nuevos. Cada versión guarda su límite de filas en `EP.lgf_dataset_sources`; las vistas vigentes aplican ese límite. Las versiones anteriores conservan su alcance aunque el almacenamiento compartido reciba más cortes.

Si cambió alguna fila histórica, se conserva el mecanismo de una nueva versión completa. No se supone que dos archivos con el mismo total sean idénticos, ni se deduplican cortes usando sólo sus cantidades.

## Avisos relativos a H1

La interfaz identifica las cinco semanas objetivo y, por fuente, muestra qué está procesado, sus archivos más recientes y qué cargar después. Los planos se comparan con la semana de H1; el clima, con la semana previa. Las estadísticas históricas continúan siendo utilizables y su actualización es una recomendación. Los estimados del ingeniero son opcionales y sólo sirven para evaluar desempeño.

Por defecto se ofrece el último origen preparado, la semana siguiente a la última semana de producción procesada; el usuario puede elegir otra H1 y los avisos se recalculan respecto a esa semana. Una base atrasada se identifica como tal; no se cambian las etiquetas de los horizontes para aparentar un pronóstico más reciente. La emisión operativa del jueves conserva el pendiente de validación indicado en el estado del prototipo.


## Reconsulta semanal y verificación del 28/10/2026

El procedimiento aplica `CAST(GETDATE()-45 AS date)` al límite inferior: el borde se define por día completo, no por hora. Se consulta hasta ayer para excluir el día en curso. Las correcciones recibidas más tarde se recogen en la siguiente actualización. Una revisión semanal solapa las ventanas; el límite de retención de WebFlor **no elimina la base histórica persistida**. Sólo es necesario recuperar un tramo por Excel si una interrupción supera la retención y quedan fechas sin guardar.

La comprobación de sólo lectura del 13/09 al 27/10 devolvió 141.004 registros de Gaitana y Arabella, con movimientos el 26 y 27/10. La ventana vigente tenía 134.213 registros. Esta comprobación no activa datos ni declara terminado un ETL. Evidencia: `storage/verification_webflor_refresh_source.json`; descarga archivada en `storage/webflor_checks/2026-10-28/`.

Las ventanas y su precedencia se guardan en el catálogo y manifiesto de ejecución. Reconstruir desde los archivos aplica las mismas reglas, por lo que no reaparecen cortes de una descarga sustituida. El adaptador del notebook 05 filtra las filas sustituidas antes de la limpieza canónica; no cambia la normalización ni deduplica movimientos. La conservación de tallos se verifica después sobre la base consolidada.

Si una corrección cambia filas históricas, se carga una nueva versión SQL completa y sólo se activa al terminar. Esto puede tardar más que una actualización estrictamente incremental; la versión anterior sigue disponible. Las pruebas cubren cambios sin fechas nuevas, retiros de movimientos, repeticiones legítimas, la ejecución real del notebook 05 y la conservación de la versión SQL anterior.

Comandos de diagnóstico de sólo lectura, desde backend: `python -m scripts.inspect_webflor_contract` y `python -m scripts.check_webflor_refresh`.
