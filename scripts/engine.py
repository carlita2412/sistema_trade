# -*- coding: utf-8 -*-
"""
Carga el motor de señales original del usuario (compute_state, refresh_all, CFG)
sin copiar su lógica, y expone utilidades comunes para los scripts del pipeline.

El archivo original vive fuera de este proyecto y tiene espacios en el nombre,
así que se carga por ruta con importlib en vez de un import normal.
"""
import importlib.util
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XRP_DIR = os.path.dirname(PROJECT_ROOT)

DASHBOARD_SCRIPT_PATH = os.environ.get(
    "DASHBOARD_SCRIPT_PATH",
    os.path.join(XRP_DIR, "xrp_dashboard_server - con chekck.py"),
)
DATA_DIR = os.environ.get("DATA_DIR", XRP_DIR)
ANALISIS_DIR = os.path.join(PROJECT_ROOT, "analisis")


def load_dotenv(path=None):
    """Carga variables desde un archivo .env sin pisar las ya definidas en el entorno."""
    path = path or os.path.join(PROJECT_ROOT, ".env")
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def _load_dashboard_module():
    if not os.path.exists(DASHBOARD_SCRIPT_PATH):
        raise FileNotFoundError(
            f"No se encontró el script original del dashboard en: {DASHBOARD_SCRIPT_PATH}\n"
            "Define la variable de entorno DASHBOARD_SCRIPT_PATH si lo moviste."
        )
    spec = importlib.util.spec_from_file_location("xrp_dashboard_core", DASHBOARD_SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.CFG["data_dir"] = DATA_DIR
    module.CFG["auto_open"] = False
    return module


_dashboard = _load_dashboard_module()

CFG = _dashboard.CFG
compute_state = _dashboard.compute_state
refresh_all = _dashboard.refresh_all
dumps = _dashboard.dumps
csv_status = _dashboard.csv_status


def refresh_and_save(log=print, skip_refresh_on_error=True):
    """Refresca los CSV vía ccxt (best-effort) y calcula+guarda el estado completo.

    Devuelve (state_dict, path_al_json). Si el refresco falla (sin conexión,
    restricción geográfica, etc.) sigue adelante con los CSV locales existentes,
    tal como espera la skill /analisis-xrp.
    """
    try:
        refresh_all(log)
    except Exception as e:
        if not skip_refresh_on_error:
            raise
        log(f"Aviso: refresco de datos falló, se usan los CSV locales ({e})")

    state = compute_state()

    os.makedirs(ANALISIS_DIR, exist_ok=True)
    state_path = os.path.join(ANALISIS_DIR, "_state.json")
    with open(state_path, "w", encoding="utf-8") as f:
        f.write(dumps(state))

    return state, state_path
