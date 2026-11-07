"""Reglas de detección: qué clase del modelo es una amenaza y cuándo se confirma.

No depende de Flask ni de TensorFlow, así que se puede probar sola (ver tests/).
"""

from pydantic import BaseModel, ConfigDict

# Orden de las clases del modelo Aria.keras. Es el orden alfabético de las carpetas del dataset,
# que es como Keras numera las clases al entrenar.
CLASS_LABELS = (
    "Arma blanca",
    "Arma corta",
    "Arma larga",
    "Ataque de perro",
    "Choques",
    "Encañonamiento",
    "Forcejeos",
    "Golpe",
    "Incendio",
    "Normalidad",
    "Patada",
    "Persona herida",
)
NORMAL_CLASS = 9
# Solo cuenta una detección si el modelo está así de seguro.
MIN_CERTAINTY = 0.95
# Sin detecciones durante este tiempo, se olvidan las anteriores.
ALERT_MODE_SECONDS = 20
# No se repite la misma amenaza antes de este tiempo.
REPEAT_MINUTES = 3


class ThreatRule(BaseModel):
    """Regla para confirmar una amenaza a partir de varias detecciones.

    Attributes:
        threat: Nombre de la amenaza que se notifica.
        classes: Clases del modelo que cuentan para esta amenaza.
        needed: Detecciones necesarias para confirmarla.
        alerts: Alertas de la cámara que la permiten; basta con una.
    """

    model_config = ConfigDict(frozen=True)

    threat: str
    classes: tuple[int, ...]
    needed: int
    alerts: tuple[str, ...]


# Se revisan en este orden. Pedir varias detecciones evita avisar por un solo cuadro mal clasificado;
# las amenazas más graves (armas) piden menos que las que se confunden más (choques, peleas).
RULES = (
    ThreatRule(threat="Armas de fuego", classes=(1, 2, 5), needed=10, alerts=("handgun", "long_gun", "cannoning")),
    ThreatRule(threat="Armas blancas", classes=(0,), needed=10, alerts=("bladed_weapon", "stabbing")),
    ThreatRule(threat="Ataque de perros", classes=(3,), needed=15, alerts=("dog_attack",)),
    ThreatRule(threat="Incendios", classes=(8,), needed=20, alerts=("fires",)),
    ThreatRule(threat="Choques", classes=(4,), needed=30, alerts=("car_accident",)),
    ThreatRule(threat="Persona herida", classes=(11,), needed=30, alerts=("injured_people",)),
    ThreatRule(threat="Pelea", classes=(6, 7, 10), needed=30, alerts=("brawls",)),
    ThreatRule(threat="Encañonamiento", classes=(5,), needed=10, alerts=("cannoning",)),
)


def is_detection(predicted_class: int, certainty: float) -> bool:
    """Decide si una predicción cuenta como posible amenaza.

    Args:
        predicted_class: Índice de la clase con mayor probabilidad.
        certainty: Probabilidad de esa clase, de 0 a 1.

    Returns:
        Si no es normalidad y el modelo está suficientemente seguro.
    """
    return predicted_class != NORMAL_CLASS and certainty > MIN_CERTAINTY


def confirmed_threat(detections: list[int], camera_alerts: list[str]) -> str | None:
    """Busca la primera amenaza con suficientes detecciones.

    Igual que antes, solo se revisa la primera regla que alcanza su umbral: si la cámara no tiene
    esa alerta activa, no se notifica nada en esta vuelta.

    Args:
        detections: Clases detectadas desde que empezó el modo alerta.
        camera_alerts: Alertas activas de la cámara, como `fires`.

    Returns:
        El nombre de la amenaza que hay que notificar, o None.
    """
    for rule in RULES:
        if sum(detections.count(cls) for cls in rule.classes) >= rule.needed:
            return rule.threat if any(alert in camera_alerts for alert in rule.alerts) else None
    return None
