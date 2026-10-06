# Trabajo escrito actualizado

`Desarrollo_del_documento.md` es el texto editable. `Estructura_actualizada_con_resultados.docx` es su versión Word. El documento incluye contexto, curvas, calidad, EDA, modelos semanales, comparación diaria con memoria larga, interpretación por permutación e inventario train/test. Las referencias E1–E13 ubican la evidencia en los notebooks.

La guía de la raíz contiene el orden exacto de corrida. Primero ejecutar las etapas afectadas, luego revisar cifras y redacción, y finalmente regenerar el Word desde la raíz:

```powershell
.\entorno_tesis\Scripts\python.exe "Trabajo escrito/actualizar_word.py"
```

El script no recalcula modelos ni interpreta resultados nuevos. Las figuras están en `Figuras_resultados`. Los documentos originales se conservan. El borrador requiere revisión bibliográfica y validación empresarial; las métricas actuales son retrospectivas.
