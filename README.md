# Sistema de Estacionamento

Sistema para controle de estacionamento: cadastro de clientes, veículos e vagas, registro de entrada e saída de veículos e cálculo automático do valor cobrado.

Este projeto é a migração de um sistema legado feito em Java 8 com PostgreSQL. O backend foi reescrito em Python com Django e usa SQLite. O frontend é o mesmo do legado, sem alterações de lógica.

## Sumário

- [O que você precisa instalar](#o-que-você-precisa-instalar)
- [Como rodar o projeto](#como-rodar-o-projeto)
- [Front e API: cada um tem seu endereço](#front-e-api-cada-um-tem-seu-endereço)
- [Regras de negócio](#regras-de-negócio)
- [Rotas da API](#rotas-da-api)
- [Formato das respostas](#formato-das-respostas)
- [Testando a API](#testando-a-api)
- [Estrutura do projeto](#estrutura-do-projeto)

## O que você precisa instalar

- [Docker Desktop](https://www.docker.com/products/docker-desktop/). Ao abrir, aguarde aparecer **Engine running** na parte inferior da janela.

Para testar a API, também é necessário um cliente HTTP. Use o [Thunder Client](https://marketplace.visualstudio.com/items?itemName=rangav.vscode-thunder-client) (extensão do VS Code), Insomnia ou Postman. Ele é necessário para os métodos POST, PUT e DELETE.

## Como rodar o projeto

Na raiz do projeto, onde está o arquivo `docker-compose.yml`, abra o terminal e rode:

```
docker compose up --build -d
```

Na primeira execução, o Docker baixa as imagens do Python e do Nginx, instala o Django e cria o banco. Isso pode levar alguns minutos. Nas próximas, o comando é mais rápido.

Verifique se os dois serviços estão rodando:

```
docker compose ps
```

Você deve ver `backend` e `frontend` com o status `running`.

Depois, abra o sistema no navegador em **http://localhost:3000**. Essa é a tela que você usa no dia a dia.

### Comandos do dia a dia

| Ação | Comando |
|---|---|
| Subir os serviços (após alterar o código) | `docker compose up --build -d` |
| Ver os logs do backend | `docker compose logs -f backend` |
| Parar os serviços (mantém os dados) | `docker compose stop` |
| Iniciar de novo | `docker compose start` |
| Reiniciar | `docker compose restart` |
| Remover os containers (mantém os dados) | `docker compose down` |
| Apagar tudo, inclusive o banco | `docker compose down -v` |

Os dados ficam em um volume do Docker (`sqlite_data`). Eles continuam disponíveis depois de `stop`, `restart` e `down`. Só são apagados com `down -v`.

## Front e API: cada um tem seu endereço

O projeto tem duas partes que rodam em endereços diferentes. Elas se comunicam, mas têm papéis distintos.

| Parte | Endereço | O que é | Quem usa |
|---|---|---|---|
| **Front** (tela) | http://localhost:3000 | Páginas HTML, CSS e JavaScript. É a interface do sistema. | Você, no navegador |
| **API** (backend) | http://localhost:8080/api/ | Dados em JSON. Não tem tela. | O JavaScript do front, e você nos testes |

Na prática:

- Para **usar o sistema**, abra **http://localhost:3000**. Não use o endereço da API para navegar.
- O front chama a API nos bastidores. Quando você cadastra um cliente na tela, o JavaScript envia uma requisição para `http://localhost:8080/api/clientes`.
- Se você abrir **http://localhost:8080/api/vagas** no navegador, verá só os dados em JSON, sem nenhuma tela. Isso é esperado.
- Os dois endereços precisam estar rodando ao mesmo tempo. Se o backend parar, a tela carrega, mas as ações falham.

O endereço da API fica configurado em `frontend/js/api.js`, na constante `API_BASE`. Ele aponta para `http://localhost:8080`.

## Regras de negócio

- **Entrada:** um veículo só pode ter uma permanência aberta por vez. A vaga precisa estar `LIVRE` e passa automaticamente para `OCUPADA`.
- **Saída:** a permanência é finalizada, o valor é calculado e a vaga volta automaticamente para `LIVRE`.
- **Tarifa:** R$ 5,00 por hora, com mínimo de 1 hora. Frações de hora são arredondadas para cima. Exemplo: 61 minutos são cobrados como 2 horas (R$ 10,00).
- **Status da vaga:** muda automaticamente na entrada e na saída. Também pode ser alterado pela edição da vaga (`PUT /api/vagas/{id}`), com qualquer valor válido.
- **Exclusão:** cliente, veículo ou vaga com permanências vinculadas não pode ser excluído. Um cliente sem permanências é excluído junto com os seus veículos.
- **Horário:** o sistema usa o horário de Brasília (`America/Sao_Paulo`).

## Rotas da API

As rotas são do **backend**, acessadas em `http://localhost:8080`. Todas começam com `/api/`, e nenhuma termina com barra (`/`).

Estas rotas não são páginas. Elas respondem com JSON e são chamadas pelo front ou por um cliente HTTP.

### Dashboard

| Método | Rota | O que faz |
|---|---|---|
| GET | `/api/dashboard` | Retorna os indicadores: total de vagas, vagas livres, vagas ocupadas e veículos estacionados. |

### Clientes

| Método | Rota | O que faz | Respostas |
|---|---|---|---|
| GET | `/api/clientes` | Lista todos os clientes, por ordem de id. | 200 |
| POST | `/api/clientes` | Cadastra um cliente. Campos obrigatórios: `nome` e `cpf`. | 201, 400, 409 (CPF já cadastrado) |
| GET | `/api/clientes/{id}` | Busca um cliente pelo id. | 200, 404 |
| PUT | `/api/clientes/{id}` | Atualiza os dados do cliente. | 200, 400, 404, 409 |
| DELETE | `/api/clientes/{id}` | Exclui o cliente e seus veículos. Não é permitido se algum veículo tiver permanências. | 200, 404, 409 |

### Veículos

| Método | Rota | O que faz | Respostas |
|---|---|---|---|
| GET | `/api/veiculos` | Lista os veículos, por ordem de placa. Cada item traz o nome do cliente (`clienteNome`). | 200 |
| POST | `/api/veiculos` | Cadastra um veículo. Campos obrigatórios: `placa`, `marca`, `modelo`, `cor` e `clienteId`. | 201, 400, 404 (cliente inexistente), 409 (placa já cadastrada) |
| GET | `/api/veiculos/{id}` | Busca um veículo pelo id. | 200, 404 |
| PUT | `/api/veiculos/{id}` | Atualiza os dados do veículo. | 200, 400, 404, 409 |
| DELETE | `/api/veiculos/{id}` | Exclui o veículo. Não é permitido se ele tiver permanências. | 200, 404, 409 |

### Vagas

| Método | Rota | O que faz | Respostas |
|---|---|---|---|
| GET | `/api/vagas` | Lista as vagas, por ordem de número. Aceita o filtro `?status=LIVRE` ou `?status=OCUPADA`. | 200, 400 (status inválido) |
| POST | `/api/vagas` | Cadastra uma vaga. Campos obrigatórios: `numero` e `tipo` (`CARRO` ou `MOTO`). A vaga nasce `LIVRE`. | 201, 400, 409 (número já cadastrado) |
| GET | `/api/vagas/{id}` | Busca uma vaga pelo id. | 200, 404 |
| PUT | `/api/vagas/{id}` | Atualiza número, tipo e status. O campo `status` é opcional e aceita `LIVRE` ou `OCUPADA`. | 200, 400, 404, 409 |
| DELETE | `/api/vagas/{id}` | Exclui a vaga. Não é permitido se ela tiver permanências. | 200, 404, 409 |

### Permanências

| Método | Rota | O que faz | Respostas |
|---|---|---|---|
| GET | `/api/permanencias` | Lista as permanências, da mais recente para a mais antiga. Aceita o filtro `?status=ABERTO` ou `?status=FINALIZADO`. | 200, 400 (status inválido) |
| POST | `/api/permanencias/entrada` | Registra a entrada de um veículo em uma vaga. Campos obrigatórios: `veiculoId` e `vagaId`. A vaga passa a `OCUPADA`. | 201, 400, 404 (veículo ou vaga inexistente), 409 (veículo já estacionado ou vaga ocupada) |
| PUT | `/api/permanencias/{id}/saida` | Registra a saída. Calcula o `valorTotal`, finaliza a permanência e libera a vaga. Não recebe corpo. | 200, 404, 409 (já finalizada) |

Para qualquer método que não esteja listado em uma rota, a API responde 405. Para uma rota que não existe dentro de `/api/`, responde 404.

## Formato das respostas

Todas as respostas da API são JSON.

**Sucesso:** o corpo traz o recurso ou uma mensagem.

```json
{
  "id": 1,
  "placa": "ABC1D23",
  "marca": "Fiat",
  "modelo": "Uno",
  "cor": "Branco",
  "clienteId": 1,
  "clienteNome": "Maria Silva"
}
```

**Erro:** o corpo traz a chave `error` com a descrição do problema.

```json
{
  "error": "Vaga já está ocupada"
}
```

**Exclusão bem-sucedida:**

```json
{
  "message": "Vaga excluída"
}
```

**Campos das permanências:**

```json
{
  "id": 1,
  "veiculoId": 1,
  "veiculoPlaca": "ABC1D23",
  "veiculoModelo": "Uno",
  "vagaId": 1,
  "vagaNumero": "A01",
  "dataHoraEntrada": "2026-11-05T14:30:00",
  "dataHoraSaida": "2026-11-05T16:10:00",
  "valorTotal": 10.0,
  "status": "FINALIZADO"
}
```

Enquanto a permanência estiver aberta, `dataHoraSaida` e `valorTotal` são `null`.

## Testando a API

Os testes da API são feitos no endereço do **backend**, `http://localhost:8080`, e não no front.

Você pode testar as rotas de `GET` direto no navegador. Os demais métodos precisam de um cliente como o Thunder Client.

Use este roteiro, nesta ordem:

1. `GET http://localhost:8080/api/vagas`: deve listar 15 vagas, todas `LIVRE`.
2. `POST http://localhost:8080/api/clientes` com `{"nome": "Maria Silva", "cpf": "123.456.789-00"}`: deve retornar 201.
3. `POST http://localhost:8080/api/veiculos` com `{"placa": "ABC1D23", "marca": "Fiat", "modelo": "Uno", "cor": "Branco", "clienteId": 1}`: deve retornar 201.
4. `POST http://localhost:8080/api/permanencias/entrada` com `{"veiculoId": 1, "vagaId": 1}`: deve retornar 201, e a vaga A01 passa a `OCUPADA`.
5. `POST http://localhost:8080/api/permanencias/entrada` com o mesmo corpo: deve retornar 409.
6. `PUT http://localhost:8080/api/permanencias/1/saida`: deve retornar 200 com `valorTotal`.
7. Abra **http://localhost:3000** e confira se o front mostra as vagas, os clientes e as permanências cadastrados nos passos anteriores.

## Estrutura do projeto

```
Migração de tecnologia/
├── docker-compose.yml          # sobe backend e frontend
├── README.md
├── backend-django/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt        # Django e dependências
│   ├── manage.py
│   ├── estacionamento/         # configuração do projeto Django
│   │   ├── settings.py
│   │   ├── urls.py             # inclui as rotas de api/
│   │   ├── middleware.py       # cabeçalhos CORS
│   │   ├── wsgi.py
│   │   └── asgi.py
│   └── api/                    # aplicação com as regras e as rotas
│       ├── models.py           # Cliente, Veiculo, Vaga, Permanencia
│       ├── serializers.py      # conversão dos models para JSON
│       ├── exceptions.py       # erros de negócio (400, 404, 409)
│       ├── utils.py            # respostas padrão e tratamento de erros
│       ├── urls.py             # rotas da API
│       ├── services/
│       │   └── permanencia_service.py   # entrada, saída e cálculo do valor
│       ├── views/
│       │   ├── cliente_views.py
│       │   ├── veiculo_views.py
│       │   ├── vaga_views.py
│       │   ├── permanencia_views.py
│       │   └── dashboard_views.py
│       └── migrations/
│           ├── 0001_initial.py      # estrutura das tabelas
│           └── 0002_seed_vagas.py   # 15 vagas iniciais
└── frontend/
    ├── Dockerfile              # Nginx servindo os arquivos estáticos
    ├── nginx.conf
    ├── index.html
    ├── css/
    └── js/
        ├── api.js              # API_BASE aponta para http://localhost:8080
        └── ...
```