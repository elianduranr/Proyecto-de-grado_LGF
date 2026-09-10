# Extracción de estimados semanales por correo

Esta carpeta contiene únicamente la automatización local de Outlook Web mediante
Microsoft Edge y Selenium.

## Ejecución

1. Cierra libros Excel abiertos dentro de `Datos/Estimados semanales`.
2. Ejecuta `EJECUTAR_EXTRACCION_LOCAL.bat`.
3. Escribe uno o varios años separados por espacios.
4. No cierres Edge mientras se ejecutan las búsquedas.

Los Excel se guardan en `../Datos/Estimados semanales/<año>`.
El perfil autenticado y las capturas de auditoría permanecen dentro de esta carpeta.

La búsqueda contempla correos enviados por `produccionlgf@lagaitanacol.com`,
`rtorres@lagaitanacol.com` y `rcubides@lagaitanacol.com`.
