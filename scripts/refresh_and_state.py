# -*- coding: utf-8 -*-
"""
Punto de entrada que invoca la skill /analisis-xrp.

Refresca los CSV (ccxt, best-effort) y calcula el estado completo con
compute_state() del script original del usuario, guardándolo en
perp-xrp-signals/analisis/_state.json.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import engine  # noqa: E402


def main():
    engine.load_dotenv()
    state, state_path = engine.refresh_and_save(log=print)
    print(f"\nEstado: {state.get('status')}")
    print(f"Guardado en: {state_path}")


if __name__ == "__main__":
    main()
