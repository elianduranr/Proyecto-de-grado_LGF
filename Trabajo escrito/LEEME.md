# Trabajo escrito actualizado

Desarrollo_del_documento.md es el texto editable; Estructura_actualizada_con_resultados.docx es su versión Word. Incluye contexto, curvas, calidad, EDA, clima y desplazamiento, modelos semanales, WAPE y sesgo frente al ingeniero, reparto diario, interpretación e inventario train/test. Las referencias E1–E18 ubican las evidencias.

Seguir la guía de la raíz para ejecutar las etapas afectadas. Después, revisar cifras y conclusiones y generar el Word desde la raíz:

```powershell
.\entorno_tesis\Scripts\python.exe "Trabajo escrito/actualizar_word.py"
```

El script convierte el Markdown y sus figuras; no recalcula modelos ni interpreta resultados nuevos. Las fuentes originales se conservan. Los resultados son retrospectivos y requieren validación empresarial y revisión bibliográfica.

La sección 5.6 y la evidencia E18 añaden el origen del error por producto, color y variedad, con concentración temporal y ejemplos de H1. Son diagnósticos del test ya observado, no cambios al modelo.
