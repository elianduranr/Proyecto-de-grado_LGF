# Modelos de pronóstico: revisión de correspondencias del 19 de octubre de 2026

Los modelos semanales aprendidos son variantes de HistGradientBoostingRegressor: árboles que corrigen una referencia usando información disponible al emitir. El ingeniero es el benchmark, no una entrada del modelo. La selección previa a 2026 es Boosting sin clima.

## Semanales

| Método | Casos | MAE (tallos) | WAPE | Sesgo (%) |
| --- | --- | --- | --- | --- |
| Referencia histórica anterior al clima actualizado | 15.838 | 2.512,65 | 19,59 % | -3,54 % |
| Boosting con clima ampliado y lluvia | 15.838 | 2.477,56 | 19,31 % | -3,19 % |
| Boosting con clima básico | 15.838 | 2.496,69 | 19,46 % | -3,80 % |
| Boosting con clima ampliado y curva atribuida a GAITANA | 15.838 | 2.493,94 | 19,44 % | -2,94 % |
| Boosting sin clima | 15.838 | 2.479,61 | 19,33 % | -2,59 % |
| Ingeniero | 15.838 | 2.531,72 | 19,74 % | -9,75 % |

| Horizonte | Casos | WAPE antes del 19/10 | WAPE actual | WAPE ingeniero | Sesgo actual | Sesgo ingeniero |
| --- | --- | --- | --- | --- | --- | --- |
| H1 | 3.413 | 15,66 % | 15,66 % | 17,09 % | -1,34 % | -7,56 % |
| H2 | 3.289 | 17,37 % | 17,36 % | 19,28 % | -2,48 % | -8,17 % |
| H3 | 3.166 | 20,39 % | 20,23 % | 20,32 % | -2,84 % | -9,46 % |
| H4 | 3.045 | 21,96 % | 21,73 % | 20,91 % | -3,49 % | -11,32 % |
| H5 | 2.925 | 22,50 % | 22,22 % | 21,40 % | -2,92 % | -12,63 % |
| Conjunto | 15.838 | 19,46 % | 19,33 % | 19,74 % | -2,59 % | -9,75 % |

Sesgo = 100 × suma(predicción − real) / suma(real). Positivo indica sobreestimación; negativo, subestimación. Errores opuestos se compensan en el sesgo, pero se suman en el WAPE. Se informan ambos sobre los mismos casos.

## H1 por separado

WAPE modelo **15,66 %**, ingeniero **17,09 %**. Sesgo modelo **-1,34 %**, ingeniero **-7,56 %**. Mismos 3.413 casos.

El WAPE conjunto pasa de 19,46 % a 19,33 % tras la revisión de cruces. Corregir la integración no garantiza mejorar todas las métricas: se informan los resultados obtenidos.

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

## Origen del error

Mismos casos estrictos de 19. Aportes en puntos del WAPE total; sesgo positivo significa sobreestimar. Los grupos se ordenan por su aporte, no sólo por WAPE local.

## H1: productos

| Producto | Casos | WAPE modelo | WAPE ingeniero | Aporte modelo (pp) | Aporte ingeniero (pp) | Sesgo modelo | Sesgo ingeniero |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION | 979 | 14,33 % | 14,53 % | 8,64 | 8,77 | -1,92 % | -6,86 % |
| CARNATION | 1258 | 18,90 % | 20,17 % | 3,50 | 3,74 | -1,30 % | -7,85 % |
| SOLOMIO | 396 | 15,14 % | 18,77 % | 1,72 | 2,13 | 0,24 % | -9,63 % |
| RAFFINE | 203 | 16,16 % | 25,58 % | 0,98 | 1,54 | -0,70 % | -9,41 % |
| STAR | 35 | 16,74 % | 19,10 % | 0,17 | 0,19 | -0,83 % | -17,00 % |
| BARBATUS | 165 | 25,46 % | 29,20 % | 0,15 | 0,17 | 4,07 % | -0,75 % |
| TRACHELIUM | 33 | 35,19 % | 41,93 % | 0,10 | 0,12 | -2,73 % | -24,17 % |
| VERONICA | 66 | 22,18 % | 26,54 % | 0,09 | 0,11 | 2,87 % | -7,91 % |
| GREEN BALL | 33 | 13,93 % | 16,10 % | 0,08 | 0,10 | 2,82 % | -1,39 % |
| VERONICA SPRAY | 66 | 23,02 % | 23,72 % | 0,09 | 0,09 | 3,82 % | -3,33 % |
| STATICE | 109 | 27,55 % | 29,79 % | 0,08 | 0,08 | 0,82 % | -2,23 % |
| AMAZON | 33 | 28,99 % | 22,66 % | 0,05 | 0,04 | 6,11 % | 0,39 % |
| ACHILLEA | 37 | 380,92 % | 99,26 % | 0,01 | 0,00 | 350,26 % | -89,63 % |

Modelo: los tres mayores aportes (MINICARNATION, CARNATION, SOLOMIO) concentran 88,49 % de su error absoluto.

Ingeniero: los tres mayores aportes (MINICARNATION, CARNATION, SOLOMIO) concentran 85,63 % de su error absoluto.

### Color: mayores aportes del modelo

