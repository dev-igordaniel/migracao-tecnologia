from django.http import JsonResponse

from api.exceptions import Invalido
from api.models import STATUS_PERMANENCIA, Permanencia
from api.serializers import permanencia_to_dict
from api.services.permanencia_service import registrar_entrada, registrar_saida
from api.utils import exigir, inteiro, ler_json, metodo_nao_permitido, tratar_erros


@tratar_erros
def lista_permanencias(request):
    if request.method == "GET":
        permanencias = (
            Permanencia.objects.select_related("veiculo", "vaga")
            .order_by("-data_hora_entrada")
        )
        status = request.GET.get("status")
        if status:
            if status not in STATUS_PERMANENCIA:
                raise Invalido("Status deve ser ABERTO ou FINALIZADO")
            permanencias = permanencias.filter(status=status)
        return JsonResponse([permanencia_to_dict(p) for p in permanencias], safe=False)

    return metodo_nao_permitido()


@tratar_erros
def entrada(request):
    if request.method == "POST":
        dados = ler_json(request)
        exigir(dados, ["veiculoId", "vagaId"])
        permanencia = registrar_entrada(
            inteiro(dados["veiculoId"], "veiculoId"),
            inteiro(dados["vagaId"], "vagaId"),
        )
        return JsonResponse(permanencia_to_dict(permanencia), status=201)

    return metodo_nao_permitido()


@tratar_erros
def saida(request, id):
    if request.method == "PUT":
        permanencia = registrar_saida(id)
        return JsonResponse(permanencia_to_dict(permanencia))

    return metodo_nao_permitido()