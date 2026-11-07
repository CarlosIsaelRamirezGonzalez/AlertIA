# Instalación

## Requisitos

- **Python 3.9 a 3.12.** TensorFlow 2.16 no tiene versión para Python 3.13 o más nuevo.
- **Windows, macOS o Linux.** En Windows se muestran los nombres de las cámaras USB con `pywin32`; en los demás sistemas se listan por número.
- **MongoDB**, local o en MongoDB Atlas.
- **Una cuenta de Gmail con contraseña de aplicación**, para los correos de confirmación y de alerta.
- **Una clave de Google Maps JavaScript API** con la librería Places, para elegir la ubicación de una cámara.
- **Twilio**, opcional: el envío de SMS está desactivado en el código.

## Pasos

1. Crea el entorno e instala las dependencias:
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Copia `.env.example` a `flasky\.env` y llena los valores. `flasky.py` lo lee al arrancar.
3. Corre la app:
   ```powershell
   cd flasky
   flask run
   ```
4. Abre http://127.0.0.1:5000 y regístrate. Si te registras con el correo de `FLASKY_ADMIN`, entras como administrador y no necesitas confirmar tu cuenta.

## Variables de entorno

| Variable | Para qué | Obligatoria |
|---|---|---|
| `SECRET_KEY` | Firma la sesión y los tokens | Sí en producción |
| `MONGODB_URI` | Conexión a MongoDB | Sí, si no es local |
| `FLASK_CONFIG` | `development`, `testing` o `production`: cambia la base (`development_db`, etc.) | No |
| `MAIL_USERNAME`, `MAIL_PASSWORD` | Cuenta que envía los correos | Sí |
| `FLASKY_ADMIN` | Correo del administrador | Sí |
| `SUPPORT_EMAIL` | A dónde llegan los reportes de problemas | No |
| `GOOGLE_MAPS_API_KEY` | Mapa al agregar o editar una cámara | Sí para ese mapa |
| `ALERTAI_MODEL_PATH` | Ruta del modelo; por defecto `Artificial_Intelligence/Aria.keras` | No |
| `ALERTAI_BASE_URL` | Dirección pública de la app, para los enlaces de los correos | No |
| `TWILIO_FROM_NUMBER` | Número que envía los SMS (desactivado) | No |
| `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` | SMS (desactivado) | No |

Las variables `SECRET`, `STRING_CONNECTION` y `MONGODB_SETTINGS` del `commands.txt` anterior se siguen aceptando, pero conviene usar los nombres nuevos.

## Pruebas

```powershell
cd flasky
flask test
```

Por ahora prueban las reglas de detección (`tests/test_detection.py`). Esas pruebas no necesitan MongoDB ni TensorFlow.
