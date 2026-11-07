# Modelos de pronóstico: evaluación actualizada al 28 de octubre de 2026

Los modelos semanales aprendidos son variantes de HistGradientBoostingRegressor: árboles que corrigen una referencia usando información disponible al emitir. El ingeniero es el benchmark, no una entrada del modelo. La selección previa a 2026 es Boosting sin clima.

## Evaluación ampliada del 28/10/2026 · cuaderno 26

Se conserva **Boosting sin clima del cuaderno 19**: dos grupos H1–H2 y H3–H5; cada uno corrige Media4 o teoría según corresponda. Mismos parámetros, sin nuevo tuneo. Se reconstruyeron las fuentes hasta el corte del 27/10 y se evaluaron **43 semanas objetivo distintas**, desde 2025-12-29 hasta 2026-10-19. La semana en curso no se evalúa como completa.

**Año ISO 2026 completo, comparación nominal sobre los mismos casos:**

| Horizonte | Casos comunes | WAPE modelo | WAPE ingeniero | Sesgo modelo | Sesgo ingeniero |
| --- | ---: | ---: | ---: | ---: | ---: |
| H1 | 4230 | 15,04 % | 17,02 % | -0,94 % | -7,97 % |
| H2 | 4201 | 17,50 % | 19,02 % | -1,67 % | -8,06 % |
| H3 | 4075 | 20,22 % | 19,83 % | -3,15 % | -9,27 % |
| H4 | 3950 | 21,76 % | 20,36 % | -4,51 % | -11,29 % |
| H5 | 3827 | 22,16 % | 20,93 % | -4,03 % | -12,17 % |
| Conjunto | 20283 | 19,27 % | 19,40 % | -2,83 % | -9,70 % |

**Panel posterior a S36, comparación nominal sobre los mismos casos:**

| Horizonte | Casos comunes | WAPE modelo | WAPE ingeniero | Sesgo modelo | Sesgo ingeniero |
| --- | ---: | ---: | ---: | ---: | ---: |
| H1 | 606 | 12,10 % | 17,07 % | -0,21 % | -11,18 % |
| H2 | 701 | 16,83 % | 17,40 % | -1,75 % | -10,82 % |
| H3 | 699 | 19,35 % | 17,74 % | -5,64 % | -10,94 % |
| H4 | 697 | 19,93 % | 17,99 % | -6,66 % | -11,08 % |
| H5 | 696 | 21,49 % | 18,01 % | -8,91 % | -11,25 % |
| Conjunto | 3399 | 18,10 % | 17,66 % | -4,76 % | -11,05 % |

Sesgo firmado = predicción menos real, dividido por real total. El cuaderno también informa MAE, RMSE, MAPE sobre reales positivos, ±8 %, saldo neto en tallos, métricas train/test del mismo ajuste y contraste con el ajuste congelado al 03/08.

**Separación temporal:** cada ajuste sólo entrena con objetivos terminados antes de su corte mensual; la imputación y codificación se ajustan dentro de train. Una semana de prueba puede incorporarse a un ajuste posterior cuando ya terminó, sin haber sido conocida por el modelo que la pronosticó. No hay reparto aleatorio ni porcentaje global 80/20. Las fechas, casos y porcentajes de cada ajuste están en `particiones_por_corte.csv`.

Esta comprobación es **retrospectiva**: no equivale a publicaciones anticipadas ni vuelve a seleccionar el modelo. La validación 2025 y la referencia original de 2026 se conservan. La comparación con idéntico corte informativo del jueves sigue pendiente. El pronóstico diario conserva su evaluación anterior y sigue en revisión; no se reentrenó en esta actualización.

Archivos: `Notebooks/Analisis/26_validacion_temporal_actualizada_y_operacion.ipynb`, resultados en `Datos_analiticos_proyecto/validacion_temporal_20261028/` e informe `Trabajo escrito/Documento_LaGaitana_v8_validacion_temporal_actualizada_20261028.docx` (también PDF).


## Referencia histórica conservada · evaluación original hasta S36

Selección previa a 2026: **HistGradientBoosting sin clima**, que corrige una referencia con variables conocidas al origen. El ingeniero es sólo benchmark. El cruce actualizado aplica el nombre del archivo para definir H1 y reúne 16.325 parejas estrictas.

| Método | Casos | MAE (tallos) | WAPE | Sesgo (%) |
| --- | ---: | ---: | ---: | ---: |
| Boosting sin clima | 16.325 | 2.487,57 | 19,36 % | -2,36 % |
| Boosting con clima básico | 16.325 | 2.499,92 | 19,45 % | -3,57 % |
| Boosting con clima ampliado y lluvia | 16.325 | 2.478,91 | 19,29 % | -2,98 % |
| Boosting con clima ampliado y curva atribuida a GAITANA | 16.325 | 2.495,57 | 19,42 % | -2,73 % |
| Ingeniero | 16.325 | 2.533,69 | 19,71 % | -9,81 % |

