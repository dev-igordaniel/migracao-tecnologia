import json
from functools import wraps

from django.db import IntegrityError
from django.db.models import ProtectedError
from django.http import JsonResponse

from api.exceptions import Conflito, Invalido, NaoEncontrado


def erro(texto, status):
    return JsonResponse({"error": texto}, status=status)


def mensagem(texto, status=200):
    return JsonResponse({"message": texto}, status=status)


def metodo_nao_permitido():
    return erro("Método não permitido", 405)


def rota_nao_encontrada(request, *args, **kwargs):
    return erro("Rota não encontrada", 404)


def ler_json(request):
    try:
        dados = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        raise Invalido("Corpo da requisição inválido")
    if not isinstance(dados, dict):
        raise Invalido("Corpo da requisição deve ser um objeto JSON")
    return dados


def exigir(dados, campos):
    for campo in campos:
        valor = dados.get(campo)
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise Invalido(f"Campo '{campo}' é obrigatório")


def inteiro(valor, campo):
    try:
        return int(valor)
    except (TypeError, ValueError):
        raise Invalido(f"Campo '{campo}' deve ser um número inteiro")


def tratar_erros(view):
    @wraps(view)
    def envelope(request, *args, **kwargs):
        try:
            return view(request, *args, **kwargs)
        except Invalido as e:
            return erro(str(e), 400)
        except NaoEncontrado as e:
            return erro(str(e), 404)
        except Conflito as e:
            return erro(str(e), 409)
        except ProtectedError:
            return erro("Registro possui vínculos e não pode ser excluído", 409)
        except IntegrityError:
            return erro("Dados conflitam com registros existentes", 409)

    return envelope