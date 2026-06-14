# Gerenciador

O Gerenciador e o servidor principal da aplicacao Sala de Aula Inteligente. A
implementacao da Parte 2 deve usar o protocolo `SMARTROOM/1.0`, documentado em
[`../../Parte2/smartroom/docs/protocolo.md`](../../Parte2/smartroom/docs/protocolo.md).

As mensagens nao usam mais o modelo antigo `HEADER | DATA` com `id_sensor`,
`tipo_componente` ou `aceitar_sinal`. O header atual usa:

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

## Armazenamento interno

O arquivo [`db.wsd`](db.wsd) representa o armazenamento interno do Gerenciador
para a lista de presenca. Ele nao exige um banco de dados real.

## Requisitos funcionais

Os diagramas fonte atualizados estao em `RequisitosFuncionais/`:

1. [`3.1.wsd`](RequisitosFuncionais/3.1.wsd): aceitar conexao de componente com `HELLO`, `ACK` e `ERROR`.
2. [`3.2.wsd`](RequisitosFuncionais/3.2.wsd): ligar iluminacao e ar-condicionado com `PRESENCE_UPDATE` e `ACTUATOR_COMMAND`.
3. [`3.3.wsd`](RequisitosFuncionais/3.3.wsd): desligar equipamentos apos ausencia prolongada.
4. [`3.4.wsd`](RequisitosFuncionais/3.4.wsd): apagar luzes e ligar projetor com `PROJECTOR_SWITCH`.
5. [`3.5.wsd`](RequisitosFuncionais/3.5.wsd): acender luzes e desligar projetor com `PROJECTOR_SWITCH`.
6. [`3.6.wsd`](RequisitosFuncionais/3.6.wsd): registrar presenca de aluno com `STUDENT_CHECKIN`.
7. [`3.7.wsd`](RequisitosFuncionais/3.7.wsd): desligamento geral as 23h.
8. [`3.8.wsd`](RequisitosFuncionais/3.8.wsd): consulta de presenca com `ATTENDANCE_REQUEST` e `ATTENDANCE_RESPONSE`.

As imagens em `RequisitosFuncionais/Images/` podem ser regeneradas a partir dos
arquivos `.wsd` quando a documentacao visual final for montada.
