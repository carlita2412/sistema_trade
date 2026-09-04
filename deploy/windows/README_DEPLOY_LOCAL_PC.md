# Desplegar en tu computadora local (en vez de Lightsail)

Se descartó Lightsail porque su región (us-east-1, EE.UU.) está bloqueada por
Binance (451). Tu red local sí llega a Binance, así que el motor corre en tu
propia PC. La diferencia frente a un servidor en la nube: tu PC está detrás
del router de tu casa, así que hay que abrir un camino desde internet hasta
ella (Vercel necesita poder llegarle a `/api/state`).

## 1. Dependencias

Ya las tienes instaladas globalmente (`ccxt`, `pandas`, `numpy` — se usaron
para las pruebas). Si en algún momento quieres aislarlas en un entorno virtual:
```
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```
y usa `venv\Scripts\python.exe` en vez de `python` en los pasos siguientes
(en PowerShell, con el prefijo `.\`, ej. `.\venv\Scripts\python.exe`).

## 2. `.env`

Ya deberías tener `perp-xrp-signals\.env` de las pruebas anteriores. Confirma
que tenga:
```
API_PORT=8787
API_HOST=0.0.0.0
API_KEY_SECRET=_s0wY7x6clT56LyGQAO_W0BVSws_lR-f_6FkzjBNL7s
ALLOWED_ORIGIN=https://sistema-trade-delta.vercel.app
TELEGRAM_BOT_TOKEN=7981206261:AAEmbR_B5kvw5ECOf47HMBaUJEpUGQwi8a8
TELEGRAM_CHAT_ID=506401950
```
(Ya lo probaste — el refresco funcionó bien.)

## 3. Encontrar la IP local de tu PC en la red de casa

```powershell
ipconfig
```
Busca "Dirección IPv4" de tu adaptador activo (ej. `192.168.1.35`). La vas a
necesitar para el paso 5.

## 4. Firewall de Windows

PowerShell como administrador:
```powershell
New-NetFirewallRule -DisplayName "XRP API" -Direction Inbound -Protocol TCP -LocalPort 8787 -Action Allow
```

## 5. Redirección de puertos en tu router (port forwarding)

Entra al panel de administración de tu router (normalmente
`http://192.168.1.1` o `http://192.168.0.1` — la puerta de enlace que te
muestre `ipconfig`). Busca la sección **Port Forwarding / Virtual Server /
NAT** (el nombre exacto varía por marca) y agrega una regla:
- Puerto externo: `8787`
- Puerto interno: `8787`
- IP interna: la de tu PC (paso 3)
- Protocolo: TCP

Sin esto, nada de afuera (incluido Vercel) puede llegar a tu PC.

## 6. DNS dinámico (tu IP de casa cambia)

Los proveedores de internet residenciales casi siempre asignan una IP pública
que cambia cada cierto tiempo. Si usas la IP directa, `LIGHTSAIL_API_URL` en
Vercel se rompe cada vez que cambie. Solución: un hostname fijo apuntando
siempre a tu IP actual.

1. Crea una cuenta gratis en **DuckDNS** (duckdns.org) o **No-IP** (noip.com).
2. Crea un subdominio, ej. `carlaxrp.duckdns.org`.
3. Revisa si tu router ya trae cliente DDNS integrado (sección "Dynamic DNS"
   del panel — muchos routers domésticos soportan DuckDNS/No-IP nativamente,
   es la forma más simple: se actualiza solo, sin instalar nada en la PC).
4. Si tu router no lo soporta, instala el actualizador oficial de DuckDNS/No-IP
   en tu PC (corre en segundo plano y actualiza el DNS cuando tu IP cambia).

Al final debes poder hacer ping a `carlaxrp.duckdns.org` y que resuelva a tu
IP pública actual.

## 7. Evitar que la PC se duerma

Si la PC entra en suspensión, se cae el servidor y las tareas programadas no
corren. **Configuración → Sistema → Energía y batería → Pantalla y suspensión**
→ pon "Nunca" en suspensión mientras esté conectada a corriente.

## 8. Programador de tareas

Igual que en el README de Lightsail (secciones 7 y 8), pero usando las rutas
de esta carpeta local:
- **Tarea "XRP Refresh"**: repetir cada 15 min, acción
  `deploy\windows\run_refresh.bat`.
- **Tarea "XRP API"**: "Al iniciar sesión" (en vez de "al iniciar el sistema",
  ya que en una PC personal normalmente inicias sesión tú, no es un server
  headless), acción `deploy\windows\run_api_server.bat`, sin límite de
  duración.

## 9. Verificar desde afuera

Desde otra red (o pídeme a mí que lo pruebe):
```
curl http://carlaxrp.duckdns.org:8787/api/state -H "X-API-Key: TU_SECRETO"
```

## 10. Apuntar Vercel a tu PC

En Vercel, actualiza la variable `LIGHTSAIL_API_URL`:
```
LIGHTSAIL_API_URL=http://carlaxrp.duckdns.org:8787/api/state
```
(el nombre de la variable quedó como estaba, apunta a tu PC en vez de a
Lightsail — no hace falta cambiar código por esto). Redeploy después de
guardar.
