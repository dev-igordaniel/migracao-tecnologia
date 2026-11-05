class Invalido(Exception):
    """Dados ausentes ou com formato errado. Resposta 400."""


class NaoEncontrado(Exception):
    """Recurso inexistente. Resposta 404."""


class Conflito(Exception):
    """Regra de negócio ou duplicidade. Resposta 409."""