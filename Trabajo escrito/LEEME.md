# Trabajo escrito actualizado

Desarrollo_del_documento.md es el texto editable; Estructura_documento_v4_oct192026.docx es la versión Word regenerada después de corregir las correspondencias cama–estadística y actualizar resultados semanales. Las referencias E1–E19 ubican las evidencias.

Seguir la guía de la raíz para ejecutar las etapas afectadas. Después, actualizar los resultados desde los archivos ejecutados y generar el Word desde la raíz:

```powershell
.\entorno_tesis\Scripts\python.exe "Trabajo escrito/actualizar_word.py"
```

Antes de construir el Word, actualizar el informe y sus resúmenes derivados:

```powershell
.\entorno_tesis\Scripts\python.exe "Trabajo escrito/actualizar_resultados.py"
```

El script convierte el Markdown y sus figuras; no recalcula modelos ni interpreta resultados nuevos. Las fuentes originales se conservan. Los resultados son retrospectivos y requieren validación empresarial y revisión bibliográfica.

La sección 5.6 y la evidencia E18 añaden el origen del error por producto, color y variedad, con concentración temporal y ejemplos de H1. Son diagnósticos del test ya observado, no cambios al modelo.

La sección 5.1.1 presenta aparte los cuadernos 21–25: ventaja clara del candidato en H1 en la evaluación reciente, empate práctico en H2 y ventaja global todavía del ingeniero. No se mezclan estos resultados con la evaluación anual.

La revisión metodológica explica cómo se normalizan rendimientos, qué representa una cohorte, por qué se proponen rezagos y ventanas, qué recibe cada modelo y qué comparación sustenta una decisión. El anexo incluye el diccionario de las 47 columnas. El EDA 18 incorpora una comparación ejecutada entre clima original, diario y ampliado. Pronóstico diario y piloto SARIMA/SARIMAX se conservan con la marca «En revisión: desarrollo preliminar y siguientes pasos». La bitácora de la raíz registra la presentación prevista y los experimentos futuros.
