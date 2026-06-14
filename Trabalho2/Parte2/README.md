## Sala de aula inteligente - Parte 2

Esta parte do trabalho esta organizada em dois blocos:

1. `smartroom/`: implementacao principal do protocolo de aplicacao via sockets
   TCP, usando mensagens JSON delimitadas por quebra de linha.
2. `app/`: prototipo FastAPI de leitura de QR Code. Ele fica preservado como
   apoio opcional ao leitor de cartao, mas nao e dependencia do fluxo principal
   exigido pelo trabalho.

## Protocolo

O protocolo padronizado e `SMARTROOM/1.0`. Toda mensagem tem o header:

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

A documentacao completa esta em
[`smartroom/docs/protocolo.md`](smartroom/docs/protocolo.md).

## Diagramas .wsd

Os arquivos `.wsd` da Parte 1 continuam sendo documentacao de fluxo e regra de
negocio. Eles nao devem ser implementados como nomes literais de mensagem.

A implementacao deve usar sempre as mensagens tecnicas do protocolo
`SMARTROOM/1.0`: `HELLO`, `ACK`, `ERROR`, `PRESENCE_UPDATE`,
`STUDENT_CHECKIN`, `PROJECTOR_SWITCH`, `ACTUATOR_COMMAND`,
`ATTENDANCE_REQUEST` e `ATTENDANCE_RESPONSE`.

O mapeamento entre os nomes conceituais dos diagramas e as mensagens reais esta
descrito em [`smartroom/docs/protocolo.md`](smartroom/docs/protocolo.md).

## Estado atual da implementacao

Blocos criados:

- constantes do protocolo;
- construcao e validacao de mensagens;
- envio e recebimento de JSON por TCP com delimitador `\n`;
- documentacao do protocolo;
- Gerenciador TCP minimo com registro `HELLO`/`ACK`;
- atuadores de iluminacao, projetor e ar-condicionado conectando via sockets.
- sensor de presenca enviando `PRESENCE_UPDATE`;
- regra de presenca detectada ligando iluminacao e ar-condicionado;
- regra de ausencia prolongada desligando iluminacao, projetor e
  ar-condicionado.
- chave ON/OFF do projetor controlando iluminacao e projetor.

Os processos executaveis do leitor de cartao e cliente/professor serao
adicionados nos proximos blocos.

## Executar processos atuais

A partir da pasta `Trabalho2/Parte2`, execute:

```sh
python -m smartroom.manager.gerenciador
```

Tambem e possivel configurar host e porta:

```sh
python -m smartroom.manager.gerenciador --host 127.0.0.1 --port 5050
```

Para testar comandos `ON/OFF` antes dos sensores estarem prontos, use o modo
manual:

```sh
python -m smartroom.manager.gerenciador --manual
```

Para demonstracao, use o modo demo. Nele, a ausencia prolongada usa 15 segundos
em vez de 15 minutos:

```sh
python -m smartroom.manager.gerenciador --demo
```

Os modos podem ser combinados:

```sh
python -m smartroom.manager.gerenciador --manual --demo
```

Com o modo manual ativo, o terminal do Gerenciador aceita:

```text
list
light on
light off
projector on
projector off
ac on
ac off
quit
```

Em outros terminais, execute os atuadores:

```sh
python -m smartroom.actuators.atuador_iluminacao
```

```sh
python -m smartroom.actuators.atuador_projetor
```

```sh
python -m smartroom.actuators.atuador_ar_condicionado
```

Cada atuador envia `HELLO`, recebe `ACK` e fica aguardando `ACTUATOR_COMMAND`.
O modo manual do Gerenciador permite enviar `ACTUATOR_COMMAND` para testar os
estados `ON/OFF`. O envio automatico sera implementado junto com as regras dos
sensores nos proximos blocos.

Para testar a regra inicial de presenca, mantenha o Gerenciador, o atuador de
iluminacao e o atuador do ar-condicionado em execucao. Em outro terminal, rode:

```sh
python -m smartroom.sensors.sensor_presenca
```

No menu do sensor, escolha:

```text
1 - Enviar presenca detectada
```

O Gerenciador deve enviar `ACTUATOR_COMMAND` com `command=ON` para
`ACT_LIGHT_01` e `ACT_AC_01`.

Para testar ausencia prolongada em modo demo, rode o Gerenciador com `--demo` e
escolha no sensor:

```text
2 - Enviar sala vazia
```

Apos 15 segundos sem nova presenca, o Gerenciador deve enviar
`ACTUATOR_COMMAND` com `command=OFF` para `ACT_LIGHT_01`, `ACT_PROJECTOR_01` e
`ACT_AC_01`.

Para testar a chave do projetor, mantenha o Gerenciador, o atuador de
iluminacao e o atuador do projetor em execucao. Em outro terminal, rode:

```sh
python -m smartroom.sensors.chave_projetor
```

No menu da chave, escolha:

```text
1 - Ligar chave do projetor
```

O Gerenciador deve apagar a iluminacao (`ACT_LIGHT_01 OFF`) e ligar o projetor
(`ACT_PROJECTOR_01 ON`).

Depois escolha:

```text
2 - Desligar chave do projetor
```

O Gerenciador deve ligar a iluminacao (`ACT_LIGHT_01 ON`) e desligar o projetor
(`ACT_PROJECTOR_01 OFF`).

## Prototipo QR opcional

O scanner de QR Code atual continua disponivel:

1. Ter Docker Desktop instalado.
2. Subir o servico:

```sh
docker compose up --build
```

3. Acessar:

```sh
localhost:8000
```

4. Exibir QR e pressionar "scan".
