# Trabajo escrito actualizado

Desarrollo_del_documento.md es el texto editable; Estructura_actualizada_con_resultados.docx es su versión Word. Incluye contexto, curvas, calidad, EDA, clima y desplazamiento, modelos semanales, WAPE y sesgo frente al ingeniero, reparto diario, interpretación e inventario train/test. Las referencias E1–E18 ubican las evidencias.

Seguir la guía de la raíz para ejecutar las etapas afectadas. Después, revisar cifras y conclusiones y generar el Word desde la raíz:

```powershell
.\entorno_tesis\Scripts\python.exe "Trabajo escrito/actualizar_word.py"
```

El script convierte el Markdown y sus figuras; no recalcula modelos ni interpreta resultados nuevos. Las fuentes originales se conservan. Los resultados son retrospectivos y requieren validación empresarial y revisión bibliográfica.

La sección 5.6 y la evidencia E18 añaden el origen del error por producto, color y variedad, con concentración temporal y ejemplos de H1. Son diagnósticos del test ya observado, no cambios al modelo.

La revisión metodológica explica cómo se normalizan rendimientos, qué representa una cohorte, por qué se proponen rezagos y ventanas, qué recibe cada modelo y qué comparación sustenta una decisión. El anexo incluye el diccionario de las 47 columnas. El EDA 18 incorpora una comparación ejecutada entre clima original, diario y ampliado. Pronóstico diario y piloto SARIMA/SARIMAX se conservan con la marca «En revisión: desarrollo preliminar y siguientes pasos». La bitácora de la raíz registra la presentación prevista y los experimentos futuros.
