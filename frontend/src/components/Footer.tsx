import React from 'react';
import { Shield, AlertTriangle } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-[#091322] text-slate-400 text-xs border-t border-slate-800 mt-auto py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-4">
        {/* Core Doctrine Callout */}
        <div className="bg-[#0F1E36] border border-[#C5A059]/40 rounded-lg p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-slate-300">
          <div className="flex items-center space-x-2">
            <Shield className="w-5 h-5 text-[#C5A059] shrink-0" />
            <span className="font-semibold text-white tracking-wide">
              CORE FORENSIC PRINCIPLE:
            </span>
            <span className="text-amber-200/90 italic font-serif">
              "The tool screens. The expert decides."
            </span>
          </div>
          <span className="text-[11px] text-slate-400 bg-black/30 px-2.5 py-1 rounded border border-slate-700">
            Automated output is never presented as legal proof or conclusive forensic opinion.
          </span>
        </div>

        {/* Mandatory Statutory Notice */}
        <div className="bg-slate-900/60 border border-slate-800 rounded p-3 text-[11px] leading-relaxed text-slate-400 flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
          <p>
            <strong className="text-slate-300">Preliminary Screening Notice:</strong> SCSS SATYA produces preliminary,
            automated image-screening findings for investigative support. Its results are not a definitive determination of
            authenticity, manipulation, source, intent, or legal admissibility. The absence of detected indicators does not
            establish that an image is authentic. Findings require interpretation by a qualified forensic examiner and must be
            considered alongside other available evidence.
          </p>
        </div>

        {/* Legal & Standards Meta */}
        <div className="flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-slate-800/80">
          <div>
            © {new Date().getFullYear()} Sure Clue Scientific Solutions (SCSS). Built for SEVA FIRST Innovation Challenge 2026.
          </div>
          <div className="flex items-center space-x-4 mt-2 sm:mt-0 font-mono">
            <span>ISO/IEC 27037:2012 Aligned</span>
            <span>•</span>
            <span>Sec 63 BSA 2023 / Sec 65B IEA</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
