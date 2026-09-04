# perp-xrp-signals

Sistema de señales XRP/USDT multi-timeframe. Reutiliza el motor ya construido en
`../xrp_dashboard_server - con chekck.py` (RSI/ADX/DMI/EMAs, escenarios, tier
checklists, win rates verificados en `../../XRP_Trading_Framework.md`) y lo
convierte en:

1. Un pipeline que corre 24/7 en el servidor Lightsail (Windows), refresca datos
   cada 15 min y manda alertas por Telegram cuando se activa un tier alto.
2. Un dashboard ligero en Vercel (tablas, protegido con password) que muestra
   el estado en vivo.
3. El andamiaje que ya esperan las skills instaladas `/analisis-xrp` y
   `/journal-xrp`.

## Estructura

- `scripts/engine.py` — carga `compute_state`/`refresh_all`/`CFG` del script
  original sin duplicar su lógica.
- `scripts/refresh_and_state.py` — usado por `/analisis-xrp`: refresca + calcula
  + guarda `analisis/_state.json`.
- `scripts/refresh_worker.py` — lo mismo, pensado para la tarea programada de
  Lightsail; además dispara `alertas_telegram`.
- `scripts/alertas_telegram.py` — notifica solo transiciones nuevas a estado
  "activo" (no repite en cada corrida).
- `api/api_server.py` — API headless (`GET /api/state`) para que Vercel la
  consuma, con auth por `X-API-Key` y CORS restringido.
- `dashboard-web/` — app Next.js, el proyecto que se despliega en Vercel.
- `deploy/windows/` — scripts y guía paso a paso para instalar todo en el
  Lightsail Windows.

## Uso local (esta máquina)

```
pip install -r requirements.txt
python scripts/refresh_and_state.py
```
Esto genera `analisis/_state.json`. A partir de ahí, `/analisis-xrp manana` o
`/analisis-xrp noche` ya funcionan (leen ese JSON y generan el brief HTML).

Para probar la API y el dashboard localmente antes de tocar Lightsail:
```
copy .env.example .env         REM completa los valores
python api\api_server.py       REM deja esto corriendo
```
En otra terminal:
```
cd dashboard-web
copy .env.example .env.local   REM LIGHTSAIL_API_URL=http://localhost:8787/api/state
npm install
npm run dev
```
Abre `http://localhost:3000` — te pedirá el usuario/password de `DASHBOARD_USER`
/ `DASHBOARD_PASSWORD`.

## Llevarlo a producción

1. **Lightsail (Windows)** — sigue `deploy/windows/README_DEPLOY_WINDOWS.md` al
   pie de la letra (copiar carpeta, `.env`, firewall en dos capas, bot de
   Telegram, Programador de tareas).
2. **Vercel** — cuando quieras desplegar `dashboard-web/`, avísame antes de que
   yo inicialice un repo git nuevo aquí o haga push a GitHub (es un proyecto
   independiente del repo que ya tienes en esta carpeta de Windows). Los pasos:
   - Repo nuevo en GitHub con el contenido de `dashboard-web/` (o todo
     `perp-xrp-signals/` con "Root Directory" = `dashboard-web` en la config de
     Vercel).
   - En Vercel: New Project → importar ese repo → Root Directory `dashboard-web`.
   - Variables de entorno del proyecto (Settings → Environment Variables):
     `LIGHTSAIL_API_URL`, `LIGHTSAIL_API_SECRET`, `DASHBOARD_USER`,
     `DASHBOARD_PASSWORD` (los mismos valores que pusiste en el `.env` de
     Lightsail para `API_KEY_SECRET`).
   - Una vez tengas la URL de Vercel, vuelve al `.env` de Lightsail y pon
     `ALLOWED_ORIGIN=https://tu-app.vercel.app`, reinicia `api_server`.

## Notas

- Todo el acceso a Binance es público/lectura (ccxt sin API keys) — no hay
  credenciales de exchange en ningún archivo de este proyecto.
- `bpt.py` y `xrp_dashboard_9panel.py` (en la carpeta padre) no forman parte de
  este pipeline, se dejaron intactos.
- El archivo original `xrp_dashboard_server - con chekck.py` tampoco se
  modificó — sigue funcionando igual para tu uso local con el dashboard de 9
  paneles.
