# Sensores

Os sensores se conectam ao Gerenciador por socket TCP e se identificam com uma
mensagem `HELLO` do protocolo `SMARTROOM/1.0`.

Toda mensagem usa o header comum:

```json
{
  "protocol_id": "SMARTROOM/1.0",
  "message_type": "...",
  "source_id": "...",
  "source_type": "SENSOR",
  "target_id": "MANAGER",
  "timestamp": "...",
  "payload": {}
}
```

## Sensor de presenca

Envia `PRESENCE_UPDATE` com:

```json
{
  "presence_detected": true
}
```

ou:

```json
{
  "presence_detected": false
}
```

## Leitor de cartao

Envia `STUDENT_CHECKIN` com:

```json
{
  "student_number": "001",
  "student_name": "Aluno 1"
}
```

## Chave ON/OFF do projetor

Envia `PROJECTOR_SWITCH` com:

```json
{
  "projector_switch_on": true
}
```

ou:

```json
{
  "projector_switch_on": false
}
```
