# Informe gerencial del benchmark H1

Abre `informe_gerencia_benchmark.html` con doble clic. Funciona sin conexión y no requiere ejecutar Python para consultarlo.

- Los filtros superiores afectan todas las pestañas. Permiten seleccionar varias fincas, productos, colores, variedades y semanas no consecutivas.
- Las pestañas por finca, producto, color y variedad incluyen un selector para consultar cruces más detallados.
- El error se calcula por registro semanal antes de resumir. Los excesos y faltantes no se compensan en WAPE y MAE.
- El filtro de uniones por variedad permite excluir las filas cuyo color prioriza el del estimado. Los dos colores originales no están disponibles en el Excel fuente.
- El control de semanas procede de la salida guardada del notebook. Es un control global, no por finca, y una fecha ausente puede ser festivo.
- `informe_gerencia_benchmark.xlsx` contiene las tablas del periodo completo. Para obtener una tabla con los filtros actuales, usa **Descargar tabla filtrada · CSV** dentro del HTML.
- Conserva HTML y Excel en la misma carpeta para que funcione el enlace de descarga del Excel. El HTML puede consultarse por sí solo.

Para actualizar el informe, vuelve a exportar `Notebooks/consolidado_benchmark.xlsx` y ejecuta únicamente la celda de la sección 6 de `03_benchmark_estimado_ingeniero.ipynb`. También puedes ejecutar desde la raíz del proyecto:

```powershell
.\entorno_tesis\Scripts\python.exe scripts/generar_informe_benchmark.py
```

La generación reemplaza los dos archivos del informe; no modifica el Excel fuente. Las métricas, supuestos y procedencia se describen en la pestaña **Metodología** y en la hoja del mismo nombre del Excel.

Validación de métricas, filtros, descargas y navegación con Edge instalado:

```powershell
.\entorno_tesis\Scripts\python.exe scripts/validar_informe_benchmark.py
```
