def _iso(data):
    return data.isoformat(timespec="seconds") if data else None


def _decimal(valor):
    return float(valor) if valor is not None else None


def cliente_to_dict(c):
    return {
        "id": c.id,
        "nome": c.nome,
        "cpf": c.cpf,
        "telefone": c.telefone,
        "email": c.email,
    }


def veiculo_to_dict(v):
    return {
        "id": v.id,
        "placa": v.placa,
        "marca": v.marca,
        "modelo": v.modelo,
        "cor": v.cor,
        "clienteId": v.cliente_id,
        "clienteNome": v.cliente.nome,
    }


def vaga_to_dict(v):
    return {
        "id": v.id,
        "numero": v.numero,
        "tipo": v.tipo,
        "status": v.status,
    }


def permanencia_to_dict(p):
    return {
        "id": p.id,
        "veiculoId": p.veiculo_id,
        "veiculoPlaca": p.veiculo.placa,
        "veiculoModelo": p.veiculo.modelo,
        "vagaId": p.vaga_id,
        "vagaNumero": p.vaga.numero,
        "dataHoraEntrada": _iso(p.data_hora_entrada),
        "dataHoraSaida": _iso(p.data_hora_saida),
        "valorTotal": _decimal(p.valor_total),
        "status": p.status,
    }