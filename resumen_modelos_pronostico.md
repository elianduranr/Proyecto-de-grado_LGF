
# Modelos de pronóstico: revisión con clima actualizado

Todos los modelos semanales aprendidos de esta tabla son variantes de HistGradientBoostingRegressor (árboles de decisión). La validación anterior a 2026 selecciona Boosting sin clima; no se cambia por el resultado de test.

La configuración semanal seleccionada no utiliza variables meteorológicas. El componente diario conserva temperatura, humedad y radiación en sus pesos; son etapas distintas.

## Semanales: mismos 15.838 casos principales de 2026

| Método | Casos | MAE (tallos) | WAPE | Sesgo |
| --- | ---: | ---: | ---: | ---: |
| Memoria larga antes de actualizar clima | 15.838 | 2.512,65 | 19,59 % | -3,54 % |
| Boosting con clima ampliado y lluvia | 15.838 | 2.496,43 | 19,46 % | -2,96 % |
| Boosting con clima básico actualizado | 15.838 | 2.510,25 | 19,57 % | -3,58 % |
| Clima ampliado + curva atribuida a GAITANA | 15.838 | 2.515,81 | 19,61 % | -2,76 % |
| Boosting sin clima | 15.838 | 2.496,17 | 19,46 % | -2,42 % |
| Ingeniero | 15.838 | 2.531,72 | 19,74 % | -9,75 % |

