from django.http import JsonResponse

from api.exceptions import Conflito, NaoEncontrado
from api.models import Cliente, Permanencia
from api.serializers import cliente_to_dict
from api.utils import exigir, ler_json, mensagem, metodo_nao_permitido, tratar_erros


def _buscar(id):
    cliente = Cliente.objects.filter(id=id).first()
    if cliente is None:
        raise NaoEncontrado("Cliente não encontrado")
    return cliente


def _cpf_em_uso(cpf, ignorar_id=None):
    qs = Cliente.objects.filter(cpf=cpf)
    if ignorar_id is not None:
        qs = qs.exclude(id=ignorar_id)
    return qs.exists()


@tratar_erros
def lista_clientes(request):
    if request.method == "GET":
        clientes = Cliente.objects.order_by("id")
        return JsonResponse([cliente_to_dict(c) for c in clientes], safe=False)

    if request.method == "POST":
        dados = ler_json(request)
        exigir(dados, ["nome", "cpf"])
        if _cpf_em_uso(dados["cpf"]):
            raise Conflito("CPF já cadastrado")
        cliente = Cliente.objects.create(
            nome=dados["nome"],
            cpf=dados["cpf"],
            telefone=dados.get("telefone") or None,
            email=dados.get("email") or None,
        )
        return JsonResponse(cliente_to_dict(cliente), status=201)

    return metodo_nao_permitido()


@tratar_erros
def detalhe_cliente(request, id):
    if request.method == "GET":
        return JsonResponse(cliente_to_dict(_buscar(id)))

    if request.method == "PUT":
        cliente = _buscar(id)
        dados = ler_json(request)
        exigir(dados, ["nome", "cpf"])
        if _cpf_em_uso(dados["cpf"], ignorar_id=cliente.id):
            raise Conflito("CPF já cadastrado")
        cliente.nome = dados["nome"]
        cliente.cpf = dados["cpf"]
        cliente.telefone = dados.get("telefone") or None
        cliente.email = dados.get("email") or None
        cliente.save()
        return JsonResponse(cliente_to_dict(cliente))

    if request.method == "DELETE":
        cliente = _buscar(id)
        if Permanencia.objects.filter(veiculo__cliente=cliente).exists():
            raise Conflito("Cliente possui veículos com permanências e não pode ser excluído")
        cliente.delete()
        return mensagem("Cliente excluído")

    return metodo_nao_permitido()