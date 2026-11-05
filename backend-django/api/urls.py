from django.urls import path, re_path

from api.utils import rota_nao_encontrada
from api.views import cliente_views, dashboard_views, permanencia_views, vaga_views, veiculo_views

urlpatterns = [
    path("dashboard", dashboard_views.dashboard),

    path("clientes", cliente_views.lista_clientes),
    path("clientes/<int:id>", cliente_views.detalhe_cliente),

    path("veiculos", veiculo_views.lista_veiculos),
    path("veiculos/<int:id>", veiculo_views.detalhe_veiculo),

    path("vagas", vaga_views.lista_vagas),
    path("vagas/<int:id>", vaga_views.detalhe_vaga),

    path("permanencias", permanencia_views.lista_permanencias),
    path("permanencias/entrada", permanencia_views.entrada),
    path("permanencias/<int:id>/saida", permanencia_views.saida),

    re_path(r"^.*$", rota_nao_encontrada),
]