| Horizonte | Casos | WAPE anterior | WAPE actual | WAPE ingeniero | Ventaja actual vs. ingeniero (pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| H1 | 3.413 | 15,68 % | 15,66 % | 17,09 % | 1,43 |
| H2 | 3.289 | 17,56 % | 17,37 % | 19,28 % | 1,91 |
| H3 | 3.166 | 20,39 % | 20,39 % | 20,32 % | -0,07 |
| H4 | 3.045 | 22,14 % | 21,96 % | 20,91 % | -1,04 |
| H5 | 2.925 | 22,77 % | 22,50 % | 21,40 % | -1,10 |
| Conjunto | 15.838 | 19,59 % | 19,46 % | 19,74 % | 0,28 |

| Horizonte | Sesgo anterior | Sesgo actual | Sesgo ingeniero |
| --- | ---: | ---: | ---: |
| H1 | -1,71 % | -1,23 % | -7,56 % |
| H2 | -3,41 % | -2,40 % | -8,17 % |
| H3 | -3,89 % | -2,70 % | -9,46 % |
| H4 | -4,63 % | -3,27 % | -11,32 % |
| H5 | -4,23 % | -2,63 % | -12,63 % |
| Conjunto | -3,54 % | -2,42 % | -9,75 % |

Sesgo = 100 × suma(predicción − real) / suma(real). Positivo: sobreestimación; negativo: subestimación. Cero no implica poco error: errores opuestos pueden compensarse. WAPE y sesgo se calculan sobre los mismos casos por horizonte.

## H1 por separado

Mismos **3.413 casos**. H1 es la primera semana pronosticada desde el lunes de emisión.

| H1: método | WAPE | MAE (tallos) | Sesgo medio (tallos) | Sesgo (%) |
| --- | ---: | ---: | ---: | ---: |
| Anterior | 15,68 % | 1.980,53 | -216,37 | -1,71 % |
| Actual: boosting sin clima | 15,66 % | 1.978,16 | -155,84 | -1,23 % |
| Ingeniero | 17,09 % | 2.158,89 | -955,34 | -7,56 % |

Frente al ingeniero, el WAPE baja **1,43 puntos**, equivalente a **8,37 % menos error absoluto** en estos casos. El sesgo negativo indica subestimación; cuanto más cerca de cero, menor desvío del volumen total.

## Diarios: mismos días observados

(En revisión: desarrollo preliminar y siguientes pasos.)

| Método | Casos | MAE (tallos) | WAPE | Sesgo |
| --- | ---: | ---: | ---: | ---: |
| Diario autónomo antes de actualizar clima | 22.973 | 543,76 | 26,76 % | -7,23 % |
| Boosting reconciliado · selección semanal | 22.973 | 554,07 | 27,27 % | -5,91 % |
| Boosting diario autónomo | 22.973 | 542,84 | 26,72 % | -7,11 % |
| Boosting reconciliado · memoria actualizada | 22.973 | 557,45 | 27,44 % | -6,21 % |
| Perfil histórico · selección semanal | 22.973 | 562,66 | 27,69 % | -5,48 % |
| Perfil histórico · memoria actualizada | 22.973 | 565,88 | 27,85 % | -5,78 % |
| Diario reconciliado antes de actualizar clima | 22.973 | 557,78 | 27,45 % | -6,21 % |
| Uniforme · selección semanal | 22.973 | 584,97 | 28,79 % | -16,81 % |
| Uniforme · memoria actualizada | 22.973 | 589,48 | 29,01 % | -17,03 % |

El autónomo no está obligado a sumar al total semanal. Los repartos sí. SARIMA/SARIMAX se evalúan sólo en tres series y no se mezclan con esta población; consultar el piloto en diario 05. El EDA no demuestra una regla causal de retraso por clima. Para train/test del mismo ajuste consultar 19, diario 05 y el inventario 17.

## Qué mejoró

- Semanal conjunto: WAPE **19,59 % → 19,46 %**; ingeniero **19,74 %**. Sesgo **-3,54 % → -2,42 %**; ingeniero **-9,75 %**.
- El modelo supera al ingeniero en WAPE en **H1 y H2**; el ingeniero conserva menor WAPE en **H3–H5**. El modelo tiene menor sesgo absoluto en los cinco horizontes.
- Diario reconciliado: **27,45 % → 27,27 %**. Diario autónomo: **26,76 % → 26,72 %**. La mejora es pequeña y el autónomo sigue teniendo menor WAPE.
- La ventaja semanal conjunta frente al ingeniero es 0,28 puntos, con intervalo exploratorio de 95 % [-1,27; 1,72]. Incluye cero: el resultado retrospectivo es favorable, pero no demuestra superioridad estable.

La lluvia y las ventanas ampliadas mejoran frente al clima básico en el test. Sin clima y clima ampliado quedan prácticamente empatados (19,458 % y 19,460); se conserva el candidato elegido en la validación. Restringir las curvas a pilotos atribuibles a GAITANA pierde cobertura y empeora el WAPE respecto a la curva compartida con el mismo clima ampliado; se conserva la referencia compartida. Esto no prueba ausencia de efecto agronómico del clima.

## De dónde viene el error

[Notebook 20](Notebooks/Analisis/20_EDA_origen_error_modelo_ingeniero.ipynb): conserva las predicciones y descompone los mismos casos. «Error del modelo (%)» es su participación en el error absoluto; el aporte se expresa en puntos del WAPE total.

### H1: cuatro productos principales

| Producto | Volumen (%) | WAPE modelo | WAPE ingeniero | Error del modelo (%) | Aporte WAPE (pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION | 60,34 | 14,33 % | 14,53 % | 55,23 | 8,65 |
| CARNATION | 18,52 | 18,91 % | 20,17 % | 22,36 | 3,50 |
| SOLOMIO | 11,34 | 15,17 % | 18,77 % | 10,99 | 1,72 |
| RAFFINE | 6,04 | 15,96 % | 25,58 % | 6,15 | 0,96 |

### H1–H5: cuatro productos principales

| Producto | Volumen (%) | WAPE modelo | WAPE ingeniero | Error del modelo (%) | Aporte WAPE (pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| MINICARNATION | 60,78 | 17,67 % | 17,75 % | 55,19 | 10,74 |
| CARNATION | 18,31 | 23,40 % | 22,43 % | 22,02 | 4,28 |
| SOLOMIO | 11,22 | 18,20 % | 18,54 % | 10,49 | 2,04 |
| RAFFINE | 6,03 | 22,99 % | 29,36 % | 7,12 | 1,39 |

- **Concentración:** MINICARNATION y CARNATION suman 77,59 % del error H1 del modelo. MINICARNATION domina también el del ingeniero (51,31 %), principalmente por volumen.
- **De dónde ganamos:** RAFFINE y SOLOMIO explican aproximadamente 69,11 % de la ventaja neta H1. En MINICARNATION ganamos sólo 3/8 meses, pese a la pequeña ventaja acumulada. En H5, CARNATION aporta 0,67 puntos a nuestra desventaja.
- **Colores:** ORANGE, HOT PINK y LIGHT PINK de MINICARNATION concentran el mayor error H1 de ambos métodos. Se comparan dentro de producto, sin mezclar identidades.
- **Variedades:** UCHUVA es la de mayor error de ambos; le siguen LORENZO y ACADEMY en el modelo, LORENZO y NENUFAR en el ingeniero. La mayor desventaja del modelo es EPSILON: WAPE 15,17 % frente a 10,11 %.
- **Sesgo no es precisión:** ACADEMY tiene sesgo 0,19 %, pero WAPE 19,15 %. En H1, sobreestimaciones (7,21 pp) y subestimaciones (8,45 pp) se compensan en el sesgo, pero se suman en WAPE.
- **Explicación a revisar:** el modelo queda corto en subidas fuertes, pero 89,39 % de su error ocurre en casos sin cambios extremos respecto a media4. Variabilidad previa, seguimiento de picos y cobertura merecen revisión; no son causas demostradas. El notebook incluye semanas y trayectorias de UCHUVA, EPSILON y ACADEMY. No se modificaron modelos mirando este test.
