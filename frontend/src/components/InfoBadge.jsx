import { useState } from "react";
import { Info } from "lucide-react";

/**
 * Petit composant générique pour afficher un "i" d'information.
 * - Affiche un bouton rond avec un i.
 * - Au clic, ouvre un panneau flottant avec un texte explicatif détaillé.
 */
export function InfoBadge({ text }) {
  const [open, setOpen] = useState(false);

  if (!text) return null;

  return (
    <div className="relative inline-flex items-center">
      <button
        type="button"
        aria-label="Informations détaillées"
        className="ml-2 inline-flex items-center justify-center h-5 w-5 rounded-full border border-cyan-400/80 bg-slate-950 text-cyan-300 hover:bg-cyan-500/20 hover:text-cyan-50 text-[10px] shadow-[0_0_14px_rgba(34,211,238,0.9)]"
        onClick={() => setOpen((v) => !v)}
      >
        <Info className="w-3 h-3" />
      </button>
      {open && (
        <div className="absolute left-full top-1/2 ml-3 -translate-y-1/2 w-72 max-w-xs rounded-xl border border-cyan-400/60 bg-slate-950/95 p-3 text-[11px] text-slate-200 shadow-[0_0_40px_rgba(34,211,238,0.9)] z-40">
          <p className="leading-snug whitespace-pre-line">
            {text}
          </p>
        </div>
      )}
    </div>
  );
}

