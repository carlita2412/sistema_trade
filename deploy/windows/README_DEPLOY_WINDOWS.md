# Desplegar en el servidor Lightsail (Windows)

Estos pasos los ejecutas tú directamente en el servidor (RDP), no requieren SSH.

## 1. Copiar los archivos

Lleva al servidor la carpeta `xrp` completa conservando la estructura, es decir:

```
xrp/
├── xrp_dashboard_server - con chekck.py
├── XRP_USDT_USDT_1m.csv, _5m.csv, _15m.csv, _1h.csv, _4h.csv, _1d.csv, _1w.csv
└── perp-xrp-signals/        <- esta carpeta
```

`engine.py` busca `xrp_dashboard_server - con chekck.py` **un nivel arriba** de
`perp-xrp-signals/` por defecto. Si en el servidor prefieres otra ubicación,
defínelo en `.env` con `DASHBOARD_SCRIPT_PATH` y `DATA_DIR`.

## 2. Python y dependencias

1. Instala Python 3.11+ si no está (python.org, marca "Add to PATH").
2. Abre PowerShell en `perp-xrp-signals/` y crea un entorno virtual:
   ```
   python -m venv venv
   venv\Scripts\pip install -r requirements.txt
   ```

## 3. Configurar `.env`

Copia `.env.example` a `.env` (misma carpeta) y completa:
- `API_KEY_SECRET`: un valor largo y aleatorio (será el mismo que pongas en Vercel).
- `ALLOWED_ORIGIN`: la URL de tu app en Vercel (ej. `https://xrp-signals.vercel.app`).
- `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID`: ver sección 6.

## 4. Probar manualmente antes de programar nada

```
venv\Scripts\python scripts\refresh_and_state.py
```
Debe imprimir `Estado: ok` y crear `analisis\_state.json`. Si da `no_data`,
revisa que los CSV estén donde `DATA_DIR` espera.

```
deploy\windows\run_api_server.bat
```
Con eso corriendo, abre otra ventana y prueba:
```
curl http://localhost:8787/health
curl http://localhost:8787/api/state -H "X-API-Key: TU_SECRETO"
```
Cierra la ventana (Ctrl+C) cuando confirmes que responde.

## 5. Firewall (dos capas, hay que abrir las dos)

**Firewall de Windows** (PowerShell como administrador):
```
New-NetFirewallRule -DisplayName "XRP API" -Direction Inbound -Protocol TCP -LocalPort 8787 -Action Allow
```

**Firewall de red de Lightsail** (consola de AWS, no el servidor):
Ve a tu instancia → pestaña **Networking** → **IPv4 Firewall** → Add rule:
- Application: Custom, TCP, puerto **8787**, origen "Any IPv4" (Vercel no tiene IPs fijas).

## 6. Bot de Telegram

1. En Telegram, habla con **@BotFather** → `/newbot` → sigue las instrucciones → copia el `token`.
2. Habla con tu bot recién creado (cualquier mensaje) para "activar" el chat.
3. Habla con **@userinfobot** para obtener tu `chat_id`, o visita
   `https://api.telegram.org/bot<TOKEN>/getUpdates` después de escribirle al bot
   y busca `"chat":{"id": ...}`.
4. Pon ambos valores en `.env`.

## 7. Programador de tareas — refresco cada 15 min

Abre **Programador de tareas** → Crear tarea (no "básica", para tener más control):
- **General**: nombre `XRP Refresh`. Marca "Ejecutar tanto si el usuario inició sesión como si no".
- **Desencadenadores** → Nuevo: "Con un programa" → Diario → en Opciones avanzadas marca
  "Repetir tarea cada: 15 minutos" y "durante: Indefinidamente".
- **Acciones** → Nuevo → Programa: ruta completa a `deploy\windows\run_refresh.bat`.
- **Configuración**: marca "Si la tarea falla, reiniciar cada: 1 minuto" (3 intentos).

## 8. Programador de tareas — servidor API persistente

Crear otra tarea:
- **Desencadenadores**: "Al iniciar el sistema".
- **Acciones**: Programa `deploy\windows\run_api_server.bat` (este .bat ya se reinicia
  solo si el proceso muere, gracias al loop interno).
- **Configuración**: **desmarca** "Detener la tarea si se ejecuta más de: ...".

Después de crearla, click derecho → **Ejecutar** para arrancarla ya, sin esperar
un reinicio del servidor.

## 9. Verificación final

Desde tu máquina local (no el servidor):
```
curl http://<IP_PUBLICA_LIGHTSAIL>:8787/api/state -H "X-API-Key: TU_SECRETO"
```
Si responde el JSON del estado, ya puedes apuntar `LIGHTSAIL_API_URL` en Vercel a
`http://<IP_PUBLICA_LIGHTSAIL>:8787/api/state`.
