# Protocolo SMARTROOM/1.0

Este documento define o protocolo de camada de aplicacao da Sala de Aula Inteligente. A comunicacao usa TCP com uma mensagem JSON por linha. Cada envio termina com `\n`, o que simplifica leitura, logs e depuracao.

## Estrutura base

```json
{
  "protocol_id": "SMARTROOM/1.0",
  "message_type": "HELLO",
  "source_id": "SENSOR_PRESENCE_01",
  "source_type": "SENSOR",
  "target_id": "MANAGER",
  "timestamp": "2026-06-14T20:00:00",
  "payload": {}
}
```

O campo `protocol_id` identifica o protocolo usado na comunicacao e deve ter
sempre o valor `SMARTROOM/1.0`.

O campo `message_type` informa o tipo da mensagem enviada, como `HELLO`,
`ACK`, `PRESENCE_UPDATE` ou `ACTUATOR_COMMAND`.

O campo `source_id` contem o identificador unico do componente que enviou a
mensagem.

O campo `source_type` indica o tipo do componente de origem. Os valores validos
sao `SENSOR`, `ACTUATOR`, `MANAGER` e `CLIENT`.

O campo `target_id` indica o destinatario logico da mensagem, como `MANAGER`,
`ACT_LIGHT_01`, `ACT_PROJECTOR_01`, `ACT_AC_01` ou `CLIENT_TEACHER`.

O campo `timestamp` registra a data e hora local do envio no formato ISO-8601.

O campo `payload` e um objeto JSON com os dados especificos de cada tipo de
mensagem.

## Tipos de mensagem

### HELLO

Usada por qualquer componente ao conectar no Gerenciador.

```json
{
  "protocol_id": "SMARTROOM/1.0",
  "message_type": "HELLO",
  "source_id": "SENSOR_PRESENCE_01",
  "source_type": "SENSOR",
  "target_id": "MANAGER",
  "timestamp": "2026-06-14T20:00:00",
  "payload": {
    "component_role": "PRESENCE_SENSOR"
  }
}
```

### ACK

Confirma registro ou recebimento de comando.

```json
{
  "protocol_id": "SMARTROOM/1.0",
  "message_type": "ACK",
  "source_id": "MANAGER",
  "source_type": "MANAGER",
  "target_id": "SENSOR_PRESENCE_01",
  "timestamp": "2026-06-14T20:00:01",
  "payload": {
    "status": "registered"
  }
}
```

### PRESENCE_UPDATE

Enviada pelo sensor de presenca.

```json
{
  "presence_detected": true
}
```

Regra: `true` liga iluminacao e ar-condicionado. `false` inicia ou mantem o
controle de ausencia. No modo normal, 15 minutos sem presenca desligam
iluminacao, projetor e ar-condicionado. No modo demo, esse tempo sera reduzido
para 15 segundos.

### STUDENT_CHECKIN

Enviada pelo leitor de cartao.

```json
{
  "student_number": "14687681",
  "student_name": "Nome do Aluno"
}
```

Regra: o Gerenciador salva o aluno na lista de presenca e evita duplicidade pelo
numero do aluno. O horario do check-in pode ser armazenado internamente pelo
Gerenciador como `checkin_timestamp`, usando o `timestamp` da propria mensagem.

### PROJECTOR_SWITCH

Enviada pela chave ON/OFF do projetor.

```json
{
  "projector_switch_on": true
}
```

Regra: `true` apaga as luzes e liga o projetor. `false` liga as luzes e desliga
o projetor.

### ACTUATOR_COMMAND

Enviada pelo Gerenciador para atuadores.

```json
{
  "actuator_id": "ACT_LIGHT_01",
  "command": "ON",
  "reason": "presence_detected"
}
```

Os atuadores obrigatorios sao o sistema de iluminacao, identificado por
`ACT_LIGHT_01`; o alimentador do projetor, identificado por `ACT_PROJECTOR_01`;
e o alimentador do ar-condicionado, identificado por `ACT_AC_01`.

### ATTENDANCE_REQUEST

Enviada pelo cliente/professor para solicitar a lista de presenca.

```json
{}
```

### ATTENDANCE_RESPONSE

Enviada pelo Gerenciador ao cliente/professor.

```json
{
  "students": [
    {
      "student_number": "001",
      "student_name": "Aluno 1"
    },
    {
      "student_number": "002",
      "student_name": "Aluno 2"
    },
    {
      "student_number": "003",
      "student_name": "Aluno 3"
    }
  ]
}
```

### ERROR

Enviada quando uma mensagem invalida for recebida.

```json
{
  "error_code": "INVALID_MESSAGE",
  "details": "Descricao objetiva do erro"
}
```

## Mapeamento dos requisitos

Os componentes se conectam e se identificam enviando `HELLO`; o Gerenciador
confirma o registro com `ACK`.

