# Entrega de la revisión del asesor · 4 de noviembre de 2026

La entrega académica es **`../Documento_LaGaitana_v9_revision_asesor_20261104_final.docx`**, con PDF y Markdown del mismo nombre. La versión 8 se conserva intacta, junto con una copia inicial en `Version_inicial/`. Los archivos v9 sin sufijo `_final` son borradores de comprobación anteriores; no son la entrega.

`REGISTRO_CUMPLIMIENTO.md` relaciona todas las indicaciones consolidadas del prompt con su implementación y ubicación. También se entrega en CSV y JSON. Los faltantes de información y decisiones del equipo están en `PENDIENTES_EQUIPO.md`; no forman un anexo del manuscrito.

## Fuentes y reproducción

- `contenido_academico.md`: prosa editable, objetivos, método, interpretación y conclusiones.
- `../revision_v9_config.py`: nombre único de la entrega.
- `../inspeccionar_revision_v9.py`: copia y huellas de la versión inicial.
- `../evidencia_revision_v9.py`: conteos, ejemplo real de curva y seis figuras desde datos/lógica.
- `../construir_revision_v9.py`: tablas y sustituciones verificadas; produce la fuente Markdown final y el registro de referencias.
- `../generar_documento_v9.py`: Word, marcadores, campos REF e índice.
- `../exportar_revision_v9_pdf.py`: Word oculto independiente, actualización de campos, exportación y paginado.
- `../verificar_revision_v9.py`: conservación de v8, cifras, cortes temporales, 47 columnas, texto, referencias y revisión de bordes/páginas del PDF. Genera mosaicos de todas las páginas para inspección visual.
- `../registrar_cumplimiento_v9.py`: registro de cumplimiento, pendientes y explicación de cambios de universos.

Desde la raíz del repositorio, con el entorno de tesis disponible:

```powershell
.\entorno_tesis\Scripts\python.exe "Trabajo escrito\ejecutar_revision_v9.py"
```

Cerrar previamente sólo la entrega v9 si se abrió para lectura. Se necesita Windows con Microsoft Word para actualizar campos y generar el PDF; los procesos ocultos se cierran al terminar. Las dependencias de la ejecución utilizada están fijadas en `requirements.txt`.

Se utilizan los archivos analíticos y las predicciones archivadas ya presentes, incluida la extracción privada `plataforma_gaitana/storage/datasets/evaluacion_local_20261028`. No se consulta SQL ni WebFlor, no se requiere VPN y no se reentrena, afina o publica ningún modelo. La fecha editorial de noviembre no significa que se hayan incorporado nuevos movimientos posteriores al corte de octubre.

## Comprobaciones

Consultar `verificacion_final.json`, `verificacion_paginado.json`, `verificacion_word.json`, `fuentes_sha256.json` y `Comprobacion_visual/`. Las dimensiones piloto nuevas sustituyen las de una extracción anterior que seguían mezcladas en v8; `NOTAS_DE_CAMBIOS.md` explica sus denominadores. El resultado predictivo principal se conserva: WAPE 19,27 % frente a 19,40 %, con ventaja en H1/H2 y sin afirmación de superioridad general.
