import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Activity, ArrowLeft, Cpu, GaugeCircle, MemoryStick, Server } from "lucide-react";
import AIMeta from "../components/AIMeta";
import { InfoBadge } from "../components/InfoBadge";

export const metadata = {
  title: "Admin — Performance Dashboard",
  description: "Latency, CPU, memory, uptime and backend performance metrics.",
  robots: "noindex, nofollow",
};

function GraphBars({ values, color }) {
  if (!values || !values.length) {
    return <p className="text-xs text-slate-500">Pas encore de données disponibles.</p>;
  }

  const normalized = values.map((v) => {
    const n = typeof v === "number" ? v : 0;
    return Math.max(4, Math.min(100, n));
  });

  return (
    <div className="flex items-end gap-1 h-24">
      {normalized.map((h, i) => (
         
        <div
          key={i}
          style={{
            width: `${100 / normalized.length - 2}%`,
            height: `${h}%`,
            background: color,
            borderRadius: 4,
          }}
        />
      ))}
    </div>
  );
}

function StatusPill({ ok }) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold ${
        ok
          ? "bg-emerald-500/10 text-emerald-300 border border-emerald-400/40"
          : "bg-red-500/10 text-red-300 border border-red-400/40"
      }`}
    >
      {ok ? "OK" : "ERROR"}
    </span>
  );
}

export default function AdminPerformanceDashboard() {
  const navigate = useNavigate();
  const [perf, setPerf] = useState(null);

  useEffect(() => {
    fetch("/api/admin/performance")
      .then((r) => r.json())
      .then(setPerf)
      .catch(() => setPerf({ error: true }));
  }, []);

  // Statut adouci : on considère l'API stable tant qu'aucun flag d'erreur explicite n'est renvoyé
  const apiOk = perf && perf.error === false;
  const uptime = perf?.uptime || "N/A";
  const cpu = typeof perf?.cpu === "number" ? perf.cpu : null;
  const memory = typeof perf?.memory === "number" ? perf.memory : null;
  const rps = typeof perf?.rps === "number" ? perf.rps : null;
  const avgLatency = typeof perf?.avg_latency_ms === "number" ? perf.avg_latency_ms : null;

  return (
    <main className="min-h-screen bg-slate-950 text-slate-50 p-6 sm:p-8 space-y-6">
      <AIMeta />

      {/* Header */}
      <header className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <Button
            size="icon"
            className="h-9 w-9 rounded-full bg-cyan-500 text-slate-950 hover:bg-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.9)] border border-cyan-300/80"
            onClick={() => navigate("/admin")}
          >
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <div>
            <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight">Backend Performance</h1>
            <p className="text-sm text-slate-400 mt-1">
              Latence, uptime, ressources et file de jobs calculés à partir du trafic réel.
            </p>
          </div>
        </div>
        <div className="flex flex-wrap gap-2 items-center">
          <Badge
            className={`text-xs px-3 py-1 rounded-full border ${
              apiOk
                ? "bg-emerald-500/10 border-emerald-400/50 text-emerald-300"
                : "bg-red-500/10 border-red-400/50 text-red-300"
            }`}
          >
            <span className="inline-flex items-center gap-1">
              <GaugeCircle className="w-3 h-3" />
              <span>{apiOk ? "API Stable" : "Incidents détectés"}</span>
            </span>
          </Badge>
        </div>
      </header>

      {/* Top cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="bg-slate-900/70 border-slate-700/70 shadow-[0_0_25px_rgba(56,189,248,0.2)]">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="flex items-center gap-1 text-xs font-medium text-cyan-300 uppercase tracking-wide">
              <span>System & API</span>
              <InfoBadge text={"Vue temps réel de la stabilité du backend (statut API, uptime, RPS, latence moyenne). Utilise cette carte pour voir si le backend tient la charge ou sature (RPS élevé + latence qui grimpe = problème)."} />
            </CardTitle>
            <Server className="w-4 h-4 text-emerald-400" />
          </CardHeader>
          <CardContent className="space-y-1 text-xs text-slate-300">
            <p>
              Statut API : <StatusPill ok={!!apiOk} />
            </p>
            <p>Uptime : {uptime}</p>
            <p>RPS (dernière minute) : {typeof rps === "number" && Number.isFinite(rps) ? rps.toFixed(2) : "N/A"}</p>
            <p>Latence moyenne : {typeof avgLatency === "number" && Number.isFinite(avgLatency) ? `${avgLatency.toFixed(1)} ms` : "N/A"}</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/70 border-slate-700/70 shadow-[0_0_25px_rgba(56,189,248,0.2)]">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="flex items-center gap-1 text-xs font-medium text-cyan-300 uppercase tracking-wide">
              <span>Ressources</span>
              <InfoBadge text={"Charge estimée sur CPU et mémoire sur les derniers échantillons. Si ces valeurs restent élevées tout le temps, augmente les ressources ou optimise les jobs les plus lourds."} />
            </CardTitle>
            <Cpu className="w-4 h-4 text-cyan-400" />
          </CardHeader>
          <CardContent className="space-y-1 text-xs text-slate-300">
            <p>CPU Load estimé : {cpu != null ? `${cpu}%` : "N/A"}</p>
            <p>Memory Usage estimée : {memory != null ? `${memory}%` : "N/A"}</p>
            <p>Jobs en file : {perf?.queue_size != null ? perf.queue_size : "N/A"}</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/70 border-slate-700/70 shadow-[0_0_25px_rgba(56,189,248,0.2)]">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="flex items-center gap-1 text-xs font-medium text-cyan-300 uppercase tracking-wide">
              <span>Synthèse rapide</span>
              <InfoBadge text={"Résumé narratif de l'état du backend sur les dernières minutes (OK vs incidents). Lis ceci en premier pour savoir rapidement si la plateforme est saine."} />
            </CardTitle>
            <Activity className="w-4 h-4 text-violet-400" />
          </CardHeader>
          <CardContent className="space-y-1 text-xs text-slate-300">
            <p>
              {apiOk
                ? "Le backend répond correctement et les métriques sont dans des plages normales."
                : "Des erreurs ont été détectées récemment sur l'API. Vérifie les logs et les jobs en erreur."}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Graphs */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card className="bg-slate-900/70 border-slate-700/70 shadow-[0_0_25px_rgba(56,189,248,0.2)]">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium text-cyan-300 uppercase tracking-wide">
              Latence des requêtes (ms)
            </CardTitle>
            <Activity className="w-4 h-4 text-cyan-400" />
          </CardHeader>
          <CardContent className="space-y-2 text-xs text-slate-300">
            <GraphBars
              values={Array.isArray(perf?.latency_samples) ? perf.latency_samples : []}
              color="linear-gradient(180deg,#58a6ff,#1f6feb)"
            />
            <p className="text-[11px] text-slate-500 mt-1">
              Calculée sur les 10 dernières minutes de trafic réel.
            </p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/70 border-slate-700/70 shadow-[0_0_25px_rgba(56,189,248,0.2)]">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium text-cyan-300 uppercase tracking-wide">
              Charge CPU & Mémoire (indices)
            </CardTitle>
            <MemoryStick className="w-4 h-4 text-emerald-400" />
          </CardHeader>
          <CardContent className="space-y-4 text-xs text-slate-300">
            <div>
              <p className="mb-1 text-[11px] text-slate-400">CPU (échantillons)</p>
              <GraphBars
                values={Array.isArray(perf?.cpu_samples) ? perf.cpu_samples : []}
                color="linear-gradient(180deg,#ffb340,#ff8c00)"
              />
            </div>
            <div>
              <p className="mb-1 text-[11px] text-slate-400">Mémoire (échantillons)</p>
              <GraphBars
                values={Array.isArray(perf?.memory_samples) ? perf.memory_samples : []}
                color="linear-gradient(180deg,#40ffbf,#00c78c)"
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