| Horizonte | Casos | WAPE modelo | WAPE ingeniero | Sesgo modelo | Sesgo ingeniero |
| --- | ---: | ---: | ---: | ---: | ---: |
| H1 | 3.512 | 15,53 % | 16,93 % | -1,34 % | -7,54 % |
| H2 | 3.388 | 17,49 % | 19,16 % | -2,01 % | -7,97 % |
| H3 | 3.264 | 20,33 % | 20,26 % | -2,46 % | -9,38 % |
| H4 | 3.141 | 21,78 % | 20,97 % | -3,18 % | -11,52 % |
| H5 | 3.020 | 22,20 % | 21,60 % | -2,97 % | -13,09 % |
| Conjunto | 16.325 | 19,36 % | 19,71 % | -2,36 % | -9,81 % |

Sesgo = 100 × suma(predicción − real) / suma(real): negativo significa subestimación. El modelo supera al ingeniero en H1 y H2; el ingeniero tiene menor WAPE en H3–H5. En el conjunto, el modelo queda 0,36 puntos por debajo. Los valores son retrospectivos.

## H1 por separado

WAPE modelo **15,53 %**, ingeniero **16,93 %**. Sesgo modelo **-1,34 %**, ingeniero **-7,54 %**. Mismos 3.512 casos. El modelo mejora el WAPE en 1,41 puntos y también subestima menos en términos netos.

## Evaluación reciente: modelos por horizonte (cuadernos 21–25)

Esta es una evaluación distinta de la tabla anual anterior: compara 1.226 pronósticos recientes de GAITANA (tres semanas objetivo) contra el ingeniero, en los mismos casos. Es una prueba retrospectiva exploratoria, no una validación prospectiva.

| Horizonte | Modelo seleccionado en el experimento | WAPE modelo / ingeniero | Sesgo modelo / ingeniero | Resultado |
| --- | --- | ---: | ---: | --- |
| **H1** | **Boosting agrupado H1–H2** | **12,28 % / 15,23 %** | **+2,75 % / −7,79 %** | **Modelo mejor en WAPE por 2,95 puntos** |
| **H2** | **Boosting separado H2** | **14,96 % / 14,98 %** | **−0,02 % / −5,80 %** | **Empate práctico en WAPE; modelo con menor sesgo** |
| H3 | Especialista por producto + modelo general | 17,27 % / 16,51 % | −5,85 % / −7,99 % | Ingeniero mejor en WAPE |
| H4 | Especialista por producto + modelo general | 18,89 % / 16,79 % | −3,96 % / −7,67 % | Ingeniero mejor en WAPE |
| H5 | Especialista por producto + modelo general | 19,76 % / 16,95 % | −7,76 % / −7,86 % | Ingeniero mejor en WAPE |
| Total comparable | Combinación seleccionada del experimento | 17,53 % / 16,34 % | −4,22 % / −7,51 % | Ingeniero mejor en WAPE por 1,19 puntos |

**Lectura:** la ventaja clara de esta evaluación está en H1; H2 queda prácticamente empatado en WAPE, aunque el sesgo del modelo es menor. Un sesgo positivo indica sobreestimación y uno negativo subestimación. La especialización explorada en el cuaderno 25 bajó el WAPE global del candidato previo de 17,80 % a 17,53 %, pero todavía no supera al ingeniero en el total ni en H3–H5. Los modelos se entrenan con variables disponibles al origen; el pronóstico del ingeniero se usa únicamente como referencia de comparación.

## Diarios

(En revisión: desarrollo preliminar y siguientes pasos.)

| Método | Casos | MAE (tallos) | WAPE | Sesgo (%) |
| --- | --- | --- | --- | --- |
| Autónomo: referencia histórica anterior al clima | 22.973 | 543,76 | 26,76 % | -7,23 % |
| Boosting diario reconciliado con selección semanal | 22.973 | 553,80 | 27,26 % | -6,03 % |
| Boosting diario autónomo | 22.973 | 542,84 | 26,72 % | -7,11 % |
| Boosting reconciliado con memoria semanal | 22.973 | 556,82 | 27,41 % | -6,27 % |
| Perfil histórico con selección semanal | 22.973 | 562,31 | 27,68 % | -5,60 % |
| Perfil histórico con memoria semanal | 22.973 | 565,17 | 27,82 % | -5,85 % |
| Reconciliado: referencia histórica anterior al clima | 22.973 | 557,78 | 27,45 % | -6,21 % |
| Uniforme con selección semanal | 22.973 | 585,22 | 28,80 % | -16,92 % |
| Uniforme con memoria semanal | 22.973 | 589,21 | 29,00 % | -17,09 % |

