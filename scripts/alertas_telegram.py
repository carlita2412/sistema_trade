# -*- coding: utf-8 -*-
"""
Notifica por Telegram cuando un escenario de tier alto pasa a estado "activo".

Solo avisa transiciones nuevas (no-activo -> activo), comparando contra
analisis/_last_alert.json, para no spamear en cada corrida del refresco.
Todos los números del mensaje se toman tal cual de compute_state(); nunca
se calculan ni se inventan aquí.
"""
import json
import os
import urllib.parse
import urllib.request

import engine

LAST_ALERT_PATH = os.path.join(engine.ANALISIS_DIR, "_last_alert.json")

TIER_LABELS = {
    "A_plus": ("LONG tier A+", "A_plus"),
    "A_minus": ("LONG tier A-", "A_minus"),
    "S_DIV": ("LONG tier S (divergencia)", "S"),
    "B_SHORT": ("SHORT tier B", "B_short"),
}


def _load_last_active():
    if not os.path.exists(LAST_ALERT_PATH):
        return set()
    try:
        with open(LAST_ALERT_PATH, "r", encoding="utf-8") as f:
            return set(json.load(f).get("active", []))
    except (json.JSONDecodeError, OSError):
        return set()


def _save_active(active_ids):
    os.makedirs(engine.ANALISIS_DIR, exist_ok=True)
    with open(LAST_ALERT_PATH, "w", encoding="utf-8") as f:
        json.dump({"active": sorted(active_ids)}, f)


def _matching_scenario(state, tier_id):
    side_cls = "short" if tier_id == "B_SHORT" else "long"
    for scn in state.get("scenarios", []):
        if scn.get("cls", "").startswith(side_cls):
            return scn
    return None


def _format_message(state, tier_id, item):
    label, wr_key = TIER_LABELS.get(tier_id, (tier_id, None))
    wr = (state.get("wr") or {}).get(wr_key) if wr_key else None
    wr_txt = f"{wr['wr']}% (n={wr['n']})" if wr else "sin muestra"

    scn = _matching_scenario(state, tier_id)
    lines = [
        f"Nueva señal activa: {label}",
        f"Score checklist: {item.get('score')}%",
        f"Precio: {state.get('px')}",
        f"WR histórico: {wr_txt}",
        f"Régimen: {(state.get('regime') or {}).get('signal', ['', ''])[0]}",
    ]
    if scn:
        for row in scn.get("rows", []):
            if len(row) >= 2 and row[-1] in ("e", "sl", "tp"):
                lines.append(f"{row[0]}: {row[1]}")
    lines.append(f"Hora: {state.get('updated')}")
    return "\n".join(lines)


def send_telegram_message(text):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Telegram no configurado (falta TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID); se omite el aviso.")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode("utf-8")
    try:
        with urllib.request.urlopen(url, data=data, timeout=15) as r:
            return r.status == 200
    except Exception as e:
        print(f"Error enviando Telegram: {e}")
        return False


def check_and_notify(state):
    if state.get("status") != "ok":
        return

    items = (state.get("tier_checks") or {}).get("items", [])
    active_now = {it["id"] for it in items if it.get("status") == "activo"}
    prev_active = _load_last_active()
    new_active = active_now - prev_active

    confirmed = set(prev_active & active_now)
    for tier_id in new_active:
        item = next((it for it in items if it["id"] == tier_id), {})
        msg = _format_message(state, tier_id, item)
        if send_telegram_message(msg):
            confirmed.add(tier_id)
        print(f"Alerta {tier_id}: {'enviada' if tier_id in confirmed else 'FALLÓ, se reintenta la próxima corrida'}")

    _save_active(confirmed)
