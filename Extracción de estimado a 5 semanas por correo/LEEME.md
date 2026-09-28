# Extracción de estimados semanales por correo

Esta carpeta contiene únicamente la automatización local de Outlook Web mediante
Microsoft Edge y Selenium.

Es una herramienta opcional para obtener los Excel originales. No forma parte de
la ejecución de limpieza, no se ejecuta automáticamente y no consulta SQL. Una
vez descargados los libros, el flujo oficial comienza en el notebook
`03_limpieza_estimados_semanales.ipynb` de la carpeta de limpieza. Ese notebook
recupera las semanas sin entrega mediante el siguiente archivo disponible y
guarda una única tabla limpia. Ver la guía de la raíz para el proceso completo.

## Ejecución

1. Cierra libros Excel abiertos dentro de `Datos/Estimados semanales`.
2. Ejecuta `EJECUTAR_EXTRACCION_LOCAL.bat`.
3. Escribe uno o varios años separados por espacios.
4. No cierres Edge mientras se ejecutan las búsquedas.

Los Excel se guardan en `../Datos/Estimados semanales/<año>`.
El perfil autenticado y las capturas de auditoría permanecen dentro de esta carpeta.

La búsqueda contempla correos enviados por `produccionlgf@lagaitanacol.com`,
`rtorres@lagaitanacol.com` y `rcubides@lagaitanacol.com`.
