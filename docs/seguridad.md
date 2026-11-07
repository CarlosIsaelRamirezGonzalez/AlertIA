# Seguridad

## Credenciales expuestas

Este repositorio es público, y hasta esta limpieza incluía `commands.txt` con valores reales de:

- la contraseña de la cuenta de Gmail que envía los correos;
- el *Account SID* y el *Auth Token* de Twilio;
- la cadena de conexión a MongoDB Atlas, con usuario y contraseña;
- el `SECRET_KEY` de Flask;
- la clave de Google Maps, que estaba en las plantillas.

El historial se limpió: los commits ya no tienen esas credenciales (se reemplazaron por `REDACTED`), ni los notebooks, ni los modelos viejos.

Aun así, **hay que cambiar o revocar todas esas credenciales**. Estuvieron públicas desde abril de 2024 y cualquiera pudo copiarlas.

Quien tenga una copia vieja del repositorio debe volver a clonarlo, porque el historial cambió.

## Cómo manejar secretos desde ahora

- Van solo en `flasky/.env`, que está en `.gitignore`.
- `.env.example` lista los nombres, sin valores.
- La clave de Google Maps conviene restringirla por dominio en Google Cloud, porque el navegador siempre la puede ver.
