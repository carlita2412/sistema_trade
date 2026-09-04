"use client";

import { useEffect, useState } from "react";

const POLL_MS = 120_000;
const TF_ORDER = ["W", "D", "H4", "H1", "M15"];
const TF_LABEL: Record<string, string> = { W: "Semanal", D: "Diario", H4: "4H", H1: "1H", M15: "15m" };

function badgeClass(cls: string) {
  if (cls?.includes("bull")) return "badge badge-bull";
  if (cls?.includes("bear")) return "badge badge-bear";
  return "badge badge-wait";
}

export default function Page() {
  const [state, setState] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const res = await fetch("/api/state");
        const data = await res.json();
        if (cancelled) return;
        if (data.status === "error") {
          setError(data.error);
        } else {
          setState(data);
          setError(null);
        }
      } catch (e: any) {
        if (!cancelled) setError(e.message);
      }
    }
    load();
    const id = setInterval(load, POLL_MS);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  if (error) {
    return (
      <main>
        <h1>XRP/USDT · Señales</h1>
        <div className="error">Error: {error}</div>
      </main>
    );
  }

  if (!state) {
    return (
      <main>
        <h1>XRP/USDT · Señales</h1>
        <p className="meta">Cargando...</p>
      </main>
    );
  }

  if (state.status === "no_data") {
    return (
      <main>
        <h1>XRP/USDT · Señales</h1>
        <div className="error">{state.msg || "Sin datos todavía."}</div>
      </main>
    );
  }

  const regime = state.regime || {};
  const tierChecks = state.tier_checks || { items: [] };
  const wr = state.wr || {};

  return (
    <main>
      <h1>XRP/USDT · Señales</h1>
      <p className="meta">
        Precio {state.px} · vela {state.ts} · actualizado {state.updated}
      </p>

      <div className="card">
        {regime.macro && <span className={badgeClass(regime.macro[1])}>{regime.macro[0]}</span>}{" "}
        {regime.tactico && <span className={badgeClass(regime.tactico[1])}>{regime.tactico[0]}</span>}{" "}
        {regime.signal && <span className={badgeClass(regime.signal[1])}>{regime.signal[0]}</span>}
      </div>

      <h2>Snapshot por timeframe</h2>
      <table>
        <thead>
          <tr>
            <th>TF</th><th>Close</th><th>RSI</th><th>ADX</th><th>DI+</th><th>DI-</th>
            <th>EMA9</th><th>EMA21</th><th>EMA55</th><th>EMA200</th>
          </tr>
        </thead>
        <tbody>
          {TF_ORDER.filter((k) => state.tf?.[k]).map((k) => {
            const r = state.tf[k];
            return (
              <tr key={k}>
                <td>{TF_LABEL[k]}</td>
                <td>{r.close}</td><td>{r.rsi}</td><td>{r.adx}</td><td>{r.pdi}</td><td>{r.mdi}</td>
                <td>{r.ema9}</td><td>{r.ema21}</td><td>{r.ema55}</td><td>{r.ema200}</td>
              </tr>
            );
          })}
        </tbody>
      </table>

      <h2>Escenarios · checklist automático ({tierChecks.most_probable_label})</h2>
      <table>
        <thead>
          <tr><th>Escenario</th><th>Lado</th><th>Estado</th><th>Score</th></tr>
        </thead>
        <tbody>
          {tierChecks.items?.map((it: any) => (
            <tr key={it.id} className={`scenario-row ${it.status}`}>
              <td>{it.name}</td>
              <td>{it.side}</td>
              <td>{it.status}</td>
              <td>{it.score}%</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Niveles · entrada / stop / TPs</h2>
      {state.scenarios?.map((s: any, i: number) => (
        <div className="card" key={i}>
          <strong>{s.ttl}</strong> — {s.stt} · {s.rr} · {s.dd}
          <table>
            <tbody>
              {s.rows?.map((row: any[], j: number) => (
                <tr key={j}>
                  <td>{row[0]}</td>
                  <td>{row[1]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}

      {state.divergence?.active && (
        <>
          <h2>Divergencia RSI 4H</h2>
          <div className="card">
            Activa · RSI previo {state.divergence.rsi_prev} → actual {state.divergence.rsi_cur}
          </div>
        </>
      )}

      <h2>Win rates verificados (holding {state.hold_bars || 6} barras)</h2>
      <table>
        <thead>
          <tr><th>Tier</th><th>N</th><th>WR%</th></tr>
        </thead>
        <tbody>
          {Object.entries(wr).map(([key, v]: [string, any]) => (
            <tr key={key}>
              <td>{key}</td>
              <td>{v?.n}</td>
              <td>{v?.wr}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
