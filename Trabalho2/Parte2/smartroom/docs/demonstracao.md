# Roteiro de demonstracao

Este roteiro foi pensado para uma gravacao curta, com foco no protocolo
`SMARTROOM/1.0`, nos processos separados e nas mensagens trocadas por sockets
TCP.

## Preparacao

Abra terminais na pasta `Trabalho2/Parte2`.

Terminal 1 - Gerenciador:

```sh
python -m smartroom.manager.gerenciador --manual --demo
```

Terminal 2 - Iluminacao:

```sh
python -m smartroom.actuators.atuador_iluminacao
```

Terminal 3 - Projetor:

```sh
python -m smartroom.actuators.atuador_projetor
```

Terminal 4 - Ar-condicionado:

```sh
python -m smartroom.actuators.atuador_ar_condicionado
```

Terminal 5 - Sensor de presenca:

```sh
python -m smartroom.sensors.sensor_presenca
```

Terminal 6 - Chave do projetor:

```sh
python -m smartroom.sensors.chave_projetor
```

Terminal 7 - Leitor de cartao:

```sh
python -m smartroom.sensors.leitor_cartao
```

Terminal 8 - Cliente/professor:

```sh
python -m smartroom.client.cliente_professor
```

## Sequencia sugerida

1. Mostre rapidamente `smartroom/docs/protocolo.md`.

Explique que o protocolo usa JSON por TCP com `protocol_id`,
`message_type`, `source_id`, `source_type`, `target_id`, `timestamp` e
`payload`.

2. Mostre o Gerenciador aceitando conexoes.

Ao iniciar os atuadores e sensores, o Gerenciador deve registrar mensagens
`HELLO` e responder `ACK`.

3. Demonstre presenca detectada.

No terminal do sensor de presenca, escolha:

```text
1 - Enviar presenca detectada
```

Resultado esperado:

- Gerenciador recebe `PRESENCE_UPDATE`;
- Gerenciador envia `ACTUATOR_COMMAND ON` para `ACT_LIGHT_01`;
- Gerenciador envia `ACTUATOR_COMMAND ON` para `ACT_AC_01`;
- iluminacao e ar-condicionado imprimem mudanca de estado para `ON`.

4. Demonstre chave do projetor ligada.

No terminal da chave do projetor, escolha:

```text
1 - Ligar chave do projetor
```

Resultado esperado:

- Gerenciador recebe `PROJECTOR_SWITCH`;
- iluminacao recebe `OFF`;
- projetor recebe `ON`.

5. Demonstre chave do projetor desligada.

No terminal da chave do projetor, escolha:

```text
2 - Desligar chave do projetor
```

Resultado esperado:

- iluminacao recebe `ON`;
- projetor recebe `OFF`.

6. Registre tres alunos.

No terminal do leitor de cartao, escolha:

```text
2 - Enviar 3 alunos de demonstracao
```

Resultado esperado:

- Gerenciador recebe tres `STUDENT_CHECKIN`;
- alunos `001`, `002` e `003` sao registrados.

7. Consulte a lista de presenca.

No terminal do cliente/professor, escolha:

```text
1 - Solicitar lista de presenca
```

Resultado esperado:

- cliente envia `ATTENDANCE_REQUEST`;
- Gerenciador responde `ATTENDANCE_RESPONSE`;
- cliente imprime os tres alunos.

8. Demonstre ausencia prolongada.

No terminal do sensor de presenca, escolha:

```text
2 - Enviar sala vazia
```

Como o Gerenciador esta com `--demo`, aguarde 15 segundos.

Resultado esperado:

- Gerenciador envia `ACTUATOR_COMMAND OFF` para iluminacao, projetor e
  ar-condicionado com motivo `absence_timeout`.

9. Demonstre desligamento geral.

No terminal do Gerenciador, use:

```text
shutdown
```

Resultado esperado:

- Gerenciador envia `ACTUATOR_COMMAND OFF` para os tres atuadores com motivo
  `scheduled_shutdown`.

Tambem e possivel aguardar o desligamento automatico do modo demo, que ocorre
20 segundos apos o inicio do Gerenciador.

## Pontos a mostrar na gravacao

Mostre os logs do Gerenciador recebendo e enviando mensagens completas.

Mostre os terminais dos atuadores imprimindo transicoes de estado, como
`OFF -> ON` e `ON -> OFF`.

Mostre o cliente/professor imprimindo a lista final de presenca.

Finalize destacando que o QR Code ficou como apoio opcional, mas o nucleo do
trabalho roda por sockets TCP com processos separados.
