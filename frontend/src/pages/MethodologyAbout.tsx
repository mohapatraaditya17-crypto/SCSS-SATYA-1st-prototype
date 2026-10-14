import React, { useEffect, useState } from 'react';
import {
  Scale,
  AlertTriangle,
  Cpu,
  Layers,
} from 'lucide-react';

export const MethodologyAbout: React.FC = () => {
  const [versionData, setVersionData] = useState<any>(null);

  useEffect(() => {
    fetch('/api/version')
      .then((res) => res.json())
      .then((data) => setVersionData(data))
      .catch(() => {});
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Title */}
      <div>
        <div className="flex items-center space-x-2 text-[#C5A059] text-xs font-semibold uppercase tracking-wider mb-1">
          <span>Forensic Doctrine & Technical Documentation</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
          SCSS SATYA — Methodology & Scientific Limitations
        </h1>
        <p className="text-slate-600 text-xs sm:text-sm mt-1">
          Technical specifications, screening principles, and evidentiary standards governing the SATYA platform.
        </p>
      </div>

      {/* Prominent Disclaimer Callout */}
      <div className="bg-amber-50 border-l-4 border-[#C5A059] p-4 rounded-r-lg shadow-xs space-y-2">
        <div className="flex items-center space-x-2 text-amber-900 font-bold text-xs uppercase tracking-wide">
          <AlertTriangle className="w-4 h-4 text-[#C5A059]" />
          <span>Mandatory Evidentiary & Scientific Disclosure</span>
        </div>
        <p className="text-xs text-amber-950 leading-relaxed">
          SCSS SATYA produces preliminary, automated image-screening findings for investigative support. Its results are
          not a definitive determination of authenticity, manipulation, source, intent, or legal admissibility. The absence of
          detected indicators does not establish that an image is authentic. Findings require interpretation by a qualified
          forensic examiner and must be considered alongside other available evidence.
        </p>
        <p className="text-[11px] text-amber-800">
          This software prototype has not been independently accredited or certified by an external laboratory standards body.
        </p>
      </div>

      {/* 4-Layer Forensic Architecture */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-200 pb-3">
          <Layers className="w-5 h-5 text-[#0F1E36]" />
          <h2 className="text-base font-bold text-slate-900">
            The 4-Layer Forensic Screening Architecture
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="border border-slate-200 rounded-lg p-4 bg-slate-50/50 space-y-2">
            <div className="font-semibold text-slate-900 flex items-center gap-1.5">
              <span className="w-5 h-5 rounded-full bg-[#0F1E36] text-white flex items-center justify-center text-[10px]">1</span>
              <span>Passive-Blind Screening (Layer 1)</span>
            </div>
            <p className="text-slate-600 leading-relaxed">
              Examines digital images without requiring the original camera or reference specimens. Analyzes metadata,
              JPEG Error Level Analysis (ELA), and high-frequency noise variance.
            </p>
          </div>

          <div className="border border-slate-200 rounded-lg p-4 bg-slate-50/50 space-y-2">
            <div className="font-semibold text-slate-900 flex items-center gap-1.5">
              <span className="w-5 h-5 rounded-full bg-[#0F1E36] text-white flex items-center justify-center text-[10px]">2</span>
              <span>Evidence Integrity Baseline (Layer 2)</span>
            </div>
            <p className="text-slate-600 leading-relaxed">
              Computes SHA-256 cryptographic hashes immediately upon ingestion. Original raw bitstream is archived in an
              isolated local evidence vault.
            </p>
          </div>

          <div className="border border-slate-200 rounded-lg p-4 bg-slate-50/50 space-y-2">
            <div className="font-semibold text-slate-900 flex items-center gap-1.5">
              <span className="w-5 h-5 rounded-full bg-[#0F1E36] text-white flex items-center justify-center text-[10px]">3</span>
              <span>Explainable Findings & Limits (Layer 3)</span>
            </div>
            <p className="text-slate-600 leading-relaxed">
              Rejects opaque black-box AI scores (e.g. "99% Fake"). Provides structured indicators, technical observations,
              known limitations, and suggested manual examiner verifications.
            </p>
          </div>

          <div className="border border-slate-200 rounded-lg p-4 bg-slate-50/50 space-y-2">
            <div className="font-semibold text-slate-900 flex items-center gap-1.5">
              <span className="w-5 h-5 rounded-full bg-[#0F1E36] text-white flex items-center justify-center text-[10px]">4</span>
              <span>Qualified Human Review (Layer 4)</span>
            </div>
            <p className="text-slate-600 leading-relaxed">
              Enables certified examiners to review indicators, inspect exhibits, record qualitative notes, and attest formal
              opinions on downloadable ISO/IEC 27037 PDF reports.
            </p>
          </div>
        </div>
      </div>

      {/* Implemented Methods Breakdown */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-6">
        <div className="flex items-center space-x-2 border-b border-slate-200 pb-3">
          <Cpu className="w-5 h-5 text-[#0F1E36]" />
          <h2 className="text-base font-bold text-slate-900">
            Implemented Screening Methods & Working Principles
          </h2>
        </div>

        {/* Method A */}
        <div className="space-y-2 text-xs">
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#C5A059]" />
            <span>Test A: File and Metadata Examination (v1.0.0)</span>
          </h3>
          <p className="text-slate-700 leading-relaxed">
            Parses EXIF, TIFF, and JFIF image headers using standard compliant parsers. Inspects hardware signatures
            (Camera Make, Model), exposure values, capture timestamps, and software processing tags (e.g., Adobe Photoshop,
            GIMP, Canva, Stable Diffusion).
          </p>
          <div className="bg-slate-50 p-3 rounded border border-slate-200 text-slate-600 space-y-1">
            <strong>Key Limitations:</strong>
            <ul className="list-disc list-inside space-y-0.5 text-[11px]">
              <li>Metadata can be altered or stripped using standard command-line tools without modifying pixels.</li>
              <li>Social messaging platforms (WhatsApp, Signal, Telegram) automatically strip EXIF headers for privacy.</li>
              <li>Missing metadata is marked as missing and inconclusive, not inherently suspicious.</li>
            </ul>
          </div>
        </div>

        {/* Method B */}
        <div className="space-y-2 text-xs border-t border-slate-100 pt-4">
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#C5A059]" />
            <span>Test B: SHA-256 Evidence Integrity Verification (v1.0.0)</span>
          </h3>
          <p className="text-slate-700 leading-relaxed">
            Computes a 256-bit cryptographic digest directly from uploaded raw bytes. An integrity verification endpoint
            enables on-demand recomputation against stored vault bytes to detect physical bit rot or unauthorized storage alteration.
          </p>
          <div className="bg-slate-50 p-3 rounded border border-slate-200 text-slate-600 space-y-1">
            <strong>Important Principle:</strong>
            <p className="text-[11px]">
              A cryptographic hash guarantees byte-level preservation from the moment of upload. It does NOT establish that
              the image depicts a genuine real-world event, nor does it identify whether tampering occurred prior to capture.
            </p>
          </div>
        </div>

        {/* Method C */}
        <div className="space-y-2 text-xs border-t border-slate-100 pt-4">
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#C5A059]" />
            <span>Test C: Error Level Analysis (ELA) (v1.0.0)</span>
          </h3>
          <p className="text-slate-700 leading-relaxed">
            Re-compresses JPEG images at a calibrated standard quality baseline (Q=90) and computes the absolute pixel
            difference across 8x8 DCT macroblocks. Differences are scaled by an amplification factor (15x) to produce an
            exploratory residual heatmap.
          </p>
          <div className="bg-slate-50 p-3 rounded border border-slate-200 text-slate-600 space-y-1">
            <strong>Scientific Guardrails:</strong>
            <ul className="list-disc list-inside space-y-0.5 text-[11px]">
              <li>ELA is mathematically valid only for lossy discrete cosine transform (DCT) JPEG images.</li>
              <li>The test is honestly marked as unavailable/not applicable for PNG and WebP files.</li>
              <li>Bright regions in ELA heatmaps can arise from high-contrast textures, text, or sharp edges; they are NOT proof of tampering.</li>
            </ul>
          </div>
        </div>

        {/* Method D */}
        <div className="space-y-2 text-xs border-t border-slate-100 pt-4">
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#C5A059]" />
            <span>Test D: Basic Image Consistency Checks (v1.0.0)</span>
          </h3>
          <p className="text-slate-700 leading-relaxed">
            Inspects physical image geometry, aspect ratio anomalies, and color channel distributions. Utilizes a high-pass
            Laplacian operator to analyze spatial high-frequency noise variance across quadrants to detect severe noise asymmetry.
          </p>
        </div>
      </div>

      {/* Regulatory & Legal Alignment */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-3">
        <div className="flex items-center space-x-2 border-b border-slate-200 pb-3">
          <Scale className="w-5 h-5 text-[#0F1E36]" />
          <h2 className="text-base font-bold text-slate-900">
            Evidentiary Standards & Legal Framework Alignment
          </h2>
        </div>
        <div className="text-xs text-slate-700 space-y-2 leading-relaxed">
          <p>
            <strong>ISO/IEC 27037:2012:</strong> Guidelines for identification, collection, acquisition, and preservation of digital evidence.
            SATYA enforces non-invasive bitstream preservation, cryptographic integrity hashes, and immutable activity event logs.
          </p>
          <p>
            <strong>Section 65B Indian Evidence Act 1872 / Section 63 Bharatiya Sakshya Adhiniyam (BSA) 2023:</strong> Electronic
            evidence admissibility requires demonstration of system integrity, non-tampering during storage, and identifiable human
            responsibility. SATYA generates traceable examination records with explicit examiner attestation.
          </p>
        </div>
      </div>

      {/* Software Manifest */}
      <div className="bg-slate-100 rounded-xl p-4 border border-slate-200 text-xs font-mono text-slate-600 flex flex-wrap items-center justify-between gap-2">
        <div>
          <span>Application: SCSS SATYA v{versionData?.version || '1.0.0'}</span>
          <span className="mx-2">•</span>
          <span>Pipeline: v{versionData?.analysis_pipeline_version || '2026.1'}</span>
        </div>
        <div>
          <span>Organization: Sure Clue Scientific Solutions (SCSS)</span>
        </div>
      </div>
    </div>
  );
};
