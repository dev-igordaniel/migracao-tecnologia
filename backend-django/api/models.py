from datetime import datetime

from django.db import models
from django.db.models import Q

TIPOS_VAGA = ["CARRO", "MOTO"]
STATUS_VAGA = ["LIVRE", "OCUPADA"]
STATUS_PERMANENCIA = ["ABERTO", "FINALIZADO"]


class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)


class Veiculo(models.Model):
    placa = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    cor = models.CharField(max_length=30)
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="veiculos",
        db_index=False,
    )

    class Meta:
        indexes = [
            models.Index(fields=["cliente"], name="idx_veiculos_cliente_id"),
        ]


class Vaga(models.Model):
    numero = models.CharField(max_length=10, unique=True)
    tipo = models.CharField(max_length=5, choices=[(t, t) for t in TIPOS_VAGA])
    status = models.CharField(
        max_length=7,
        choices=[(s, s) for s in STATUS_VAGA],
        default="LIVRE",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(tipo__in=TIPOS_VAGA), name="vaga_tipo_valido"),
            models.CheckConstraint(condition=Q(status__in=STATUS_VAGA), name="vaga_status_valido"),
        ]


class Permanencia(models.Model):
    veiculo = models.ForeignKey(
        Veiculo,
        on_delete=models.PROTECT,
        related_name="permanencias",
        db_index=False,
    )
    vaga = models.ForeignKey(
        Vaga,
        on_delete=models.PROTECT,
        related_name="permanencias",
        db_index=False,
    )
    data_hora_entrada = models.DateTimeField(default=datetime.now)
    data_hora_saida = models.DateTimeField(blank=True, null=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=[(s, s) for s in STATUS_PERMANENCIA],
        default="ABERTO",
    )

    class Meta:
        indexes = [
            models.Index(fields=["status"], name="idx_permanencias_status"),
            models.Index(fields=["veiculo"], name="idx_permanencias_veiculo_id"),
            models.Index(fields=["vaga"], name="idx_permanencias_vaga_id"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=STATUS_PERMANENCIA),
                name="permanencia_status_valido",
            ),
        ]