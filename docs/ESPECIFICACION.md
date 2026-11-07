# Plataforma de predicción y análisis de producción floral

La Gaitana Farms · Especificación maestra · 23 de octubre de 2026.

Estado: alcance solicitado y referencia permanente de implementación. La revisión inicial y la arquitectura propuesta están en [Fase 1](FASE_1_REVISION_Y_ARQUITECTURA.md). Este documento expresa requisitos; no significa que la aplicación ya esté implementada.

Actualización del 26 de octubre: existe un [prototipo funcional](../plataforma_gaitana/README.md), con [estado y comprobaciones](../plataforma_gaitana/ESTADO_PROTOTIPO.md). Se implementaron el ETL de fuentes originales y la conexión/migraciones de SQL Server `Proyectos`; todos los objetos propios usan el esquema **EP**. El cierre de la carga inicial y la inferencia sobre esa carga se registran en el estado del prototipo y en su evidencia operativa. La plantilla Excel definitiva y el despliegue Docker siguen pendientes de comprobación. No se considera terminada la plataforma empresarial completa.

## 1. Objetivo y referencia metodológica

Convertir el desarrollo analítico existente en una aplicación web empresarial para consultar, generar, analizar, ajustar y publicar pronósticos de producción floral. La herramienta debe ser comprensible para el ingeniero, atractiva, mantenible y específica para la operación floricultora.

Los notebooks existentes son la referencia técnica principal. Primero comprender y reproducir lo que funciona; después modularizarlo. Conservar limpieza, normalización, uniones, variables, reglas temporales y metodología del cuadernillo 19. Los estimados del ingeniero son una referencia de desempeño y no son predictores.

El WAPE aproximado de 19,59 % mencionado en la solicitud es una referencia inicial, no una constante de la aplicación. La fase 1 debe identificar la versión de datos, el panel y las métricas efectivamente disponibles antes de congelar el modelo. No atribuir a una versión las cifras de otra evaluación.

## 2. Arquitectura y desarrollo

Tecnologías propuestas por el usuario:

| Componente | Tecnología |
| --- | --- |
| Interfaz | React, TypeScript, Vite y componentes accesibles, preferiblemente shadcn/ui. |
| Gráficos | Plotly o Apache ECharts; elegir una biblioteca principal. |
| API | Python y FastAPI. |
| ETL y modelos | Python con las bibliotecas y transformaciones verificadas en los notebooks. |
| Persistencia | SQL Server, base existente `proyectos`, SQLAlchemy y controlador compatible. |
| Despliegue | Docker y Docker Compose. |
| Versionamiento | Git. |

Separar frontend, API, ETL, construcción de variables, entrenamiento/inferencia y persistencia. Usar una estructura modular y responsabilidades claras, sin abstracciones innecesarias. Los procesos pesados se ejecutarán fuera de las solicitudes HTTP y mostrarán estado y progreso.

Configuración mediante variables de entorno; `.env` fuera de Git y `.env.example` sin secretos. Dependencias con versiones fijadas, migraciones, logs, errores centralizados, validaciones, endpoints documentados y pruebas de procesos críticos. Documentar instalación, desarrollo, pruebas y despliegue. Verificar que los datos sobrevivan a la reconstrucción de contenedores.

## 3. Fuentes, cargas y almacenamiento

| Fuente | Actualización requerida |
| --- | --- |
| Clima | Archivo completo o nuevos registros. |
| Planos de siembra | Incorporación incremental de registros faltantes, conservando la edición del plano. |
| Producción real | Archivo completo o nuevos registros. |
| Estadísticas de producción | Archivo completo, con reemplazo lógico versionado. |
| Estimados semanales del ingeniero | Cargas periódicas con histórico para validación y comparación. |

El usuario selecciona la fuente y adjunta el archivo. El sistema valida estructura, columnas, tipos, fechas, duplicados, faltantes e inconsistencias y aplica el ETL de los notebooks. Presenta registros nuevos, actualizados, duplicados, rechazados y procesados, con razones consultables. Registra usuario, archivo, fecha, fuente y estado de ejecución.

Conservar los originales en almacenamiento persistente separado de SQL Server. Guardar en SQL datos limpios y normalizados, trazabilidad de cargas y resultados; evitar una tabla duplicada por cada archivo original. Registrar identificador, ubicación y huella del archivo para auditar y reprocesar.

Definir claves de negocio con evidencia de las fuentes. Una recarga idéntica no debe duplicar registros. No eliminar movimientos legítimos sólo porque coincidan sus cantidades y dimensiones. Las modalidades completas e incrementales deben ser explícitas; no asumir que un archivo completo autoriza borrar historia.

Usar transacciones y controles de integridad. Una carga fallida no debe sobrescribir datos validados. Las cargas completas de estadísticas se activan como una nueva versión sólo después de validarse; las anteriores permanecen identificables. Conservar la relación archivo → carga → datos normalizados → versión analítica → pronóstico.

