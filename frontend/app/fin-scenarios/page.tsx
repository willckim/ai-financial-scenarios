"use client";

import React, { useMemo, useState } from "react";

type ForecastRow = Record<string, string | number>;
type AnalyzeResponse = {
  forecast: ForecastRow[];
  summary: string;
  key_metrics: Record<string, number>;
};

const toCurrency = (n: number) =>
  n.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });

export default function FinancialScenarioPage() {
  const [file, setFile] = useState<File | null>(null);
  const [months, setMonths] = useState(12);
  const [provider, setProvider] = useState<"anthropic" | "openai" | "azure">("anthropic");
  const [model, setModel] = useState("");
  const [revGrowthM, setRevGrowthM] = useState(0.02);
  const [churnM, setChurnM] = useState(0.015);
  const [cac, setCAC] = useState(110);
  const [mktSpend, setMktSpend] = useState(4000);
  const [cogsPct, setCogsPct] = useState(0.34);
  const [opexGrowthM, setOpexGrowthM] = useState(0.01);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const [data, setData] = useState<AnalyzeResponse | null>(null);

  const backend = (process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

  const scenarioJson = useMemo(
    () =>
      JSON.stringify({
        months_ahead: months,
        rev_growth_m: revGrowthM,
        churn_m: churnM,
        cac,
        marketing_spend: mktSpend,
        cogs_pct: cogsPct,
        opex_growth_m: opexGrowthM,
      }),
    [months, revGrowthM, churnM, cac, mktSpend, cogsPct, opexGrowthM]
  );

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setData(null);

    if (!file) {
      setError("Upload a CSV with columns: month,revenue,cogs,opex,customers.");
      return;
    }
    try {
      setLoading(true);
      const fd = new FormData();
      fd.append("file", file);
      fd.append("scenario_json", scenarioJson);
      fd.append("provider", provider);
      if (model) fd.append("model", model);

      const res = await fetch(`${backend}/analyze`, { method: "POST", body: fd });
      if (!res.ok) {
        let msg = await res.text();
        try { const j = JSON.parse(msg); msg = j?.detail || j?.message || msg; } catch {}
        throw new Error(msg || `HTTP ${res.status}`);
      }
      const json = (await res.json()) as AnalyzeResponse;
      setData(json);
    } catch (err: any) {
      setError(err?.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  function downloadForecastCSV() {
    if (!data?.forecast?.length) return;
    const headers = Object.keys(data.forecast[0]);
    const rows = data.forecast.map((r) => headers.map((h) => String(r[h] ?? "")).join(","));
    const csv = [headers.join(","), ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "forecast.csv"; a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <main>
      {/* Hero */}
      <section className="glass p-5 mb-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
          <div>
            <h1 className="font-bold tracking-tight text-[clamp(22px,3.6vw,30px)]"
                style={{ background: "linear-gradient(90deg, #fff, #c7d2fe 30%, #a5f3fc 70%)",
                         WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent" }}>
              Financial Scenario Generator
            </h1>
            <p className="text-muted mt-1">Upload monthly historicals → tweak assumptions → get a CFO-style analysis.</p>
          </div>
          <button type="button" className="btn" onClick={async () => {
            try {
              const r = await fetch(`${backend}/health`);
              const j = await r.json();
              alert(`API OK: ${JSON.stringify(j.providers)}`);
            } catch {
              alert("API not reachable");
            }
          }}>
            Check API
          </button>
        </div>
      </section>

      {/* Form grid */}
      <form onSubmit={onSubmit} className="grid md:grid-cols-3 gap-5">
        <section className="md:col-span-2 space-y-5">
          <div className="glass p-5">
            <h2 className="mb-3 text-[18px]">📄 Upload CSV</h2>
            <label className="text-muted text-sm block mb-2">Required columns: month, revenue, cogs, opex, customers</label>
            <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0] ?? null)} className="file w-full" />
            <p className="text-muted text-xs mt-2">
              Tip: use <code>sample_data/historicals_example.csv</code> from your repo.
            </p>
          </div>

          <div className="glass p-5">
            <h2 className="mb-3 text-[18px]">⚙️ Assumptions</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <Num label="Months ahead" value={months} setValue={setMonths} min={1} max={36} step={1} />
              <Num label="Rev growth (mo)" value={revGrowthM} setValue={setRevGrowthM} step={0.005} />
              <Num label="Churn (mo)" value={churnM} setValue={setChurnM} step={0.0025} />
              <Num label="CAC" value={cac} setValue={setCAC} step={10} />
              <Num label="Mkt spend" value={mktSpend} setValue={setMktSpend} step={250} />
              <Num label="COGS %" value={cogsPct} setValue={setCogsPct} step={0.01} />
              <Num label="OpEx growth (mo)" value={opexGrowthM} setValue={setOpexGrowthM} step={0.0025} />
            </div>
          </div>
        </section>

        <section className="space-y-5">
          <div className="glass p-5">
            <h2 className="mb-3 text-[18px]">🤖 Model</h2>

            <label className="text-sm text-muted block mb-1">Provider</label>
            <select value={provider} onChange={(e) => setProvider(e.target.value as any)} className="select">
              <option value="anthropic">Anthropic (Claude)</option>
              <option value="openai">OpenAI (ChatGPT)</option>
              <option value="azure">Azure OpenAI</option>
            </select>

            <label className="text-sm text-muted block mt-4 mb-1">Model (optional)</label>
            <input value={model} onChange={(e) => setModel(e.target.value)} placeholder="e.g., claude-3-5-sonnet or gpt-4o-mini" className="input" />

            <button type="submit" disabled={loading} className="btn btn-primary w-full mt-5">
              {loading ? "Analyzing…" : "Run Scenario"}
            </button>

            {error && <p className="mt-3 text-sm" style={{ color: "var(--err)" }}>{error}</p>}
            <p className="mt-3 text-xs text-muted">Backend: <code>{backend}</code></p>
          </div>

          {data?.key_metrics && (
            <div className="glass p-5">
              <h2 className="mb-3 text-[18px]">📊 Key Metrics</h2>
              <Metric label="Revenue (12m)" value={toCurrency(data.key_metrics["revenue_12m"] || 0)} />
              <Metric label="EBITDA (12m)" value={toCurrency(data.key_metrics["ebitda_12m"] || 0)} />
              <Metric label="EBITDA Margin (last)" value={`${Math.round((data.key_metrics["ebitda_margin_last"] || 0) * 100)}%`} />
              <button type="button" onClick={downloadForecastCSV} className="btn w-full mt-4">Download Forecast CSV</button>
            </div>
          )}
        </section>
      </form>

      {data?.summary && (
        <div className="glass p-5 mt-6">
          <h2 className="mb-3 text-[18px]">🧠 Executive Summary</h2>
          <article className="prose whitespace-pre-wrap" style={{ background: "var(--answer)", border: "1px solid rgba(255,255,255,.08)", borderRadius: 12, padding: "12px 14px" }}>
            {data.summary}
          </article>
        </div>
      )}

      {data?.forecast?.length ? (
        <div className="glass p-5 mt-6">
          <h2 className="mb-3 text-[18px]">📈 Forecast (first 12 rows)</h2>
          <div className="overflow-auto">
            <table className="table min-w-full text-sm">
              <thead>
                <tr>
                  {Object.keys(data.forecast[0]).map((k) => (
                    <th key={k} className="text-left p-2 font-medium">{k}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.forecast.slice(0, 12).map((row, i) => (
                  <tr key={i} className="odd:bg-transparent even:bg-[rgba(255,255,255,.04)]">
                    {Object.entries(row).map(([key, v], j) => (
                      <td key={j} className="p-2">
                        {typeof v === "number" && ["revenue", "cogs", "opex", "gross_profit", "ebitda"].includes(key)
                          ? toCurrency(v)
                          : String(v)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </main>
  );
}

/* ---------- UI helpers ---------- */

function Num({
  label, value, setValue, step = 0.01, min, max,
}: {
  label: string; value: number; setValue: (v: number) => void; step?: number; min?: number; max?: number;
}) {
  return (
    <div>
      <label className="block text-sm text-muted mb-1">{label}</label>
      <input
        type="number"
        step={step}
        min={min}
        max={max}
        value={value}
        onChange={(e) => setValue(parseFloat(e.target.value || "0"))}
        className="input"
      />
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-xl border p-3" style={{ borderColor: "var(--border)" }}>
      <span className="text-sm text-muted">{label}</span>
      <span className="text-base font-semibold">{value}</span>
    </div>
  );
}
