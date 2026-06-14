"""Processo do sensor de presenca."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from smartroom.components.base_client import ClienteComponenteTCP, criar_parser_conexao  # noqa: E402
from smartroom.protocol.constants import (  # noqa: E402
    MESSAGE_ACK,
    MESSAGE_ERROR,
    MESSAGE_PRESENCE_UPDATE,
    ROLE_PRESENCE_SENSOR,
    SENSOR_PRESENCE_ID,
    SOURCE_TYPE_SENSOR,
)
from smartroom.protocol.socket_utils import ConnectionClosed, ProtocolSocketError  # noqa: E402


class SensorPresenca:
    """Sensor de presenca com simulacao por terminal."""

    def __init__(self, host: str, port: int):
        self.cliente = ClienteComponenteTCP(
            host=host,
            port=port,
            source_id=SENSOR_PRESENCE_ID,
            source_type=SOURCE_TYPE_SENSOR,
            component_role=ROLE_PRESENCE_SENSOR,
            log_prefix=SENSOR_PRESENCE_ID,
        )

    def executar(self) -> None:
        """Conecta ao Gerenciador e inicia o menu de simulacao."""

        try:
            self.cliente.conectar()
            self.menu()
        except KeyboardInterrupt:
            self.cliente.log("Encerrando por interrupcao do usuario")
        except (OSError, ProtocolSocketError, RuntimeError) as exc:
            self.cliente.log(f"Erro no sensor de presenca: {exc}")
        finally:
            self.cliente.fechar()

    def menu(self) -> None:
        """Exibe menu para enviar atualizacoes de presenca."""

        while True:
            print()
            print("Sensor de presenca")
            print("1 - Enviar presenca detectada")
            print("2 - Enviar sala vazia")
            print("0 - Sair")
            choice = input("> ").strip()

            if choice == "1":
                self.enviar_presenca(True)
            elif choice == "2":
                self.enviar_presenca(False)
            elif choice == "0":
                return
            else:
                self.cliente.log("Opcao invalida")

    def enviar_presenca(self, presence_detected: bool) -> None:
        """Envia PRESENCE_UPDATE ao Gerenciador."""

        message = self.cliente.criar_mensagem(
            message_type=MESSAGE_PRESENCE_UPDATE,
            payload={"presence_detected": presence_detected},
        )
        self.cliente.enviar(message)
        self.receber_confirmacao()

    def receber_confirmacao(self) -> None:
        """Aguarda ACK ou ERROR do Gerenciador apos uma atualizacao."""

        try:
            response = self.cliente.receber()
        except ConnectionClosed:
            self.cliente.log("Conexao encerrada pelo Gerenciador")
            return

        if response["message_type"] == MESSAGE_ACK:
            self.cliente.log(f"Atualizacao confirmada: {response['payload']}")
            return

        if response["message_type"] == MESSAGE_ERROR:
            self.cliente.log(f"ERROR recebido do Gerenciador: {response['payload']}")
            return

        self.cliente.log(f"Resposta inesperada do Gerenciador: {response['message_type']}")


def main() -> None:
    parser = criar_parser_conexao("Sensor de presenca SMARTROOM/1.0")
    args = parser.parse_args()
    sensor = SensorPresenca(host=args.host, port=args.port)
    sensor.executar()


if __name__ == "__main__":
    main()
