# Contexto del proyecto Modelo 02

## Estado actual

El proyecto dispone de una **base analítica y tres benchmarks**; todavía no existe un modelo final de machine learning entrenado.

La producción teórica se reconstruye por segmento del Plano de Siembras:

`tallos_teoricos_cama = plantas_cama × flores_planta(variedad, edad)`

Luego se agrega por emisión, horizonte, producto, color y variedad. El estimado del ingeniero es un benchmark externo, no una entrada del experimento principal.

## Objetivo recomendado

`residuo_teorico = tallos_reales - tallos_teoricos`

Un futuro modelo de corrección se interpretará como:

`pronostico_corregido = tallos_teoricos + residuo_predicho`

## Horizontes provisionales

- H1: semana de emisión (`semanas_adelante=0`).
- H2: emisión + 1.
- H3: emisión + 2.
- H4: emisión + 3.
- H5: emisión + 4.

Está pendiente confirmar con tutor y empresa si la tesis requiere realmente semanas adelante 1–5.

## Clima

- **Seguro:** `*_lag1_seguro` a `*_lag4_seguro`, correspondientes a semanas completamente anteriores.
- **Condicionado:** `*_emision_condicionado`; solo usar si se confirma que la semana estaba completa al emitir.
- **Prohibido para entrenamiento:** `*_objetivo_prohibido`; sirve únicamente para análisis retrospectivo.

Las semanas ISO inválidas se excluyen de rezagos y quedan auditadas, sin alterar la fuente.

## Producción real

`estado_objetivo` distingue `real_observado`, `semana_futura` y `sin_registro_en_semana_cerrada`. Los faltantes nunca se convierten automáticamente en cero.

## Riesgos abiertos

- No hay fecha exacta de disponibilidad de las curvas; la regla anual es provisional y puede introducir fuga dentro del año.
- No hay timestamp confiable para versiones corregidas del ingeniero; su prioridad también es provisional.
- La disponibilidad del clima de emisión y de la producción anterior debe confirmarse operativamente.
- El nivel cama construye la teoría, pero real e ingeniero solo permiten evaluar después de agregar.
- Las relaciones climáticas son exploratorias; no demuestran causalidad.

## Validación temporal preparada

Se proponen cortes de origen móvil: 2023→2024, 2023–2024→2025 y 2023–2025→2026 como prueba final. No se utiliza división aleatoria ni se permite que una misma semana objetivo aparezca en ambos conjuntos.
