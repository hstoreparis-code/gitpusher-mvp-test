import React from "react";

export default function AiDiscoveryManagerPage() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-50 p-8">
      <h1 className="text-2xl font-semibold mb-4">AI Discovery Dashboard</h1>

      <button
        onClick={async () => {
          await fetch("/admin/ai-autofix", { method: "POST" });
          window.location.reload();
        }}
        style={{
          padding: "8px 16px",
          background: "#0070f3",
          color: "white",
          borderRadius: "6px",
          cursor: "pointer",
          marginBottom: "20px",
        }}
      >
        Run AutoFix
      </button>

      <p className="text-sm text-slate-400">
        This dashboard ensures all AI indexers and knowledge files stay valid so that AI discovery of GitPusher.ai
        remains 100% operational.
      </p>
    </main>
  );
}
