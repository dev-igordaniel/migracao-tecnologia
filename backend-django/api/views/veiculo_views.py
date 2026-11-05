from django.http import JsonResponse

from api.exceptions import Conflito, NaoEncontrado
from api.models import Cliente, Permanencia, Veiculo
from api.serializers import veiculo_to_dict
from api.utils import exigir, inteiro, ler_json, mensagem, metodo_nao_permitido, tratar_erros

CAMPOS_OBRIGATORIOS = ["placa", "marca", "modelo", "cor", "clienteId"]


def _buscar(id):
    veiculo = Veiculo.objects.select_related("cliente").filter(id=id).first()
    if veiculo is None:
        raise NaoEncontrado("Veículo não encontrado")
    return veiculo


def _validar_cliente(dados):
    cliente_id = inteiro(dados["clienteId"], "clienteId")
    if not Cliente.objects.filter(id=cliente_id).exists():
        raise NaoEncontrado("Cliente não encontrado")
    return cliente_id


def _placa_em_uso(placa, ignorar_id=None):
    qs = Veiculo.objects.filter(placa=placa)
    if ignorar_id is not None:
        qs = qs.exclude(id=ignorar_id)
    return qs.exists()


@tratar_erros
def lista_veiculos(request):
    if request.method == "GET":
        veiculos = Veiculo.objects.select_related("cliente").order_by("placa")
        return JsonResponse([veiculo_to_dict(v) for v in veiculos], safe=False)

    if request.method == "POST":
        dados = ler_json(request)
        exigir(dados, CAMPOS_OBRIGATORIOS)
        cliente_id = _validar_cliente(dados)
        if _placa_em_uso(dados["placa"]):
            raise Conflito("Placa já cadastrada")
        veiculo = Veiculo.objects.create(
            placa=dados["placa"],
            marca=dados["marca"],
            modelo=dados["modelo"],
            cor=dados["cor"],
            cliente_id=cliente_id,
        )
        return JsonResponse(veiculo_to_dict(veiculo), status=201)

    return metodo_nao_permitido()


@tratar_erros
def detalhe_veiculo(request, id):
    if request.method == "GET":
        return JsonResponse(veiculo_to_dict(_buscar(id)))

    if request.method == "PUT":
        veiculo = _buscar(id)
        dados = ler_json(request)
        exigir(dados, CAMPOS_OBRIGATORIOS)
        cliente_id = _validar_cliente(dados)
        if _placa_em_uso(dados["placa"], ignorar_id=veiculo.id):
            raise Conflito("Placa já cadastrada")
        veiculo.placa = dados["placa"]
        veiculo.marca = dados["marca"]
        veiculo.modelo = dados["modelo"]
        veiculo.cor = dados["cor"]
        veiculo.cliente_id = cliente_id
        veiculo.save()
        veiculo = _buscar(veiculo.id)
        return JsonResponse(veiculo_to_dict(veiculo))

    if request.method == "DELETE":
        veiculo = _buscar(id)
        if Permanencia.objects.filter(veiculo=veiculo).exists():
            raise Conflito("Veículo possui permanências e não pode ser excluído")
        veiculo.delete()
        return mensagem("Veículo excluído")

    return metodo_nao_permitido()