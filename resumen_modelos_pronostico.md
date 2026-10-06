# Comparación de modelos de pronóstico

## 1. Modelos semanales

Los modelos semanales usan principalmente **HistGradientBoostingRegressor**, un algoritmo de *machine learning* basado en árboles de decisión.

| Modelo semanal | WAPE | ¿En qué se basa? |
|---|---:|---|
| Boosting con tendencias diarias | 20,06 % | Usa producción histórica, clima y tendencias de corte diario para ajustar el pronóstico semanal. |
| Boosting separado por horizonte | 19,68 % | Entrena modelos distintos para horizontes cercanos (**H1–H2**) y más lejanos (**H3–H5**). |
| **Boosting separado + memoria larga** | **19,59 %** | Añade hasta **12 semanas de historia**, cambios de tendencia y variabilidad reciente. Es el mejor modelo semanal evaluado. |
| Boosting + memoria larga + revisiones | 19,65 % | Incluye además cómo han cambiado las proyecciones teóricas anteriores para una misma semana objetivo. |
| Combinación con referencia histórica | 19,65 % | Combina el modelo de boosting con una referencia histórica simple. La validación terminó utilizando prácticamente solo el modelo. |
| Ingeniero | 19,74 % | Pronóstico humano utilizado como referencia de comparación. |

**Evaluación:** mismos **15.838 casos de 2026**.  
**Métrica:** WAPE; menor valor significa menor error.

---

## 2. Modelos diarios

| Modelo diario | Total semanal utilizado | WAPE |
|---|---|---:|
| **Boosting autónomo** | No depende del pronóstico semanal | **26,76 %** |
| Boosting reconciliado | Boosting semanal con memoria larga | **27,45 %** |
| Perfil histórico de 8 semanas | Boosting semanal con memoria larga | 27,87 % |
| Boosting reconciliado anterior | Sistema semanal anterior | 28,29 % |
| Perfil histórico anterior | Sistema semanal anterior | 28,65 % |
| Reparto uniforme | Boosting semanal con memoria larga | 29,03 % |
| Reparto uniforme anterior | Sistema semanal anterior | 29,89 % |

**Evaluación:** mismos **22.973 días observados de 2026**.

---

## 3. Resumen

- **Mejor modelo semanal:** **Boosting separado + memoria larga**, con **19,59 % WAPE**.
- Frente al pronóstico del ingeniero (**19,74 %**), la mejora global es pequeña, pero el modelo tiene mejor desempeño conjunto.
- **Mejor modelo diario:** **Boosting autónomo**, con **26,76 % WAPE**.
- Si se necesita que la suma de los pronósticos diarios coincida exactamente con el pronóstico semanal, la mejor opción es el **Boosting reconciliado**, con **27,45 % WAPE**.
- **SARIMA y SARIMAX** se evaluaron únicamente sobre tres series, por lo que no se incluyen en la comparación general diaria.


---

## 4. Desempeño del mejor modelo semanal por horizonte

Para el **Boosting separado + memoria larga**, los resultados de evaluación son:

| Horizonte | WAPE modelo | WAPE ingeniero | Diferencia a nuestro favor |
|---|---:|---:|---|
| **H1** | **15,68 %** | 17,09 % | ✅ **1,41 puntos mejor** |
| **H2** | **17,56 %** | 19,28 % | ✅ **1,73 puntos mejor** |
| H3 | 20,39 % | **20,32 %** | 0,07 puntos peor |
| H4 | 22,14 % | **20,91 %** | 1,23 puntos peor |
| H5 | 22,77 % | **21,40 %** | 1,37 puntos peor |
| **Conjunto** | **19,59 %** | 19,74 % | ✅ **0,15 puntos mejor** |

**Lectura principal:** el modelo mejora claramente al ingeniero en **H1–H2**, prácticamente empata en **H3** y sigue por detrás en **H4–H5**. La ventaja conjunta observada es pequeña, por lo que todavía debe confirmarse con un periodo nuevo de evaluación.
