# La Gaitana · Plataforma de producción

Primer prototipo funcional, con fuentes reales del proyecto. Referencia: [especificación maestra](../docs/ESPECIFICACION.md).

## Revisar en Windows

Desde PowerShell, dentro de esta carpeta:

```powershell
.\instalar.cmd
.\iniciar.cmd
```

Abrir **http://localhost:5173**. Documentación de la API: **http://localhost:8000/docs**. Para detener sólo los procesos iniciados por el lanzador:

```powershell
.\detener.cmd
```

Requisitos: Python 3.14, Node 24 y acceso a los archivos locales del proyecto. El lanzador usa `npm.cmd` para evitar restricciones de PowerShell y no cambia su política global. Las dependencias se instalan en `.venv` de esta carpeta; el entorno de los notebooks no se modifica.

`instalar.cmd` crea `.env` sólo si no existe y conserva configuraciones previas. Los tokens generados quedan allí. No subir ese archivo, datasets, modelos entrenados ni `storage/` a Git.

## Qué funciona

- **Histórico:** panorama general real/modelo/ingeniero, WAPE y sesgo de ambos y semanas evaluadas explícitas. Se distingue entrenamiento, validación, prueba y seguimiento de publicaciones nuevas.
- **Comparador de errores:** selección visible de una semana, semanas sueltas, un rango, todas o las últimas 1/4/8 disponibles; año ISO, producto/color/variedad y navegación al detalle con regreso desde la ruta del cultivo. Recupera la exploración por niveles y descarga del antiguo benchmark, conservando los casos comparables del modelo 19. Incluye error absoluto, aportes, WAPE, sesgo, cantidades, búsqueda, paginación, ganador por grupo y descarga CSV de toda la tabla filtrada. La vista temporal permite alternar producción y diferencias netas en tallos; estas últimas no se confunden con el error absoluto del WAPE.
- **Pronóstico:** el usuario elige la semana H1; el calendario H1–H5 y los avisos de fuentes se recalculan respecto a ese lunes. El backend valida el origen solicitado y sólo genera si ya tiene variables admisibles procesadas; no mueve variables de otra semana ni completa una semana futura por suposición. Un origen pasado se identifica como simulación retrospectiva. Trabajos independientes, adaptador del 19, grupos H1–H2/H3–H5 y rutas teoría/Media4. No consulta al ingeniero para predecir.
- **Revisión:** producto por volumen → color → una o varias variedades, con rango libre de semanas, historia y controles independientes de real/modelo/revisión/teoría. La curva por edad utiliza los valores normalizados existentes; sólo la línea de proyección absoluta tiene suavizado visual, sin alterar cantidades. El checklist explícito distingue pendiente, sugerencia aceptada y revisión con ajustes; se guarda por propuesta en SQL y conserva el avance por producto/color. Cambiar cantidades vuelve a dejar pendientes las variedades afectadas. Seleccionar para comparar no equivale a confirmar revisión.
- **Ajustes:** cantidades o porcentajes, reparto proporcional con restos mayores, originales conservados, restauración y control de revisiones concurrentes.
- **Versiones:** borradores independientes; sólo publicar cambia la vigente por finca/origen. Auditoría y resultados persisten en la base configurada.
- **Archivos y ETL:** recepción persistente con progreso de envío, confirmación por archivo, selección múltiple de planos, estimados, estadísticas de familias distintas y cargas adicionales de clima/producción, con reintento de errores. La inspección inicial sólo consulta el índice y los encabezados XML del Excel, sin cargar celdas/cachés, y se ejecuta fuera del bucle HTTP. Guardar no activa datos: **Procesar archivos** solicita al trabajador las limpiezas de referencia, proyecciones y variables en una versión aislada; valida los resultados, guarda las fuentes limpias en SQL Server y activa la versión completa mediante una transacción. Véase [ETL y SQL](ETL_Y_SQL.md).
- **Excel:** descarga de valores originales/ajustados y trazabilidad en un formato preliminar claramente identificado.
- **Guía:** recorrido interactivo y explicación concreta del modelo, curvas, métricas y límites.
- **WebFlor:** botón de actualización por lectura del reporte real; archiva la descarga, audita el empalme y sustituye por versión el rango reciente hasta ayer, conservando el histórico anterior. La conexión de fuente es distinta de `Proyectos.EP`. Ver [reglas y evidencia de WebFlor](WEBFLOR.md).

## Límites visibles del prototipo

1. **La vigencia depende de los archivos efectivamente procesados.** Por defecto se ofrece el último origen de la base activa; el usuario puede elegir otro H1 y consultar lo que falta para esa semana. Las ediciones de planos y del ingeniero se comprueban por coincidencia del origen elegido, no sólo porque haya un archivo posterior. Una semana sin variables preparadas queda bloqueada hasta actualizar y procesar los insumos. Los derivados Parquet y los modelos se conservan en almacenamiento persistente; las fuentes normalizadas y la trazabilidad se guardan en SQL Server.
2. **Recibir y procesar son pasos distintos.** Una carga nueva queda `pendiente_etl` hasta ejecutar «Procesar archivos». Sólo una ejecución validada activa los nuevos datos; un fallo conserva la versión anterior. Una carga idéntica ya procesada se reconoce sin repetir el ETL. El clima desactualizado permite utilizar la variante validada `Sin_clima`; no se rellena arbitrariamente con ceros.
3. **SQL Server configurado y migrado en `Proyectos`, esquema `EP`.** SQLite se conserva para desarrollo y pruebas aisladas. La carga inicial de millones de registros puede tardar; su avance y resultado se consultan en el estado del ETL. No interpretar la existencia de tablas como confirmación de una carga terminada.
4. **La exportación no replica todavía las 16 tablas dinámicas del Excel original.** Hay que designar y validar una plantilla definitiva antes de declarar equivalencia de formato.
5. **Autenticación de prototipo:** modo local asigna perfil ingeniero; con `DEV_MODE=false` se exige token para administrador, ingeniero o consulta. La auditoría identifica ese perfil, todavía no personas con cuentas nominales. No equivale a un sistema de usuarios/SSO listo para Internet.
6. **Inferencia verificada por regresión parcial:** consultar `storage/verification_model19.json` después de ejecutar la comprobación descrita abajo. Sólo se certifican los orígenes realmente comparados; no se promete aún equivalencia de todos los cortes ni del escenario de emisión del jueves.
7. Sólo GAITANA tiene alcance inicial de pronóstico. No se despliegan los experimentos por producto/horizonte posteriores ni el modelo diario.

