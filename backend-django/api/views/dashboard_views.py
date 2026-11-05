from django.http import JsonResponse

from api.models import Permanencia, Vaga
from api.utils import metodo_nao_permitido, tratar_erros


@tratar_erros
def dashboard(request):
    if request.method == "GET":
        return JsonResponse({
            "totalVagas": Vaga.objects.count(),
            "vagasLivres": Vaga.objects.filter(status="LIVRE").count(),
            "vagasOcupadas": Vaga.objects.filter(status="OCUPADA").count(),
            "veiculosEstacionados": Permanencia.objects.filter(status="ABERTO").count(),
        })

    return metodo_nao_permitido()