## 4. Interfaz y módulos

Navegación consistente mediante barra institucional, menú lateral y área principal. Por ajuste solicitado el 26/10/2026, se separa el análisis detallado del resumen: cuatro módulos, **Histórico y desempeño**, **Comparador de errores**, **Generación y ajuste del pronóstico** y **Metodología y guía de uso**. El primero ofrece el panorama general; el comparador permite elegir una semana o un rango, filtrar producto/color/variedad y localizar el aporte de cada grupo al error del modelo y del ingeniero, manteniendo la misma población comparable y un horizonte por consulta.

### 4.1. Histórico y desempeño

Consultar producción histórica semanal y comparar real, estimado del ingeniero, sugerencia del modelo y versiones ajustadas/publicadas. Filtros por finca, producto, color, variedad, semana y periodo. Gráficos interactivos, tablas explorables, diferencias absolutas/porcentuales y cantidades en tallos.

Calcular WAPE global, por horizonte, finca y producto; sesgo firmado; diferencias en tallos y comparación ingeniero/modelo. Usar únicamente casos con real observado y emparejados por serie, origen y horizonte. No sumar indiscriminadamente una semana objetivo repetida en varios orígenes. Identificar periodo, población, versión del modelo y versión del pronóstico evaluado.

### 4.2. Estado y preparación de datos

Mostrar última semana completa de real disponible, cobertura climática, última edición de planos, estado de estadísticas, última estimación y siguiente origen pendiente. Estados por fuente: actualizada, incompleta, pendiente o con errores. Permitir cargar fuentes desde este espacio.

La validación previa diferencia fuentes obligatorias para la variante elegida de fuentes opcionales. Indicar exactamente qué debe corregirse cuando no se puede generar. Determinar el siguiente origen según el calendario y la disponibilidad real de insumos, no sólo según la fecha máxima de un archivo.

Selector **Utilizar información climática: Sí / No**. Ejecutar sólo variantes previamente entrenadas, verificadas y habilitadas para el ámbito solicitado. Mostrar nombre y versión del modelo. No rellenar clima con ceros ni activar variantes nuevas de forma automática.

### 4.3. Generación y análisis

Acción principal **Generar pronóstico**. Cada ejecución crea una simulación independiente; no publica ni sustituye el vigente.

Resumen con finca/producto, totales semanales, línea histórica y futura, variaciones, tabla con semanas en columnas, consolidación/desagregación y descarga. Identificar visualmente la frontera entre observado y pronosticado y mostrar suficiente historia para juzgar la trayectoria.

Detalle jerárquico **Finca → Producto → Color → Variedad**. Ordenar productos por producción estimada descendente; colores y variedades alfabéticamente. Actualizar gráficos, tablas e indicadores al cambiar la selección.

Permitir activar/desactivar real, modelo, pronóstico vigente ajustado, ingeniero, tendencia reciente y proyección teórica cuando existan. Comparar series de la misma escala y nivel de agregación. No convertir ausencia en cero para completar gráficas.

Al seleccionar variedad, mostrar su curva teórica normalizada en un gráfico complementario: edad/periodo del cultivo, rendimiento normalizado, etapas relevantes y comparación compatible con observaciones cuando aplique. Conservar la normalización de los notebooks. Diferenciar rendimiento por planta/edad, proyección absoluta del plano y pronóstico corregido en tallos.

Ficha contextual compacta: finca, producto, color, variedad, producción reciente, tendencia y desviación, sólo cuando estén disponibles y definidas.

### 4.4. Sesgo e incertidumbre

Mostrar comportamiento histórico del modelo seleccionado por H1–H5, con periodo y población de validación. Distinguir WAPE (magnitud agregada del error), sesgo firmado (sobre/subestimación neta) e incertidumbre (variabilidad esperada). No presentar WAPE como sesgo ni como banda de confianza. Incorporar bandas únicamente con un procedimiento validado; en caso contrario, mostrar las métricas disponibles sin inventar intervalos.

### 4.5. Ajustes del ingeniero

Permitir modificar cantidades semanales de una variedad o de un total finca/producto/color, mediante tallos o porcentaje. Conservar sugerencia original, valor ajustado y diferencia; impedir negativos y recalcular los totales. Registrar autor, fecha y observación opcional. Permitir deshacer/restaurar con trazabilidad.

Al ajustar un agregado, aplicar una redistribución explícita entre sus variedades y respetar los redondeos en tallos. Definir el caso de base cero antes de habilitar esa redistribución. Mantener coherencia de todas las sumas. Distinguir visualmente modelo y resultado ajustado.

### 4.6. Versiones, publicación y exportación

