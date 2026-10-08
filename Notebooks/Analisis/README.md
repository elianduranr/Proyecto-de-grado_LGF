# Análisis vigente

Consultar la [guía única](../../GUIA_PASO_A_PASO_DATOS_Y_MODELOS.md) para las dependencias y el orden exacto de ejecución.

- 10–13: base analítica, EDA, ajuste inicial y benchmark del ingeniero.
- 14–15: tendencias diarias, memoria y referencias de calidad. El contraste histórico de calidad incluye ahora también la actualización climática; no aísla ambos efectos.
- 18: cobertura climática, lluvia y EDA de error/desplazamiento; compara explícitamente las 26 entradas climáticas originales, diarias y ampliadas. Requiere las señales de diario 01 antes de ejecutarse.
- 19: comparación controlada sin clima/con clima y curvas atribuibles a GAITANA; selección anterior a 2026, WAPE y sesgo por H1–H5.
- 16: importancia por permutación del candidato de 19; requiere ejecutar 19 primero.
- 17: inventario train/test de referencias y componentes de entrenamiento para diario 05.

(Pronóstico diario en revisión: desarrollo preliminar y siguientes pasos.) El reparto diario está en Modelo_de_series_diario/05. Cada notebook contiene su código y lee archivos explícitos, sin depender de variables de otro kernel.

20_EDA_origen_error_modelo_ingeniero.ipynb cierra el recorrido: descomposición del error por producto, color y variedad, H1 separado y cada horizonte, semanas críticas y foco en tres variedades. Requiere salidas vigentes de 10 y 19; no reentrena.
