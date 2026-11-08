# Inteligencia artificial

## El modelo

- **Archivo:** `Artificial_Intelligence/Aria.keras`, de unos 8 MB, en formato Keras 3.
- **Tipo:** clasificador de imágenes. Recibe una imagen de 256 × 256 en RGB con valores de 0 a 1 y regresa la probabilidad de cada una de 12 clases.
- **Nombre:** la página de inicio de sesión dice que la IA se llama "alertito".

Antes había dos archivos, `ARIA.keras` y `Aria.keras`, con exactamente el mismo contenido. En Windows y macOS chocaban porque solo cambian las mayúsculas, así que se dejó solo `Aria.keras`.

## Arquitectura

Se leyó del propio archivo (`config.json` dentro de `Aria.keras`, guardado el 13 de junio de 2024 con Keras 3.0.5). Es una red neuronal convolucional (CNN):

| Bloque | Capas |
|---|---|
| Entrada | 256 × 256 × 3 |
| 1 | Conv 32 (2×2) → BatchNorm → Conv 64 (2×2, paso 2) → BatchNorm → MaxPool → Dropout 0.2 |
| 2 | Conv 128 → BatchNorm → MaxPool → Dropout 0.2 |
| 3 | Conv 128 → BatchNorm → Conv 256 → BatchNorm → MaxPool → Dropout 0.2 |
| 4 | Conv 256 → BatchNorm → Conv 128 → BatchNorm → MaxPool → Dropout 0.2 |
| 5 | Conv 64 → BatchNorm → Conv 32 → BatchNorm → MaxPool |
| Salida | Flatten → Dropout 0.2 → Dense 32 (ReLU) → Dense 12 (softmax) |

Todas las convoluciones usan ReLU. Se compiló con Adam, pérdida `sparse_categorical_crossentropy` y métrica de exactitud.

## Clases

Keras numera las clases en orden alfabético por el nombre de las carpetas, y este es ese orden. Es el mismo que usaba el notebook y que ahora usa `flasky/app/detection.py`:

| Índice | Clase |
|---|---|
| 0 | Arma blanca |
| 1 | Arma corta |
| 2 | Arma larga |
| 3 | Ataque de perro |
| 4 | Choques |
| 5 | Encañonamiento |
| 6 | Forcejeos |
| 7 | Golpe |
| 8 | Incendio |
| 9 | Normalidad |
| 10 | Patada |
| 11 | Persona herida |

## El entrenamiento

El código original se perdió. `scripts/train.py` lo reconstruye:

- **Igual que el original:** la arquitectura, capa por capa (comprobado contra el archivo), el optimizador, la pérdida y la métrica.
- **Supuestos:** imágenes escaladas de 0 a 1 antes de entrar, porque la app divide entre 255 y el modelo no tiene capa de escala; lotes de 32; 20 % de validación; hasta 20 épocas con parada temprana; y se guarda el modelo con mejor exactitud de validación.

Para limpiar el dataset antes de entrenar existe `clean_dataset.py`. Nunca toca la carpeta original:
escribe un dataset nuevo y un reporte JSON con cada archivo descartado y el motivo.

1. **Descarta** la basura del sistema (`.DS_Store`, `desktop.ini`…), lo que no es imagen, las imágenes
   dañadas o truncadas y las de menos de 64 px de lado.
2. **Quita repetidas:** duplicados exactos y casi duplicados (la misma foto con otra compresión,
   tamaño o formato, detectada con una huella visual). De cada grupo se queda la de mayor resolución.
3. **Conflictos:** si la misma foto está en dos clases, no se queda en ninguna y aparece en el reporte
   como `conflicto-entre-clases` para revisarla a mano.
4. **Normaliza:** JPEG RGB, orientación corregida, sin metadatos y con el lado más largo en 512 px.
   Con las imágenes actuales, 1.3 GB bajan a unos 220 MB.
5. **Clases:** une los nombres de carpeta con los del modelo ("Armas blancas" → "Arma blanca",
   "Negativos dificiles" → "Normalidad") y reconoce carpetas con acentos dañados por un ZIP.
   "Carpeta general" se excluye; se puede incluir con `--include "Carpeta general"`.

## Scripts

Los notebooks se convirtieron en scripts sin rutas fijas de ninguna computadora:

```powershell
# Entrenar de nuevo (reconstrucción)
python Artificial_Intelligence/scripts/train.py C:\ruta\al\dataset --output Artificial_Intelligence/Aria.keras

# Revisar el dataset sin escribir nada (solo reporte)
python Artificial_Intelligence/scripts/clean_dataset.py AlertIA-images

# Escribir el dataset limpio en una carpeta nueva
python Artificial_Intelligence/scripts/clean_dataset.py AlertIA-images --output AlertIA-limpio

# Empaquetar el dataset limpio para Kaggle (ZIP, labels.csv, ficha y metadatos)
python Artificial_Intelligence/scripts/package_dataset.py AlertIA-limpio --owner TU_USUARIO_DE_KAGGLE

# Probar con una imagen
python Artificial_Intelligence/scripts/predict.py imagen "Artificial_Intelligence/Imagenes/Incendio.jpg"

# Probar con la cámara (q para salir)
python Artificial_Intelligence/scripts/predict.py camara --index 0
```

Tanto `predict.py` como la app convierten la imagen de la cámara de BGR, que es como la entrega OpenCV, a RGB, que es como se entrenó el modelo.