## Configurar SQL Server

Todas las tablas de la plataforma en SQL Server pertenecen al esquema **`EP`**, incluidas las tablas de cargas, pronósticos, auditoría y el registro `EP.lgf_alembic_version`. Las migraciones crean el esquema si no existe; la cuenta de despliegue necesita ese permiso o un administrador debe crearlo previamente. SQLite conserva su estructura local sin esquemas.

Editar `.env` local:

```dotenv
SQL_SERVER=servidor
SQL_DATABASE=proyectos
SQL_USER=usuario
SQL_PASSWORD=clave_local
SQL_DRIVER=ODBC Driver 18 for SQL Server
SQL_TRUST_CERTIFICATE=no
```

La fuente directa de corte utiliza las variables independientes `WEBFLOR_SERVER`, `WEBFLOR_DATABASE`, `WEBFLOR_USER`, `WEBFLOR_PASSWORD`, `WEBFLOR_DRIVER` y `WEBFLOR_TRUST_CERTIFICATE`, indicadas sin secretos en `.env.example`. El botón se habilita al terminar la carga inicial y cuando no hay trabajos en curso. Los pendientes de clima, planos y estimados no bloquean WebFlor; un completo de producción pendiente se debe procesar primero. La tabla de fuentes muestra hasta dónde están los datos, qué período se recomienda para H1 y desde dónde cargar los faltantes. Clima y estadísticas históricas no se exigen como una actualización semanal para la variante Sin clima.

Cuando `SQL_SERVER` tiene valor, se usa esa conexión y no SQLite. Se requiere el controlador ODBC instalado y permisos para crear los objetos propios `lgf_*` y su registro `lgf_alembic_version`. La migración no modifica tablas de las fuentes productivas ni reutiliza la tabla de migraciones de otra aplicación. Revisar permisos/esquema antes de aplicarla contra la base compartida.

Si se cambia de SQLite a SQL Server, las versiones locales no se transfieren solas. `backend/scripts/transfer_local_history.py` permite transferir los registros propios del prototipo de forma idempotente; conservar el respaldo local y comprobar conteos. No registrar cadenas de conexión ni contraseñas en logs.

## Ejecución manual y comprobaciones

Tres terminales, partiendo de esta carpeta:

```powershell
# API
cd backend
..\.venv\Scripts\python.exe -m alembic upgrade head
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```powershell
# Trabajador
cd backend
..\.venv\Scripts\python.exe -m app.worker
```

```powershell
# Interfaz
cd frontend
npm.cmd run dev
```

Desde `backend/`:

```powershell
..\.venv\Scripts\python.exe -m pytest -q
..\.venv\Scripts\python.exe -m scripts.verify_model19
```

La regresión reproduce un origen archivado y compara por serie/origen/objetivo/horizonte con tolerancia absoluta de una millonésima de tallo. No sobrescribe fuentes ni predicciones de notebooks; guarda modelos y reporte sólo en `storage/`. La caché de modelos incluye huella de datos, código del adaptador, variante y corte mensual, de modo que una modificación del adaptador invalida la caché anterior.

## Docker

Con Docker disponible y `.env` creado:

```powershell
docker compose up --build -d
docker compose logs -f api worker
docker compose down
```

Las entradas analíticas y los notebooks necesarios se montan en lectura; los archivos y resultados del prototipo usan un volumen persistente. `down` conserva ese volumen; no usar `down -v` si se deben conservar las versiones. Con SQL Server externo, sus datos persisten en la instancia, independientemente del contenedor.

La configuración Docker se entrega para probar: no se pudo construir en esta estación porque Docker no está disponible en el PATH. El funcionamiento local y las pruebas se registran en [ESTADO_PROTOTIPO.md](ESTADO_PROTOTIPO.md).

## Estructura

`frontend/`: React, estilos y gráficos. `backend/app/`: API, datos, adaptador del 19, ajustes, persistencia, recepción de archivos y trabajador. `backend/migrations/`: Alembic. `backend/tests/`: reglas críticas. `deploy/`: imágenes y proxy. `scripts/`: configuración y lanzadores. `storage/`: archivos privados, logs, modelos y base local, siempre fuera de Git.


### Carga de varios Excel

El selector admite varios archivos y permite agregarlos en selecciones sucesivas, quitar pendientes y reintentar sólo los errores. Todos deben corresponder al año indicado. Planos añade semanas faltantes; estimados conserva las ediciones nominales; estadísticas admite un completo por familia. Clima y producción admiten varios adicionales con fechas nuevas que no se crucen. El modo completo recibe un único archivo por fuente/año (y familia cuando corresponda), para evitar que dos reemplazos se anulen entre sí. Guardar los Excel sigue siendo distinto de procesar y activar el ETL.
