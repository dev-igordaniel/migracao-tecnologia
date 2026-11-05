from django.http import JsonResponse

from api.exceptions import Conflito, Invalido, NaoEncontrado
from api.models import STATUS_VAGA, TIPOS_VAGA, Permanencia, Vaga
from api.serializers import vaga_to_dict
from api.utils import exigir, ler_json, mensagem, metodo_nao_permitido, tratar_erros


def _buscar(id):
    vaga = Vaga.objects.filter(id=id).first()
    if vaga is None:
        raise NaoEncontrado("Vaga não encontrada")
    return vaga


def _numero_em_uso(numero, ignorar_id=None):
    qs = Vaga.objects.filter(numero=numero)
    if ignorar_id is not None:
        qs = qs.exclude(id=ignorar_id)
    return qs.exists()


def _validar_tipo(tipo):
    if tipo not in TIPOS_VAGA:
        raise Invalido("Tipo deve ser CARRO ou MOTO")


def _validar_status(status):
    if status not in STATUS_VAGA:
        raise Invalido("Status deve ser LIVRE ou OCUPADA")


@tratar_erros
def lista_vagas(request):
    if request.method == "GET":
        vagas = Vaga.objects.order_by("numero")
        status = request.GET.get("status")
        if status:
            _validar_status(status)
            vagas = vagas.filter(status=status)
        return JsonResponse([vaga_to_dict(v) for v in vagas], safe=False)

    if request.method == "POST":
        dados = ler_json(request)
        exigir(dados, ["numero", "tipo"])
        _validar_tipo(dados["tipo"])
        if _numero_em_uso(dados["numero"]):
            raise Conflito("Número de vaga já cadastrado")
        vaga = Vaga.objects.create(numero=dados["numero"], tipo=dados["tipo"])
        return JsonResponse(vaga_to_dict(vaga), status=201)

    return metodo_nao_permitido()


@tratar_erros
def detalhe_vaga(request, id):
    if request.method == "GET":
        return JsonResponse(vaga_to_dict(_buscar(id)))

    if request.method == "PUT":
        vaga = _buscar(id)
        dados = ler_json(request)
        exigir(dados, ["numero", "tipo"])
        _validar_tipo(dados["tipo"])
        status = dados.get("status", vaga.status)
        _validar_status(status)
        if _numero_em_uso(dados["numero"], ignorar_id=vaga.id):
            raise Conflito("Número de vaga já cadastrado")
        vaga.numero = dados["numero"]
        vaga.tipo = dados["tipo"]
        vaga.status = status
        vaga.save()
        return JsonResponse(vaga_to_dict(vaga))

    if request.method == "DELETE":
        vaga = _buscar(id)
        if Permanencia.objects.filter(vaga=vaga).exists():
            raise Conflito("Vaga possui permanências e não pode ser excluída")
        vaga.delete()
        return mensagem("Vaga excluída")

    return metodo_nao_permitido()