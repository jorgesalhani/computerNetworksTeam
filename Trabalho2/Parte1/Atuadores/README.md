# Atuadores

Os atuadores se conectam ao Gerenciador por socket TCP e se identificam com uma
mensagem `HELLO` do protocolo `SMARTROOM/1.0`.

Toda mensagem usa o header comum:

```json
{
  "protocol_id": "SMARTROOM/1.0",
  "message_type": "...",
  "source_id": "...",
  "source_type": "ACTUATOR",
  "target_id": "MANAGER",
  "timestamp": "...",
  "payload": {}
}
```

Depois do registro, cada atuador aguarda mensagens `ACTUATOR_COMMAND` enviadas
pelo Gerenciador.

## Sistema de iluminacao

Identificador: `ACT_LIGHT_01`.

Payload esperado em comandos:

```json
{
  "actuator_id": "ACT_LIGHT_01",
  "command": "ON",
  "reason": "presence_detected"
}
```

## Alimentador do projetor

Identificador: `ACT_PROJECTOR_01`.

Payload esperado em comandos:

```json
{
  "actuator_id": "ACT_PROJECTOR_01",
  "command": "OFF",
  "reason": "projector_switch_off"
}
```

## Alimentador do ar-condicionado

Identificador: `ACT_AC_01`.

Payload esperado em comandos:

```json
{
  "actuator_id": "ACT_AC_01",
  "command": "ON",
  "reason": "presence_detected"
}
```
