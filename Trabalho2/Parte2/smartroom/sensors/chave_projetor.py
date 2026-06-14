"""Processo da chave ON/OFF do projetor."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from smartroom.components.base_client import ClienteComponenteTCP, criar_parser_conexao  # noqa: E402
from smartroom.protocol.constants import (  # noqa: E402
    MESSAGE_ACK,
    MESSAGE_ERROR,
    MESSAGE_PROJECTOR_SWITCH,
    ROLE_PROJECTOR_SWITCH,
    SENSOR_PROJECTOR_SWITCH_ID,
    SOURCE_TYPE_SENSOR,
)
from smartroom.protocol.socket_utils import ConnectionClosed, ProtocolSocketError  # noqa: E402


class ChaveProjetor:
    """Chave ON/OFF do projetor com simulacao por terminal."""

    def __init__(self, host: str, port: int):
        self.cliente = ClienteComponenteTCP(
            host=host,
            port=port,
            source_id=SENSOR_PROJECTOR_SWITCH_ID,
            source_type=SOURCE_TYPE_SENSOR,
            component_role=ROLE_PROJECTOR_SWITCH,
            log_prefix=SENSOR_PROJECTOR_SWITCH_ID,
        )

    def executar(self) -> None:
        """Conecta ao Gerenciador e inicia o menu da chave."""

        try:
            self.cliente.conectar()
            self.menu()
        except KeyboardInterrupt:
            self.cliente.log("Encerrando por interrupcao do usuario")
        except (OSError, ProtocolSocketError, RuntimeError) as exc:
            self.cliente.log(f"Erro na chave do projetor: {exc}")
        finally:
            self.cliente.fechar()

    def menu(self) -> None:
        """Exibe menu para alternar a chave do projetor."""

        while True:
            print()
            print("Chave do projetor")
            print("1 - Ligar chave do projetor")
            print("2 - Desligar chave do projetor")
            print("0 - Sair")
            choice = input("> ").strip()

            if choice == "1":
                self.enviar_estado(True)
            elif choice == "2":
                self.enviar_estado(False)
            elif choice == "0":
                return
            else:
                self.cliente.log("Opcao invalida")

    def enviar_estado(self, projector_switch_on: bool) -> None:
        """Envia PROJECTOR_SWITCH ao Gerenciador."""

        message = self.cliente.criar_mensagem(
            message_type=MESSAGE_PROJECTOR_SWITCH,
            payload={"projector_switch_on": projector_switch_on},
        )
        self.cliente.enviar(message)
        self.receber_confirmacao()

    def receber_confirmacao(self) -> None:
        """Aguarda ACK ou ERROR do Gerenciador apos alternar a chave."""

        try:
            response = self.cliente.receber()
        except ConnectionClosed:
            self.cliente.log("Conexao encerrada pelo Gerenciador")
            return

        if response["message_type"] == MESSAGE_ACK:
            self.cliente.log(f"Alteracao confirmada: {response['payload']}")
            return

        if response["message_type"] == MESSAGE_ERROR:
            self.cliente.log(f"ERROR recebido do Gerenciador: {response['payload']}")
            return

        self.cliente.log(f"Resposta inesperada do Gerenciador: {response['message_type']}")


def main() -> None:
    parser = criar_parser_conexao("Chave do projetor SMARTROOM/1.0")
    args = parser.parse_args()
    chave = ChaveProjetor(host=args.host, port=args.port)
    chave.executar()


if __name__ == "__main__":
    main()
