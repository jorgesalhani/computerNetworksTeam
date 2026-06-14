"""Processo do cliente/professor para consultar a lista de presenca."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from smartroom.components.base_client import ClienteComponenteTCP, criar_parser_conexao  # noqa: E402
from smartroom.protocol.constants import (  # noqa: E402
    CLIENT_TEACHER_ID,
    MESSAGE_ATTENDANCE_REQUEST,
    MESSAGE_ATTENDANCE_RESPONSE,
    MESSAGE_ERROR,
    ROLE_TEACHER_CLIENT,
    SOURCE_TYPE_CLIENT,
)
from smartroom.protocol.socket_utils import ConnectionClosed, ProtocolSocketError  # noqa: E402


class ClienteProfessor:
    """Cliente do professor para solicitar a lista de presenca."""

    def __init__(self, host: str, port: int):
        self.cliente = ClienteComponenteTCP(
            host=host,
            port=port,
            source_id=CLIENT_TEACHER_ID,
            source_type=SOURCE_TYPE_CLIENT,
            component_role=ROLE_TEACHER_CLIENT,
            log_prefix=CLIENT_TEACHER_ID,
        )

    def executar(self) -> None:
        """Conecta ao Gerenciador e inicia o menu do professor."""

        try:
            self.cliente.conectar()
            self.menu()
        except KeyboardInterrupt:
            self.cliente.log("Encerrando por interrupcao do usuario")
        except (OSError, ProtocolSocketError, RuntimeError) as exc:
            self.cliente.log(f"Erro no cliente/professor: {exc}")
        finally:
            self.cliente.fechar()

    def menu(self) -> None:
        """Exibe menu para solicitar presenca."""

        while True:
            print()
            print("Cliente/professor")
            print("1 - Solicitar lista de presenca")
            print("0 - Sair")
            choice = input("> ").strip()

            if choice == "1":
                self.solicitar_lista()
            elif choice == "0":
                return
            else:
                self.cliente.log("Opcao invalida")

    def solicitar_lista(self) -> None:
        """Envia ATTENDANCE_REQUEST e imprime ATTENDANCE_RESPONSE."""

        message = self.cliente.criar_mensagem(
            message_type=MESSAGE_ATTENDANCE_REQUEST,
            payload={},
        )
        self.cliente.enviar(message)
        self.receber_lista()

    def receber_lista(self) -> None:
        """Recebe e imprime a lista de presenca retornada pelo Gerenciador."""

        try:
            response = self.cliente.receber()
        except ConnectionClosed:
            self.cliente.log("Conexao encerrada pelo Gerenciador")
            return

        if response["message_type"] == MESSAGE_ERROR:
            self.cliente.log(f"ERROR recebido do Gerenciador: {response['payload']}")
            return

        if response["message_type"] != MESSAGE_ATTENDANCE_RESPONSE:
            self.cliente.log(f"Resposta inesperada do Gerenciador: {response['message_type']}")
            return

        students = response["payload"].get("students", [])
        print()
        print("Lista de presenca")
        if not students:
            print("Nenhum aluno registrado.")
            return

        for index, student in enumerate(students, start=1):
            print(f"{index}. {student['student_number']} - {student['student_name']}")


def main() -> None:
    parser = criar_parser_conexao("Cliente/professor SMARTROOM/1.0")
    args = parser.parse_args()
    client = ClienteProfessor(host=args.host, port=args.port)
    client.executar()


if __name__ == "__main__":
    main()
