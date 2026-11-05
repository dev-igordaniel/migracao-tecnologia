import math
from datetime import datetime
from decimal import Decimal

from django.db import transaction

from api.exceptions import Conflito, NaoEncontrado
from api.models import Permanencia, Vaga, Veiculo

TARIFA_HORA = Decimal("5.00")


def _calcular_valor(entrada, saida):
    minutos = int((saida - entrada).total_seconds() // 60)
    horas = max(1, math.ceil(minutos / 60))
    return TARIFA_HORA * horas


def registrar_entrada(veiculo_id, vaga_id):
    with transaction.atomic():
        veiculo = Veiculo.objects.select_for_update().filter(id=veiculo_id).first()
        if veiculo is None:
            raise NaoEncontrado("Veículo não encontrado")

        if Permanencia.objects.filter(veiculo=veiculo, status="ABERTO").exists():
            raise Conflito("Veículo já possui uma permanência em aberto")

        vaga = Vaga.objects.select_for_update().filter(id=vaga_id).first()
        if vaga is None:
            raise NaoEncontrado("Vaga não encontrada")
        if vaga.status != "LIVRE":
            raise Conflito("Vaga já está ocupada")

        vaga.status = "OCUPADA"
        vaga.save(update_fields=["status"])

        return Permanencia.objects.create(
            veiculo=veiculo,
            vaga=vaga,
            data_hora_entrada=datetime.now(),
            status="ABERTO",
        )


def registrar_saida(permanencia_id):
    with transaction.atomic():
        permanencia = (
            Permanencia.objects.select_related("veiculo", "vaga")
            .select_for_update()
            .filter(id=permanencia_id)
            .first()
        )
        if permanencia is None:
            raise NaoEncontrado("Permanência não encontrada")
        if permanencia.status != "ABERTO":
            raise Conflito("Permanência já foi finalizada")

        agora = datetime.now()
        permanencia.data_hora_saida = agora
        permanencia.valor_total = _calcular_valor(permanencia.data_hora_entrada, agora)
        permanencia.status = "FINALIZADO"
        permanencia.save(update_fields=["data_hora_saida", "valor_total", "status"])

        vaga = permanencia.vaga
        vaga.status = "LIVRE"
        vaga.save(update_fields=["status"])

        return permanencia