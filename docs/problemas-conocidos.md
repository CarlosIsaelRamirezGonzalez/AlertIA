# Problemas conocidos

## Pendientes

1. **El monitoreo solo corre mientras el servidor está prendido y alguien abrió `/home`.** No hay un proceso o servicio independiente que vigile las cámaras.
2. **`Notification.user` guarda el correo como texto** en vez de una referencia al usuario. Si un usuario cambia de correo, pierde sus notificaciones. Corregirlo requiere migrar los datos que ya hay en MongoDB.
3. **Dependencias viejas:** Flask 1.1, Werkzeug 1.0 y Jinja2 2.11 ya no reciben parches de seguridad. Actualizarlas requiere probar la app completa.
4. **Las cámaras USB con nombre de Windows no abren directo:** OpenCV abre las cámaras por número, así que una cámara registrada por su identificador de Windows usa la cámara 0.
5. **La regla de "Encañonamiento" casi nunca se alcanza:** la clase 5 también cuenta para "Armas de fuego", que se revisa antes con el mismo umbral.
6. **El modelo no se ha vuelto a entrenar:** el código original se perdió, y `train.py` es una reconstrucción que no se ha probado con datos.

## Corregidos

| # | Problema | Corrección |
|---|---|---|
| 1 | Los números de clase no coincidían con el modelo: la app trataba la 11 como normal, la 7 como incendio y la 9 como persona herida | `app/detection.py` usa el orden real: 9 = Normalidad, 8 = Incendio, 11 = Persona herida, y Golpe (7) cuenta como pelea. Tiene pruebas en `tests/` |
| 2 | Las rutas de notificaciones no pedían sesión ni revisaban de quién eran | Todas piden sesión y solo ven o tocan las del usuario |
| 3 | Editar y borrar cámaras no revisaba el dueño, y borrar funcionaba con un enlace | Se revisa el dueño; borrar exige POST con token CSRF |
| 4 | Con POST, `/alert/notifications` creaba una notificación de prueba | Se quitó |
| 5 | El correo de "cámara desconectada" tronaba (`datetime.now` sin paréntesis) | Corregido |
| 6 | `/admin/delete/<id>` no podía funcionar | Acepta POST con token y usa MongoEngine |
| 7 | Reportar una notificación fallaba: se asignaba un texto a una referencia | Se guarda el usuario; la cámara se busca solo entre las suyas |
| 8 | `/auth/confirm/<token>/<email>` daba error 500 con un código inválido | Regresa a la pantalla del código |
| 9 | Error de dedo `reverse_delte_rule` en `Report.camera` | Corregido |
| 10 | El límite de 100 destacadas contaba las de todos y no impedía destacar | Es por usuario y sí lo impide |
| 11 | El modelo recibía colores BGR y la foto del correo salía con colores invertidos | Se convierte a RGB |
| 12 | El modelo se cargaba en cada visita a `/home` y cada visita abría otro hilo | Se carga una vez; el hilo de avisos se inicia una vez; una cámara caída se vuelve a vigilar |
| 13 | Solo funcionaba en Windows | `pywin32` se usa solo en Windows; en otros sistemas las cámaras se listan con OpenCV |
| 14 | Las webcams siempre abrían la cámara 0 | Se usa la cámara elegida si es un número |
| 15 | El enlace del correo apuntaba a `127.0.0.1:5000` | Sale de `ALERTAI_BASE_URL` |
| 16 | No había pruebas | `flasky/tests/test_detection.py`; `flask test` acepta correr sin argumentos |
| 17 | Recuperar contraseña con un correo no registrado tronaba | Responde igual que con uno registrado, para no revelar qué correos existen |
| 18 | La validación de URL repetida buscaba un campo `ip` que no existe | Revisa `url` |
| 19 | Fechas guardadas como texto y mostradas sin formato | Se guardan como fecha y se muestran como `07-11-2026 15:21` |
| 20 | Notebooks, `commands.txt` con credenciales, ruta del modelo y clave de Maps fijas, modelo duplicado | Scripts, `.env.example` y variables de entorno; historial limpio |
| 21 | Sin `SECRET_KEY`, la app usaba la clave fija "Hard to guess", con la que cualquiera podría falsificar sesiones | Fuera de desarrollo, la app no arranca si falta `SECRET_KEY`; en desarrollo usa una clave local. Tiene pruebas en `tests/test_config.py` |
| 22 | Las pruebas solo se corrían a mano | GitHub Actions las corre en cada push y cada PR |
