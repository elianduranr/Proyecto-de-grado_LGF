# Proyecciones y calidad: recorrido vigente

Seguir la guía paso a paso del proyecto. Orden con los resultados existentes:

1. `00_catalogo_variedades.ipynb`: catálogo compartido en `Extracción SQL/Datos/01_maestros_y_geografia/Catalogo_analitico`.
2. `Auditoria_calidad_curvas.ipynb`: recupera información verificable, conserva fuentes y cantidades y expone faltantes, soporte y antes/después.
3. `Proyecciones_teoricas_todos_los_anios.ipynb`: listas explícitas de variedades/edades sin curva, comparación de planos y salida para el modelo.

Con fuentes Excel nuevas: catálogo → todos los años con recálculo → auditoría → todos los años con recuperación. El lector desde Excel ya contiene las reglas corregidas. No hace falta reconstruir Excel para estudiar las tablas actuales.

`Proyecciones_teoricas.ipynb` conserva la explicación y resultados de la construcción original, identificados como referencia anterior. No es una segunda implementación vigente. Los originales y respaldos del usuario se conservan.

La auditoría usa identidad comercial, no un ID SQL arbitrario, y no fusiona colores distintos ni ciclos. Las diferencias de obtentor requieren revisión agronómica. Tener historia no garantiza cobertura de todas las edades; los faltantes no se convierten en cero.