Reconciliado: 27,27 % antes → 27,26 % ahora. Autónomo: 26,72 %. SARIMA/SARIMAX se comparan sólo en su piloto de tres series, no con este panel completo.

## Cuándo se aplica directamente la curva

La producción real permanece en la base analítica. La curva teórica se usa como referencia directa cuando representa las edades de todas las cohortes del plano; si no, el modelo puede apoyarse en la producción reciente cuando hay historia suficiente. Por eso, el indicador de cobertura describe en qué casos aplica directamente la curva, no cuánta producción o cuántos registros existen.

## Entrenamiento y test

No hay división aleatoria. Se entrena con semanas objetivo terminadas antes del corte, se selecciona en noviembre–diciembre de 2025 y se evalúa 2026 con reentrenamiento mensual. El inventario 17 y las hojas Ultimo_ajuste de 19 y Train_test_ultimo_ajuste de diario 05 permiten comparar train y test del mismo ajuste. Son resultados retrospectivos.

# Origen del error semanal: diagnóstico de 20

Mismos casos estrictos de 19. Aportes en puntos del WAPE total; sesgo positivo significa sobreestimar. Los grupos se ordenan por su aporte, no sólo por WAPE local.

## H1: productos

| Producto | Casos | WAPE modelo | WAPE ingeniero | Aporte modelo (pp) | Aporte ingeniero (pp) | Sesgo modelo | Sesgo ingeniero |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION | 1008 | 14,19 % | 14,36 % | 8,58 | 8,68 | -1,89 % | -6,79 % |
| CARNATION | 1295 | 18,82 % | 20,04 % | 3,48 | 3,70 | -1,24 % | -7,86 % |
| SOLOMIO | 408 | 14,88 % | 18,64 % | 1,68 | 2,10 | 0,23 % | -9,50 % |
| RAFFINE | 209 | 16,08 % | 25,55 % | 0,97 | 1,54 | -1,02 % | -9,86 % |
| STAR | 36 | 16,64 % | 18,75 % | 0,17 | 0,19 | -0,51 % | -16,50 % |
| BARBATUS | 170 | 25,30 % | 28,92 % | 0,15 | 0,17 | 3,88 % | -0,95 % |
| TRACHELIUM | 35 | 34,67 % | 41,45 % | 0,10 | 0,12 | -4,27 % | -24,17 % |
| VERONICA | 68 | 22,37 % | 26,75 % | 0,09 | 0,11 | 1,68 % | -8,87 % |
| GREEN BALL | 34 | 13,48 % | 16,09 % | 0,08 | 0,10 | 2,66 % | -1,91 % |
| VERONICA SPRAY | 68 | 22,76 % | 23,67 % | 0,09 | 0,09 | 3,21 % | -3,94 % |
| STATICE | 110 | 27,23 % | 29,79 % | 0,07 | 0,08 | 0,57 % | -2,78 % |
| AMAZON | 34 | 29,13 % | 22,27 % | 0,05 | 0,04 | 6,79 % | 0,53 % |
| ACHILLEA | 37 | 380,92 % | 99,26 % | 0,01 | 0,00 | 350,26 % | -89,63 % |

Modelo: los tres mayores aportes (MINICARNATION, CARNATION, SOLOMIO) concentran 88,47 % de su error absoluto.

Ingeniero: los tres mayores aportes (MINICARNATION, CARNATION, SOLOMIO) concentran 85,55 % de su error absoluto.

### Color: mayores aportes del modelo

