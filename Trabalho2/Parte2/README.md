# Sala de aula inteligente - Parte 2

Trabalho pratico da disciplina SSC0142 - Redes de Computadores.

A aplicacao implementa um protocolo de camada de aplicacao para uma sala de
aula inteligente. O nucleo da entrega usa sockets TCP, processos separados e
mensagens JSON delimitadas por quebra de linha.

O prototipo FastAPI de leitura de QR Code foi mantido em `app/` como apoio
opcional ao leitor de cartao, mas nao e necessario para executar o fluxo
principal do trabalho.

## Protocolo

O protocolo da aplicacao e `SMARTROOM/1.0`.

Toda mensagem enviada por TCP segue este formato:

```json
{
  "protocol_id": "SMARTROOM/1.0",
  "message_type": "...",
  "source_id": "...",
  "source_type": "...",
  "target_id": "...",
  "timestamp": "...",
  "payload": {}
}
```

As mensagens sao codificadas em JSON e terminadas por `\n`.

Tipos de mensagem implementados:

- `HELLO`
- `ACK`
- `ERROR`
- `PRESENCE_UPDATE`
- `STUDENT_CHECKIN`
- `PROJECTOR_SWITCH`
- `ACTUATOR_COMMAND`
- `ATTENDANCE_REQUEST`
- `ATTENDANCE_RESPONSE`

A especificacao completa esta em
[`smartroom/docs/protocolo.md`](smartroom/docs/protocolo.md).

## Componentes

Gerenciador:

- `smartroom/manager/gerenciador.py`

Sensores:

- `smartroom/sensors/sensor_presenca.py`
- `smartroom/sensors/leitor_cartao.py`
- `smartroom/sensors/chave_projetor.py`

Atuadores:

- `smartroom/actuators/atuador_iluminacao.py`
- `smartroom/actuators/atuador_projetor.py`
- `smartroom/actuators/atuador_ar_condicionado.py`

Cliente/professor:

- `smartroom/client/cliente_professor.py`

Codigo compartilhado:

- `smartroom/protocol/constants.py`
- `smartroom/protocol/message.py`
- `smartroom/protocol/socket_utils.py`
- `smartroom/components/base_client.py`

## Requisitos atendidos

Todos os sensores e atuadores possuem identificador unico e se registram no
Gerenciador com `HELLO`/`ACK`.

O sensor de presenca envia `PRESENCE_UPDATE`. Quando ha pessoas na sala, o
Gerenciador liga iluminacao e ar-condicionado. Quando a sala fica vazia, o
Gerenciador inicia o controle de ausencia e desliga iluminacao, projetor e
ar-condicionado apos o limite configurado.

A chave do projetor envia `PROJECTOR_SWITCH`. Quando ligada, o Gerenciador
apaga as luzes e liga o projetor. Quando desligada, liga as luzes e desliga o
projetor.

O leitor de cartao envia `STUDENT_CHECKIN` com numero e nome do aluno. O
Gerenciador armazena a lista de presenca em memoria e evita duplicidade pelo
numero do aluno.

O cliente/professor envia `ATTENDANCE_REQUEST` e recebe
`ATTENDANCE_RESPONSE` com a lista de alunos presentes.

O Gerenciador implementa a regra de desligamento geral das 23h. Em modo demo, a
mesma regra e simulada apos poucos segundos para facilitar a apresentacao.

## Ambiente

Ambiente usado no desenvolvimento:

- Sistema operacional: Microsoft Windows 11 Home Single Language
- Versao do Windows: 10.0.26200
- Python: 3.13.2

Dependencias do nucleo por sockets:

- nenhuma dependencia externa; usa apenas a biblioteca padrao do Python.

Dependencias opcionais do prototipo QR:

- estao listadas em `requirements.txt`;
- o Dockerfile ja instala a biblioteca `libzbar0` necessaria para o leitor QR.

## Como executar

Abra um terminal na pasta `Trabalho2/Parte2` antes de rodar os comandos.

Gerenciador:

```sh
python -m smartroom.manager.gerenciador
```

Gerenciador com modo manual e modo demo:

```sh
python -m smartroom.manager.gerenciador --manual --demo
```

Atuadores, cada um em um terminal separado:

```sh
python -m smartroom.actuators.atuador_iluminacao
```

```sh
python -m smartroom.actuators.atuador_projetor
```

```sh
python -m smartroom.actuators.atuador_ar_condicionado
```

Sensores, cada um em um terminal separado:

```sh
python -m smartroom.sensors.sensor_presenca
```

```sh
python -m smartroom.sensors.chave_projetor
```

```sh
python -m smartroom.sensors.leitor_cartao
```

Cliente/professor:

```sh
python -m smartroom.client.cliente_professor
```

## Ordem recomendada

1. Iniciar o Gerenciador com `--manual --demo`.
2. Iniciar os tres atuadores.
3. Iniciar o sensor de presenca.
4. Enviar presenca detectada pelo sensor.
5. Iniciar a chave do projetor.
6. Ligar e desligar a chave do projetor.
7. Iniciar o leitor de cartao.
8. Enviar os 3 alunos de demonstracao.
9. Iniciar o cliente/professor.
10. Solicitar a lista de presenca.
11. Enviar sala vazia pelo sensor de presenca.
12. Aguardar o desligamento por ausencia em modo demo.
13. Usar `shutdown` no Gerenciador ou aguardar o desligamento geral demo.

## Modo manual do Gerenciador

Com `--manual`, o terminal do Gerenciador aceita:

```text
list
light on
light off
projector on
projector off
ac on
ac off
shutdown
quit
```

Esses comandos sao uteis para testar os atuadores antes ou durante a
demonstracao.

## Modo demo

Com `--demo`:

- ausencia prolongada usa 15 segundos no lugar de 15 minutos;
- desligamento geral das 23h e simulado 20 segundos apos o inicio do
  Gerenciador.

O modo demo nao muda o protocolo. Ele altera apenas os tempos para facilitar a
gravacao.

## Roteiro de demonstracao

O roteiro curto de apresentacao esta em
[`smartroom/docs/demonstracao.md`](smartroom/docs/demonstracao.md).

## Prototipo QR opcional

O scanner de QR Code atual continua disponivel em `app/`.

Para executar:

```sh
docker compose up --build
```

Acesse:

```sh
localhost:8000
```

O QR pode conter um JSON como:

```json
{
  "student_number": "001",
  "student_name": "Aluno 1"
}
```

Esse fluxo e opcional. A demonstracao principal pode ser feita inteiramente pelo
leitor de cartao via terminal.
