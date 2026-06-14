"""Processo do atuador do ar-condicionado."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from smartroom.actuators.base_actuator import executar_atuador  # noqa: E402
from smartroom.protocol.constants import ACT_AC_ID, ROLE_AC_ACTUATOR  # noqa: E402


def main() -> None:
    executar_atuador(
        actuator_id=ACT_AC_ID,
        component_role=ROLE_AC_ACTUATOR,
        display_name="Alimentador do ar-condicionado",
    )


if __name__ == "__main__":
    main()