Cada generación conserva ID, usuario, fecha/hora, origen, versión del modelo, datos utilizados, configuración climática, valores originales, ajustes y estado. Una nueva ejecución para el mismo periodo crea una nueva versión.

Separar **generar**, **ajustar/guardar borrador** y **publicar**. Sólo publicar cambia la versión vigente del ámbito correspondiente. Conservar estados borrador, publicado y reemplazado y las versiones anteriores para auditoría y comparación. La publicación y el cambio del vigente deben ser atómicos.

Acción **Descargar estimado**: respetar exactamente la plantilla Excel del ingeniero —hojas, nombres, columnas, orden y estructura— una vez identificada la plantilla definitiva. Al publicar, conservar resultados y versión en SQL Server para consultas y evaluación futura.

### 4.7. Metodología y guía

Sección visual, breve y didáctica, con ejemplos reales, diagramas, tarjetas y elementos interactivos. Explicar objetivo, fuentes, flujo de procesamiento, modelo real del 19, horizontes, construcción/normalización de curvas, métricas, tendencias y limitaciones.

Tutorial: **Carga → Validación → Generación → Análisis → Ajuste → Publicación → Exportación**. Ilustraciones discretas alusivas al clavel; no sustituir la explicación metodológica por decoración.

## 5. Identidad visual y accesibilidad

- Principal `#800020`; secundario `#600018`; fondo `#f4f5f7`; superficies `#ffffff`.
- Roboto para texto y Raleway para títulos institucionales; logotipo corporativo cuando se proporcione o identifique el archivo autorizado.
- Espaciado consistente, bordes discretos, sombras suaves y jerarquía clara. Vinotinto como identidad, con colores legibles para distinguir las series de los gráficos.
- Diseño adaptable a escritorio, tableta y móvil; menú móvil desplegable; búsqueda, filtros y paginación.
- Estados de carga, error, vacío, éxito y permisos; progreso de tareas; confirmación de acciones destructivas.
- Navegación por teclado, foco visible, contraste accesible y leyendas que no dependan sólo del color.

## 6. Roles y seguridad

| Perfil | Capacidades |
| --- | --- |
| Administrador | Configuración, usuarios, cargas y versiones del sistema. |
| Ingeniero | Actualizar fuentes, generar, ajustar, publicar y exportar. |
| Consulta | Consultar historia, resultados y documentación. |

Verificar permisos desde el backend. Proteger credenciales, archivos, operaciones críticas y registro de acciones. No confiar en controles visuales para autorizar una operación.

## 7. Fases y criterios de aceptación

| Fase | Entrega | Comprobación necesaria |
| --- | --- | --- |
| 1. Revisión y arquitectura | Inventario de notebooks/fuentes/Excel/SQL, arquitectura, diseño conceptual y plan. | Separar evidencia de propuestas y pendientes; identificar referencia del 19. |
| 2. Infraestructura y ETL | Estructura del proyecto, Docker, API, SQL Server, migraciones y cargas. | ETL equivalente a notebooks, recargas sin duplicados y recuperación ante errores. |
| 3. Integración del modelo | Componentes reutilizables del 19, artefactos, versiones e inferencia. | Reproducir predicciones bajo las mismas condiciones, con comparación por registro, horizonte, WAPE y sesgo. |
| 4. Interfaz y análisis | Tres módulos conectados a la API y datos reales. | Filtros, gráficos, estados y cifras coherentes con SQL y el modelo. |
| 5. Publicación y validación | Ajustes, estados, publicación, exportación, pruebas y despliegue. | Coherencia de sumas, versiones, roles, Excel y persistencia tras reinicios. |

Primero identificar y preservar la referencia reproducible del 19; desarrollar mejoras estadísticas posteriormente y como versiones independientes. No cambiar parámetros ni transformaciones para facilitar la integración sin justificar y medir el efecto. La reproducción completa debe ocurrir antes de declarar equivalente el backend.

## 8. Reglas de trabajo

Implementar por fases y actualizar esta especificación con decisiones, comprobaciones y pendientes. Mantener separadas las propuestas de lo que efectivamente está funcionando.

No inventar columnas, estructuras fuente, IDs, fincas, resultados ni datos. Los nombres de entidades nuevas de la aplicación se documentan como diseño propuesto, nunca como objetos encontrados en las fuentes. Datos de ejemplo únicamente en prototipos y claramente identificados.

Probar ETL, predicción, persistencia y ajustes; mantener coherencia entre gráficos, tablas y exportaciones. No publicar fuentes ni datasets en Git. Conservar notebooks como evidencia y evitar lógica duplicada entre aplicación, ETL y modelo.

El pronóstico diario sigue como desarrollo preliminar; el primer producto operativo integra el semanal del 19. No ampliar silenciosamente su alcance validado a otras fincas ni reemplazarlo por los experimentos posteriores.
