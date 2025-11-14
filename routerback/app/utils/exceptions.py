"""
Excepciones personalizadas
"""


class RasaConnectionError(Exception):
    """Error al conectarse con RASA"""
    pass


class RasaTimeoutError(Exception):
    """Timeout al comunicarse con RASA"""
    pass


class InvalidMessageError(Exception):
    """Mensaje inválido"""
    pass
