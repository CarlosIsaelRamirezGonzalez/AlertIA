"""Pruebas de la configuración: la clave secreta es obligatoria fuera de desarrollo."""

import importlib
import os
import sys
import unittest
from unittest import mock

# config.py está en flasky/, un nivel arriba de estas pruebas.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class FakeConfig:
    """Lee los valores de una clase de configuración, como `app.config` después de `from_object`.

    Attributes:
        config_class: Clase de configuración.
    """

    def __init__(self, config_class):
        """Guarda la clase de configuración.

        Args:
            config_class: Clase de configuración.
        """
        self.config_class = config_class

    def get(self, name, default=None):
        """Busca un valor, como `app.config.get`.

        Args:
            name: Nombre del valor.
            default: Lo que se regresa si no existe.

        Returns:
            El valor configurado, o `default`.
        """
        return getattr(self.config_class, name, default)


class FakeApp:
    """Lo mínimo de una aplicación de Flask que necesita `init_app`.

    Attributes:
        config: Valores de configuración.
    """

    def __init__(self, config_class):
        """Prepara la configuración de la aplicación.

        Args:
            config_class: Clase de configuración.
        """
        self.config = FakeConfig(config_class)


def load_config(**environment):
    """Carga `config.py` de nuevo con ciertas variables de entorno.

    Args:
        **environment: Variables que se definen; `SECRET_KEY` y `SECRET` se quitan si no se pasan.

    Returns:
        El módulo de configuración recién cargado.
    """
    # patch.dict restaura el entorno al salir, aunque aquí se quiten variables.
    with mock.patch.dict(os.environ, environment):
        for name in ('SECRET_KEY', 'SECRET'):
            if name not in environment:
                os.environ.pop(name, None)
        import config

        return importlib.reload(config)


class ConfigTest(unittest.TestCase):
    """Pruebas de la clave secreta por entorno."""

    def test_production_fails_without_secret_key(self):
        """Sin SECRET_KEY, producción no arranca."""
        config = load_config()
        production = config.get_config('production')
        with self.assertRaises(RuntimeError):
            production.init_app(FakeApp(production))

    def test_testing_fails_without_secret_key(self):
        """Sin SECRET_KEY, el entorno de pruebas tampoco arranca."""
        config = load_config()
        testing = config.get_config('testing')
        with self.assertRaises(RuntimeError):
            testing.init_app(FakeApp(testing))

    def test_development_starts_without_secret_key(self):
        """En desarrollo se usa una clave local para poder arrancar sin configurar nada."""
        config = load_config()
        development = config.get_config('development')
        development.init_app(FakeApp(development))
        self.assertEqual(development.SECRET_KEY, config.DEVELOPMENT_SECRET_KEY)

    def test_production_uses_the_defined_secret_key(self):
        """Con SECRET_KEY definida, producción arranca y la usa."""
        config = load_config(SECRET_KEY='clave-de-prueba')
        production = config.get_config('production')
        production.init_app(FakeApp(production))
        self.assertEqual(production.SECRET_KEY, 'clave-de-prueba')

    def test_old_secret_variable_is_still_accepted(self):
        """La variable vieja SECRET sigue funcionando."""
        config = load_config(SECRET='clave-vieja')
        self.assertEqual(config.get_config('production').SECRET_KEY, 'clave-vieja')


if __name__ == '__main__':
    unittest.main()
