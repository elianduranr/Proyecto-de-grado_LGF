from pathlib import Path

root = Path(__file__).resolve().parents[1]
summary = root / "resumen_modelos_pronostico.md"
diagnostic = root / "Datos_analiticos_proyecto/eda_origen_error/hallazgos_origen_error.md"
text = summary.read_text(encoding="utf-8")
text = text.replace(
    "# Modelos de pronóstico: revisión de correspondencias del 19 de octubre de 2026",
    "# Modelos de pronóstico: benchmark semanal actualizado al 22 de octubre de 2026",
    1,
)
start = text.index("## Semanales")
end = text.index("## Evaluación reciente:", start)
weekly = """## Semanales

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

"""
text = text[:start] + weekly + text[end:]
origin = text.index("## Origen del error")
text = text[:origin] + diagnostic.read_text(encoding="utf-8")
summary.write_text(text, encoding="utf-8")
print(f"Resumen actualizado desde el panel estricto de 16.325 casos: {summary}")
