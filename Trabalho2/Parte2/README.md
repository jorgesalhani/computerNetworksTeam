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
- Gerenciador TCP minimo com registro `HELLO`/`ACK`.

Os processos executaveis dos sensores, atuadores e cliente serao adicionados nos
proximos blocos.

## Executar Gerenciador

A partir da pasta `Trabalho2/Parte2`, execute:

```sh
python -m smartroom.manager.gerenciador
```

Tambem e possivel configurar host e porta:

```sh
python -m smartroom.manager.gerenciador --host 127.0.0.1 --port 5050
```

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