A deteccao de pessoas e enviada por `PRESENCE_UPDATE` com
`presence_detected=true`. Ao receber essa mensagem, o Gerenciador liga a
iluminacao e o ar-condicionado.

A ausencia e enviada por `PRESENCE_UPDATE` com `presence_detected=false`. A
partir desse estado, o Gerenciador controla o temporizador de ausencia e desliga
iluminacao, projetor e ar-condicionado quando o limite e atingido.

A chave do projetor ligada e representada por `PROJECTOR_SWITCH` com
`projector_switch_on=true`. Essa mensagem faz o Gerenciador apagar as luzes e
ligar o projetor.

A chave do projetor desligada e representada por `PROJECTOR_SWITCH` com
`projector_switch_on=false`. Essa mensagem faz o Gerenciador ligar as luzes e
desligar o projetor.

O registro de alunos e feito por `STUDENT_CHECKIN`, contendo numero e nome do
aluno.

A consulta do professor usa `ATTENDANCE_REQUEST`, e a resposta do Gerenciador
usa `ATTENDANCE_RESPONSE`.

O desligamento geral as 23h e uma regra periodica executada pelo Gerenciador.

Os comandos enviados aos atuadores usam `ACTUATOR_COMMAND`, com o identificador
do atuador, o comando `ON` ou `OFF` e o motivo da acao.

## Relacao entre os diagramas .wsd e o protocolo SMARTROOM/1.0

Os diagramas `.wsd` da Parte 1 devem ser lidos como documentacao dos fluxos e
das regras de negocio. Eles ajudam a visualizar os cenarios esperados, mas nao
sao o contrato tecnico literal da implementacao.

O contrato tecnico da implementacao e o protocolo `SMARTROOM/1.0`, usando JSON
delimitado por quebra de linha sobre sockets TCP.

O fluxo conceitual `connect()` corresponde ao envio de `HELLO` pelo componente
e ao retorno de `ACK` pelo Gerenciador.

O fluxo conceitual `people_arrive()` corresponde a `PRESENCE_UPDATE` com
`payload.presence_detected=true`.

O fluxo conceitual `no_people_here()` corresponde a `PRESENCE_UPDATE` com
`payload.presence_detected=false`.

O fluxo conceitual `movie_mode()` corresponde a `PROJECTOR_SWITCH` com
`payload.projector_switch_on=true`.

O fluxo conceitual `movie_mode_off()` corresponde a `PROJECTOR_SWITCH` com
`payload.projector_switch_on=false`.

O fluxo conceitual `attend_list()` corresponde a `STUDENT_CHECKIN`.

O fluxo conceitual `check_attend_list()` corresponde a `ATTENDANCE_REQUEST`.

A resposta da lista de presenca corresponde a `ATTENDANCE_RESPONSE`.

Os fluxos conceituais `lights_on()`, `lights_off()`, `projector_on()`,
`projector_off()`, `air_cond_on()` e `air_cond_off()` correspondem a
`ACTUATOR_COMMAND`, variando os campos `actuator_id`, `command` e `reason`.

## Observacoes sobre os diagramas .wsd

Alguns titulos ou nomes internos dos diagramas podem ter sido herdados de
rascunhos. Na implementacao, devem ser usados os nomes formais do protocolo
`SMARTROOM/1.0`.

O arquivo `3.3.wsd` representa a regra de ausencia prolongada. A logica correta
do temporizador deve ser interpretada como:

```text
now() - absence_started_at >= 15min
```

No modo demo, o mesmo criterio sera aplicado usando 15 segundos no lugar de 15
minutos.

O arquivo `3.8.wsd` representa a consulta da lista de presenca. A implementacao
final deve garantir que o Gerenciador responda ao Cliente/professor com
`ATTENDANCE_RESPONSE`.

O arquivo `db.wsd` representa o armazenamento conceitual da lista de presenca.
Ele nao obriga a implementacao de um banco de dados real; uma estrutura em
memoria no Gerenciador atende ao escopo da demonstracao.

Nomes informais que aparecam em rascunhos, como `midnight_gospel()`, devem ser
entendidos apenas como nomes conceituais. Na documentacao e no codigo da
implementacao, devem ser usados nomes formais como `scheduled_shutdown` ou
`shutdown_all_at_23h`.

## Fluxo minimo de demonstracao

1. Gerenciador inicia o servidor TCP.
2. Atuadores conectam e enviam `HELLO`.
3. Sensores conectam e enviam `HELLO`.
4. Sensor de presenca envia `PRESENCE_UPDATE=true`.
5. Gerenciador envia `ACTUATOR_COMMAND=ON` para luz e ar-condicionado.
6. Chave do projetor envia `PROJECTOR_SWITCH=true`.
7. Gerenciador desliga luz e liga projetor.
8. Leitor de cartao envia tres `STUDENT_CHECKIN`.
9. Cliente/professor envia `ATTENDANCE_REQUEST`.
10. Gerenciador responde com `ATTENDANCE_RESPONSE`.
