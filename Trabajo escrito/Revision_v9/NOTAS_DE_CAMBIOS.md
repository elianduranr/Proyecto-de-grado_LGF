# Decisiones y cambios de evidencia de la revisión v9

- Base preservada: versión 8, 84 páginas. Copia inicial y SHA-256 en `Version_inicial` y `version_inicial_sha256.json`.
- No se reentrenó ni se afinó ningún modelo. Se conservaron las predicciones y la elección previa; el WAPE ampliado sigue siendo 19,27 % frente a 19,40 %, con ventaja en H1/H2 y sin superioridad general.
- Se eliminaron dimensiones históricas mezcladas con la extracción ampliada. La auditoría piloto actual contiene 543.368 filas, 523.336 con pareja única y 490.116 utilizables. Los conteos anteriores de 530.250/510.237/477.426 correspondían a la extracción previa, no a errores nuevos ni a una modificación del algoritmo. Entre cortes fechados en 2026: 46.085/46.157 parejas únicas (99,84 %).
- Se documenta el panel de la misma extracción de la evaluación: 648.030 casos, 216.127 con real y 148.435 con real/historia admisible. Los 46.528 casos con todas las edades representadas no son plantas, tallos ni uniones fallidas. La figura de edades se redibuja con eje inferior 15 %.
- Curva ilustrativa reconstruida al último plano de esa extracción (12/10/2026). Clima exploratorio conservado en su panel previo a julio de 2025 y redibujado para legibilidad, sin recalcular un resultado predictivo.
- Objetivos reformulados con el alcance efectivo, sin alterar el anteproyecto original. Se mantiene en el manuscrito la aspiración comercial y su equivalencia pendiente.
- Se sintetiza el EDA, se integran resultados/discusión y se separan los tres problemas diarios. Se elimina la tabla de evidencia interna del documento académico y se conserva su trazabilidad aquí.
- Hiperparámetros unificados, incluyendo pesos propios/general y diferencias de muestreo/variables de los experimentos recientes. No se atribuyen diferencias sólo a separar horizontes.
- Bibliografía en IEEE: se preservan las fuentes reales de evaluación temporal, fuga y operación; se verifican publicaciones originales de boosting y LSTM. Las referencias de código internas no se hacen pasar por bibliografía académica.
