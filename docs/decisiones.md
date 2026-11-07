# Por qué cada modelo y cada tecnología

El equipo original no dejó escritas sus razones. Lo que sigue está reconstruido a partir del código, del archivo del modelo y del historial. Donde algo se deduce y no se sabe con certeza, se dice.

## Modelo de inteligencia artificial: una CNN propia

**Qué es:** una red neuronal convolucional (CNN) entrenada desde cero, con 10 capas convolucionales, normalización por lotes, *dropout* y una salida de 12 clases. Pesa 8 MB. El detalle está en [inteligencia-artificial.md](inteligencia-artificial.md).

**Por qué una CNN:** la tarea es decir qué hay en una imagen fija: un arma, fuego, un choque. Las CNN son el estándar para clasificar imágenes, porque aprenden por sí solas los bordes, las texturas y las formas, sin que alguien tenga que describirlos.

**Por qué cada pieza:**

| Pieza | Para qué sirve |
|---|---|
| Entrada de 256 × 256 | Suficiente detalle para distinguir un arma en la mano, sin que cada cuadro de video tarde demasiado |
| Filtros de 2×2 | Pocos parámetros por capa; el modelo cabe en 8 MB y corre en una computadora normal sin GPU |
| `BatchNormalization` tras cada convolución | Hace el entrenamiento más estable y rápido |
| `Dropout` de 0.2 | Evita que memorice las fotos del dataset; importa porque las clases se parecen (golpe, patada, forcejeo) |
| `MaxPooling` | Reduce la imagen paso a paso para que la red vea el conjunto y no solo detalles |
| Capa densa de 32 | Junta lo aprendido antes de decidir; es pequeña para no sobreajustar |
| Salida *softmax* con 12 clases | Da una probabilidad por clase; la app usa la más alta como certeza |
| Adam y `sparse_categorical_crossentropy` | El optimizador estándar y la pérdida para clases numeradas, como las arma Keras desde carpetas |

**Por qué no un modelo preentrenado:** en una versión anterior, `home/views.py` importaba el preprocesamiento de MobileNetV2, así que parece que se consideró. Quizá se descartó porque una red propia daba más control, o para el proyecto escolar. **Recomendación:** si se vuelve a entrenar, conviene probar *transfer learning* con MobileNetV2 o EfficientNet. Con pocos datos por clase suele dar más exactitud, y también corre en tiempo real.

**Por qué detectar sobre cuadros y no sobre video:** clasificar imagen por imagen es más simple y ligero. La desventaja es que una sola imagen se confunde fácil. Por eso la app no avisa a la primera, sino cuando junta varias detecciones (siguiente sección).

## Reglas de detección (`app/detection.py`)

- **95 % de certeza mínima:** el historial muestra que se fue subiendo de 70 a 85 y luego a 95 %, para bajar las falsas alarmas.
- **Varias detecciones antes de avisar:** un solo cuadro mal clasificado no dispara una alerta.
- **Umbral distinto por amenaza:**
  - las armas, con 10, piden menos detecciones porque son las más urgentes;
  - los choques, las peleas y las personas heridas, con 30, piden más porque se confunden con escenas normales.
- **20 segundos para olvidar:** si la amenaza no se repite en ese tiempo, se olvidan las detecciones anteriores.
- **3 minutos sin repetir la misma amenaza:** evita llenar el correo con avisos de un mismo evento.

## Modelos de datos (MongoDB)

| Documento | Por qué existe |
|---|---|
| `User` | La cuenta. La contraseña se guarda cifrada con Werkzeug y el correo debe confirmarse, para no avisar a direcciones falsas |
| `Camera` | Cada cámara tiene sus alertas y su lugar. Las alertas se eligen por lugar porque no se vigila lo mismo en una casa que en la calle. Se guarda la computadora donde se registró porque la cámara física está conectada ahí |
| `Notification` | El historial de amenazas con su foto, para revisar después qué pasó. Las destacadas no se borran solas; las demás tienen un tope de 500 por usuario |
| `Report` | El usuario marca una alerta como error. Sirve al administrador para saber dónde se equivoca el modelo y conseguir imágenes para reentrenarlo. Tiene un tope de 25 |

## Modelos Pydantic (`app/schemas.py`)

El código no usa diccionarios para datos internos: cada estructura es un modelo Pydantic. Así queda claro qué campos tiene cada cosa, y los errores de forma salen al crearla y no después.

| Modelo | Reemplaza |
|---|---|
| `EmailAttachment` | Los adjuntos de los correos |
| `CameraDevice` | La lista de cámaras conectadas al registrar una |
| `LoginTip` | Los datos curiosos de la pantalla de inicio de sesión |
| `PlaceAlerts` | Las alertas por lugar |
| `MonitoredCamera` | El registro de cámaras vigiladas y sus hilos |
| `ApiMessage` | Las respuestas JSON del administrador |
| `MongoSettings` (en `config.py`) | La conexión a MongoDB; está ahí para no crear un ciclo de importación |
| `ThreatRule` (en `detection.py`) | Las reglas de detección; está ahí para que sus pruebas no necesiten Flask |

**Excepciones:** donde una librería exige un diccionario, el modelo se convierte con `model_dump()` solo en ese punto. Pasa en tres lugares: Flask-MongoEngine, `jsonify` y el contexto de `flask shell`.

## Tecnologías

| Tecnología | Por qué |
|---|---|
| **Flask** | Ligero y fácil de organizar en secciones (*blueprints*). La estructura sigue el libro *Flask Web Development*, de ahí el nombre `flasky` |
| **MongoDB con MongoEngine** | Las alertas de cada cámara son una lista y las fotos van dentro del documento; un esquema flexible lo hace simple. Atlas da una base gratis en la nube |
| **TensorFlow / Keras** | La herramienta más común para entrenar CNN, con buen soporte para guardar y cargar el modelo |
| **OpenCV** | Lee webcams y cámaras IP (por URL, como RTSP) con la misma interfaz |
| **Flask-Mail con Gmail** | Avisar por correo es gratis y llega al teléfono; Gmail permite enviar con una contraseña de aplicación |
| **Twilio** | Para SMS, que llegan sin internet. Está desactivado, probablemente por el costo de cada mensaje |
| **Google Maps** | Para elegir la dirección de la cámara en un mapa en lugar de escribirla |
| **Hilos** (`threading`) | Cada cámara se vigila en paralelo sin bloquear la página. Es simple, pero solo funciona mientras el servidor esté encendido (ver [problemas-conocidos.md](problemas-conocidos.md)) |
