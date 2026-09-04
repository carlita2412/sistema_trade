# -*- coding: utf-8 -*-
"""
Ciclo de refresco para la tarea programada en Lightsail: refresca datos,
calcula el estado, lo guarda y dispara alertas de Telegram si corresponde.

Pensado para ejecutarse repetidamente (cada 15 min) vía el Programador de
tareas de Windows — ver deploy/windows/README_DEPLOY_WINDOWS.md.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import engine  # noqa: E402
import alertas_telegram  # noqa: E402


def main():
    engine.load_dotenv()
    state, state_path = engine.refresh_and_save(log=print)
    print(f"Estado: {state.get('status')} -> {state_path}")
    alertas_telegram.check_and_notify(state)


if __name__ == "__main__":
    main()