| Grupo | Casos | WAPE modelo | WAPE ingeniero | Aporte modelo (pp) | Exceso frente al ingeniero (pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION / HOT PINK | 68 | 14,76 % | 14,90 % | 1,07 | -0,01 |
| MINICARNATION / ORANGE | 78 | 17,24 % | 18,42 % | 1,07 | -0,07 |
| MINICARNATION / LIGHT PINK | 102 | 16,17 % | 15,20 % | 1,02 | 0,06 |
| MINICARNATION / WHITE | 102 | 14,82 % | 16,28 % | 0,78 | -0,08 |
| MINICARNATION / RED | 68 | 12,96 % | 13,08 % | 0,78 | -0,01 |

### Variedad: mayores aportes del modelo

| Grupo | Casos | WAPE modelo | WAPE ingeniero | Aporte modelo (pp) | Exceso frente al ingeniero (pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION / ORANGE / UCHUVA | 34 | 17,86 % | 17,16 % | 0,93 | 0,04 |
| MINICARNATION / HOT PINK / LORENZO | 34 | 16,28 % | 16,16 % | 0,67 | 0,00 |
| MINICARNATION / LIGHT PINK / ACADEMY | 34 | 18,74 % | 17,05 % | 0,61 | 0,06 |
| MINICARNATION / YELLOW / CAESAR | 34 | 13,57 % | 14,20 % | 0,50 | -0,02 |
| MINICARNATION / LAVENDER / NENUFAR | 34 | 13,23 % | 14,76 % | 0,49 | -0,06 |
## H1–H5: productos

| Producto | Casos | WAPE modelo | WAPE ingeniero | Aporte modelo (pp) | Aporte ingeniero (pp) | Sesgo modelo | Sesgo ingeniero |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION | 4710 | 17,49 % | 17,66 % | 10,63 | 10,73 | -4,37 % | -9,07 % |
| CARNATION | 6007 | 23,34 % | 22,63 % | 4,29 | 4,16 | -1,04 % | -9,37 % |
| SOLOMIO | 1920 | 18,13 % | 18,40 % | 2,03 | 2,06 | 2,43 % | -11,71 % |
| RAFFINE | 975 | 23,27 % | 29,50 % | 1,41 | 1,78 | -0,23 % | -14,41 % |
| STAR | 163 | 18,26 % | 20,43 % | 0,18 | 0,20 | 1,97 % | -19,13 % |
| BARBATUS | 800 | 33,58 % | 28,31 % | 0,20 | 0,17 | 8,54 % | -2,70 % |
| TRACHELIUM | 155 | 43,23 % | 48,20 % | 0,13 | 0,14 | -3,59 % | -30,25 % |
| VERONICA | 320 | 28,33 % | 34,82 % | 0,12 | 0,14 | 3,95 % | -19,08 % |
| GREEN BALL | 160 | 18,86 % | 18,52 % | 0,11 | 0,11 | 9,91 % | 2,67 % |
| VERONICA SPRAY | 320 | 30,36 % | 26,66 % | 0,12 | 0,10 | 6,25 % | -8,27 % |
| STATICE | 480 | 34,52 % | 35,78 % | 0,08 | 0,09 | 7,80 % | -5,54 % |
| AMAZON | 160 | 32,85 % | 22,04 % | 0,06 | 0,04 | 13,50 % | 0,44 % |
| ACHILLEA | 155 | 821,83 % | 99,81 % | 0,02 | 0,00 | 806,45 % | -97,36 % |

Modelo: los tres mayores aportes (MINICARNATION, CARNATION, SOLOMIO) concentran 87,52 % de su error absoluto.

Ingeniero: los tres mayores aportes (MINICARNATION, CARNATION, SOLOMIO) concentran 85,94 % de su error absoluto.

### Color: mayores aportes del modelo

| Grupo | Casos | WAPE modelo | WAPE ingeniero | Aporte modelo (pp) | Exceso frente al ingeniero (pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION / HOT PINK | 320 | 18,73 % | 16,12 % | 1,36 | 0,19 |
| MINICARNATION / LIGHT PINK | 480 | 21,59 % | 20,27 % | 1,35 | 0,08 |
| MINICARNATION / ORANGE | 360 | 17,41 % | 21,78 % | 1,08 | -0,27 |
| MINICARNATION / WHITE | 480 | 20,05 % | 20,94 % | 1,06 | -0,05 |
| MINICARNATION / RED | 320 | 17,61 % | 14,30 % | 1,04 | 0,20 |

### Variedad: mayores aportes del modelo

| Grupo | Casos | WAPE modelo | WAPE ingeniero | Aporte modelo (pp) | Exceso frente al ingeniero (pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION / ORANGE / UCHUVA | 160 | 17,78 % | 20,41 % | 0,94 | -0,14 |
| MINICARNATION / HOT PINK / LORENZO | 160 | 19,64 % | 16,10 % | 0,81 | 0,15 |
| MINICARNATION / LIGHT PINK / ACADEMY | 160 | 21,81 % | 19,82 % | 0,70 | 0,06 |
| MINICARNATION / YELLOW / CAESAR | 160 | 18,14 % | 19,94 % | 0,69 | -0,07 |
| MINICARNATION / PURPLE / EPSILON | 160 | 19,95 % | 11,94 % | 0,66 | 0,27 |

## Cómo interpretar

Los diagnósticos de ruta, variabilidad y cambio ex post son asociaciones, no causas. Las tablas dentro de producto ayudan a distinguir composición, pero no eliminan confusión. Los cambios ex post usan producción futura conocida sólo al evaluar. La selección de grupos críticos se hace mirando test: cualquier ajuste posterior debe validarse en otro periodo. No se modifica el modelo con este EDA.
