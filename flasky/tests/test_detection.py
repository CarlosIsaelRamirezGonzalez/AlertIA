"""Pruebas de las reglas de detección. Se corren con `flask test` o `python -m unittest`."""

import importlib.util
import os
import unittest

# Se carga el archivo directamente, para no necesitar Flask ni MongoDB en estas pruebas.
_PATH = os.path.join(os.path.dirname(__file__), "..", "app", "detection.py")
_SPEC = importlib.util.spec_from_file_location("detection", _PATH)
detection = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(detection)


class DetectionTest(unittest.TestCase):
    """Pruebas de las reglas que confirman una amenaza."""

    def test_normal_is_never_a_detection(self):
        """La normalidad nunca cuenta, aunque el modelo esté muy seguro."""
        self.assertFalse(detection.is_detection(detection.NORMAL_CLASS, 0.99))

    def test_low_certainty_is_ignored(self):
        """Por debajo del 95 % de certeza no cuenta."""
        self.assertFalse(detection.is_detection(8, 0.80))
        self.assertTrue(detection.is_detection(8, 0.97))

    def test_class_order_matches_the_model(self):
        """El orden de las clases es el del modelo."""
        self.assertEqual(detection.CLASS_LABELS[detection.NORMAL_CLASS], "Normalidad")
        self.assertEqual(detection.CLASS_LABELS[8], "Incendio")
        self.assertEqual(detection.CLASS_LABELS[11], "Persona herida")

    def test_fire_needs_twenty_detections(self):
        """Un incendio necesita 20 detecciones."""
        self.assertIsNone(detection.confirmed_threat([8] * 19, ["fires"]))
        self.assertEqual(detection.confirmed_threat([8] * 20, ["fires"]), "Incendios")

    def test_blow_counts_as_fight_not_fire(self):
        """Golpe (7) cuenta como pelea, no como incendio."""
        self.assertEqual(detection.confirmed_threat([7] * 30, ["brawls", "fires"]), "Pelea")

    def test_injured_person_uses_class_eleven(self):
        """Persona herida es la clase 11."""
        self.assertEqual(detection.confirmed_threat([11] * 30, ["injured_people"]), "Persona herida")

    def test_threat_needs_the_camera_alert(self):
        """Sin la alerta en la cámara no se notifica; apuñalamiento cuenta para armas blancas."""
        self.assertIsNone(detection.confirmed_threat([0] * 10, ["fires"]))
        self.assertEqual(detection.confirmed_threat([0] * 10, ["stabbing"]), "Armas blancas")

    def test_firearms_group_short_long_and_pointing(self):
        """Arma corta, arma larga y encañonamiento suman para armas de fuego."""
        self.assertEqual(detection.confirmed_threat([1] * 4 + [2] * 3 + [5] * 3, ["handgun"]), "Armas de fuego")


if __name__ == "__main__":
    unittest.main()
