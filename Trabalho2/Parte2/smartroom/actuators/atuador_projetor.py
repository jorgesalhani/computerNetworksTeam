"""Processo do atuador do projetor."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from smartroom.actuators.base_actuator import executar_atuador  # noqa: E402
from smartroom.protocol.constants import ACT_PROJECTOR_ID, ROLE_PROJECTOR_ACTUATOR  # noqa: E402


def main() -> None:
    executar_atuador(
        actuator_id=ACT_PROJECTOR_ID,
        component_role=ROLE_PROJECTOR_ACTUATOR,
        display_name="Alimentador do projetor",
    )


if __name__ == "__main__":
    main()
