"""Base comum para atuadores SMARTROOM/1.0."""

from __future__ import annotations

from typing import Any

from smartroom.components.base_client import ClienteComponenteTCP, criar_parser_conexao
from smartroom.protocol.constants import (
    MANAGER_ID,
    MESSAGE_ACTUATOR_COMMAND,
    MESSAGE_ERROR,
    SOURCE_TYPE_ACTUATOR,
)
from smartroom.protocol.socket_utils import ProtocolSocketError

COMMAND_ON = "ON"
COMMAND_OFF = "OFF"


class AtuadorSmartRoom:
    """Atuador com estado interno ON/OFF controlado pelo Gerenciador."""

    def __init__(
        self,
        host: str,
        port: int,
        actuator_id: str,
        component_role: str,
        display_name: str,
    ):
        self.actuator_id = actuator_id
        self.component_role = component_role
        self.display_name = display_name
        self.state = COMMAND_OFF
        self.cliente = ClienteComponenteTCP(
            host=host,
            port=port,
            source_id=actuator_id,
            source_type=SOURCE_TYPE_ACTUATOR,
            component_role=component_role,
            log_prefix=actuator_id,
        )

    def executar(self) -> None:
        """Conecta ao Gerenciador e aguarda comandos."""

        try:
            self.cliente.conectar()
            self.cliente.log(f"{self.display_name} iniciado com estado {self.state}")
            self.cliente.escutar(self.processar_mensagem)
        except KeyboardInterrupt:
            self.cliente.log("Encerrando por interrupcao do usuario")
        except (OSError, ProtocolSocketError, RuntimeError) as exc:
            self.cliente.log(f"Erro no atuador: {exc}")
        finally:
            self.cliente.fechar()

    def processar_mensagem(self, message: dict[str, Any]) -> None:
        """Processa mensagens recebidas do Gerenciador."""

        message_type = message["message_type"]

        if message_type == MESSAGE_ACTUATOR_COMMAND:
            self.processar_comando(message["payload"])
            return

        if message_type == MESSAGE_ERROR:
            self.cliente.log(f"ERROR recebido do Gerenciador: {message['payload']}")
            return

        self.cliente.log(f"Mensagem ignorada pelo atuador: {message_type}")
        self.cliente.enviar_erro(
            error_code="UNSUPPORTED_MESSAGE",
            details=f"Atuador nao processa mensagem {message_type}",
        )

    def processar_comando(self, payload: dict[str, Any]) -> None:
        """Aplica comando ON/OFF recebido em ACTUATOR_COMMAND."""

        actuator_id = payload.get("actuator_id")
        command = payload.get("command")
        reason = payload.get("reason", "sem_motivo")

        if actuator_id != self.actuator_id:
            self.cliente.log(f"Comando ignorado: destino {actuator_id!r}")
            return

        if command not in {COMMAND_ON, COMMAND_OFF}:
            self.cliente.enviar_erro(
                error_code="INVALID_COMMAND",
                details=f"Comando invalido para {self.actuator_id}: {command!r}",
            )
            return

        previous_state = self.state
        self.state = command
        self.cliente.log(
            f"{self.display_name}: {previous_state} -> {self.state} "
            f"(motivo: {reason})"
        )
        self.cliente.enviar_ack(
            status="command_applied",
            payload={
                "actuator_id": self.actuator_id,
                "state": self.state,
                "reason": reason,
            },
        )


def executar_atuador(actuator_id: str, component_role: str, display_name: str) -> None:
    """Executa um atuador configurado por linha de comando."""

    parser = criar_parser_conexao(f"Atuador SMARTROOM/1.0 - {display_name}")
    args = parser.parse_args()
    atuador = AtuadorSmartRoom(
        host=args.host,
        port=args.port,
        actuator_id=actuator_id,
        component_role=component_role,
        display_name=display_name,
    )
    atuador.executar()
