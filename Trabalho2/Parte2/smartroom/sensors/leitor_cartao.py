"""Processo do leitor de cartao dos alunos."""

from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from smartroom.components.base_client import ClienteComponenteTCP, criar_parser_conexao  # noqa: E402
from smartroom.protocol.constants import (  # noqa: E402
    MESSAGE_ACK,
    MESSAGE_ERROR,
    MESSAGE_STUDENT_CHECKIN,
    ROLE_CARD_READER,
    SENSOR_CARD_READER_ID,
    SOURCE_TYPE_SENSOR,
)
from smartroom.protocol.socket_utils import ConnectionClosed, ProtocolSocketError  # noqa: E402

DEMO_STUDENTS = [
    {"student_number": "001", "student_name": "Aluno 1"},
    {"student_number": "002", "student_name": "Aluno 2"},
    {"student_number": "003", "student_name": "Aluno 3"},
]


class LeitorCartao:
    """Leitor de cartao com simulacao por terminal."""

    def __init__(self, host: str, port: int):
        self.cliente = ClienteComponenteTCP(
            host=host,
            port=port,
            source_id=SENSOR_CARD_READER_ID,
            source_type=SOURCE_TYPE_SENSOR,
            component_role=ROLE_CARD_READER,
            log_prefix=SENSOR_CARD_READER_ID,
        )

    def executar(self) -> None:
        """Conecta ao Gerenciador e inicia o menu do leitor."""

        try:
            self.cliente.conectar()
            self.menu()
        except KeyboardInterrupt:
            self.cliente.log("Encerrando por interrupcao do usuario")
        except (OSError, ProtocolSocketError, RuntimeError) as exc:
            self.cliente.log(f"Erro no leitor de cartao: {exc}")
        finally:
            self.cliente.fechar()

    def menu(self) -> None:
        """Exibe menu para registrar alunos."""

        while True:
            print()
            print("Leitor de cartao")
            print("1 - Registrar aluno manualmente")
            print("2 - Enviar 3 alunos de demonstracao")
            print("3 - Registrar aluno a partir de JSON")
            print("0 - Sair")
            choice = input("> ").strip()

            if choice == "1":
                self.registrar_manual()
            elif choice == "2":
                self.enviar_alunos_demo()
            elif choice == "3":
                self.registrar_json()
            elif choice == "0":
                return
            else:
                self.cliente.log("Opcao invalida")

    def registrar_manual(self) -> None:
        """Le aluno por terminal e envia STUDENT_CHECKIN."""

        student_number = input("Numero do aluno: ").strip()
        student_name = input("Nome do aluno: ").strip()
        self.enviar_checkin(student_number=student_number, student_name=student_name)

    def enviar_alunos_demo(self) -> None:
        """Envia tres alunos para a demonstracao minima."""

        for student in DEMO_STUDENTS:
            self.enviar_checkin(
                student_number=student["student_number"],
                student_name=student["student_name"],
            )

    def registrar_json(self) -> None:
        """Le um JSON simples no formato usado pelo QR opcional."""

        raw_data = input("JSON do aluno: ").strip()
        try:
            student_data = json.loads(raw_data)
        except json.JSONDecodeError as exc:
            self.cliente.log(f"JSON invalido: {exc}")
            return

        self.enviar_checkin(
            student_number=student_data.get("student_number", ""),
            student_name=student_data.get("student_name", ""),
        )

    def enviar_checkin(self, student_number: str, student_name: str) -> None:
        """Envia STUDENT_CHECKIN ao Gerenciador."""

        message = self.cliente.criar_mensagem(
            message_type=MESSAGE_STUDENT_CHECKIN,
            payload={
                "student_number": student_number,
                "student_name": student_name,
            },
        )
        self.cliente.enviar(message)
        self.receber_confirmacao()

    def receber_confirmacao(self) -> None:
        """Aguarda ACK ou ERROR do Gerenciador apos check-in."""

        try:
            response = self.cliente.receber()
        except ConnectionClosed:
            self.cliente.log("Conexao encerrada pelo Gerenciador")
            return

        if response["message_type"] == MESSAGE_ACK:
            self.cliente.log(f"Check-in confirmado: {response['payload']}")
            return

        if response["message_type"] == MESSAGE_ERROR:
            self.cliente.log(f"ERROR recebido do Gerenciador: {response['payload']}")
            return

        self.cliente.log(f"Resposta inesperada do Gerenciador: {response['message_type']}")


def main() -> None:
    parser = criar_parser_conexao("Leitor de cartao SMARTROOM/1.0")
    args = parser.parse_args()
    leitor = LeitorCartao(host=args.host, port=args.port)
    leitor.executar()


if __name__ == "__main__":
    main()