| Grupo | Casos | WAPE modelo | WAPE ingeniero | Aporte modelo (pp) | Exceso frente al ingeniero (pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION / ORANGE | 76 | 17,69 % | 18,69 % | 1,09 | -0,06 |
| MINICARNATION / HOT PINK | 66 | 14,92 % | 14,87 % | 1,08 | 0,00 |
| MINICARNATION / LIGHT PINK | 99 | 16,26 % | 14,92 % | 1,02 | 0,08 |
| MINICARNATION / RED | 66 | 13,20 % | 13,31 % | 0,79 | -0,01 |
| MINICARNATION / WHITE | 99 | 14,54 % | 16,76 % | 0,76 | -0,12 |

### Variedad: mayores aportes del modelo

| Grupo | Casos | WAPE modelo | WAPE ingeniero | Aporte modelo (pp) | Exceso frente al ingeniero (pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION / ORANGE / UCHUVA | 33 | 18,40 % | 17,50 % | 0,96 | 0,05 |
| MINICARNATION / HOT PINK / LORENZO | 33 | 16,33 % | 16,11 % | 0,67 | 0,01 |
| MINICARNATION / LIGHT PINK / ACADEMY | 33 | 19,15 % | 16,36 % | 0,63 | 0,09 |
| MINICARNATION / YELLOW / CAESAR | 33 | 13,65 % | 14,58 % | 0,51 | -0,03 |
| MINICARNATION / LAVENDER / NENUFAR | 33 | 13,45 % | 15,00 % | 0,50 | -0,06 |
## H1–H5: productos

| Producto | Casos | WAPE modelo | WAPE ingeniero | Aporte modelo (pp) | Aporte ingeniero (pp) | Sesgo modelo | Sesgo ingeniero |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION | 4567 | 17,42 % | 17,75 % | 10,59 | 10,79 | -4,81 % | -9,13 % |
| CARNATION | 5825 | 23,39 % | 22,43 % | 4,28 | 4,11 | -0,80 % | -8,86 % |
| SOLOMIO | 1860 | 18,14 % | 18,54 % | 2,04 | 2,08 | 2,16 % | -12,02 % |
| RAFFINE | 945 | 23,42 % | 29,36 % | 1,41 | 1,77 | 0,20 % | -13,77 % |
| STAR | 158 | 18,23 % | 20,75 % | 0,18 | 0,20 | 1,52 % | -19,51 % |
| BARBATUS | 775 | 33,76 % | 28,54 % | 0,20 | 0,17 | 8,83 % | -2,38 % |
| TRACHELIUM | 148 | 41,96 % | 47,36 % | 0,12 | 0,14 | -4,75 % | -32,12 % |
| VERONICA | 310 | 28,16 % | 34,39 % | 0,11 | 0,14 | 5,67 % | -17,88 % |
| GREEN BALL | 155 | 19,12 % | 18,54 % | 0,11 | 0,11 | 9,95 % | 3,06 % |
| VERONICA SPRAY | 310 | 30,28 % | 26,16 % | 0,11 | 0,10 | 7,99 % | -6,93 % |
| STATICE | 475 | 35,03 % | 36,07 % | 0,09 | 0,09 | 8,11 % | -5,17 % |
| AMAZON | 155 | 32,66 % | 22,16 % | 0,06 | 0,04 | 12,81 % | 0,40 % |
| ACHILLEA | 155 | 821,83 % | 99,81 % | 0,02 | 0,00 | 806,45 % | -97,36 % |

Modelo: los tres mayores aportes (MINICARNATION, CARNATION, SOLOMIO) concentran 87,48 % de su error absoluto.

Ingeniero: los tres mayores aportes (MINICARNATION, CARNATION, SOLOMIO) concentran 86,02 % de su error absoluto.

### Color: mayores aportes del modelo

| Grupo | Casos | WAPE modelo | WAPE ingeniero | Aporte modelo (pp) | Exceso frente al ingeniero (pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION / HOT PINK | 310 | 18,80 % | 16,26 % | 1,37 | 0,19 |
| MINICARNATION / LIGHT PINK | 465 | 21,12 % | 20,14 % | 1,32 | 0,06 |
| MINICARNATION / ORANGE | 350 | 17,62 % | 21,76 % | 1,09 | -0,26 |
| MINICARNATION / RED | 310 | 17,70 % | 14,37 % | 1,05 | 0,20 |
| MINICARNATION / WHITE | 465 | 19,38 % | 21,26 % | 1,02 | -0,10 |

### Variedad: mayores aportes del modelo

| Grupo | Casos | WAPE modelo | WAPE ingeniero | Aporte modelo (pp) | Exceso frente al ingeniero (pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION / ORANGE / UCHUVA | 155 | 17,98 % | 20,43 % | 0,95 | -0,13 |
| MINICARNATION / HOT PINK / LORENZO | 155 | 19,94 % | 16,24 % | 0,83 | 0,15 |
| MINICARNATION / LIGHT PINK / ACADEMY | 155 | 21,54 % | 19,38 % | 0,70 | 0,07 |
| MINICARNATION / YELLOW / CAESAR | 155 | 18,19 % | 19,70 % | 0,69 | -0,06 |
| MINICARNATION / PURPLE / EPSILON | 155 | 20,02 % | 12,02 % | 0,67 | 0,27 |

## Cómo interpretar

Los diagnósticos de ruta, variabilidad y cambio ex post son asociaciones, no causas. Las tablas dentro de producto ayudan a distinguir composición, pero no eliminan confusión. Los cambios ex post usan producción futura conocida sólo al evaluar. La selección de grupos críticos se hace mirando test: cualquier ajuste posterior debe validarse en otro periodo. No se modifica el modelo con este EDA.
