import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldCheck,
  PlusCircle,
  FileText,
  Clock,
  CheckCircle,
  AlertTriangle,
  ArrowRight,
  RefreshCw,
  FolderOpen,
  Eye,
} from 'lucide-react';
import { api } from '../services/api';
import type { DashboardStats, ExaminationOverview } from '../types/examination';
import { ReviewBadge } from '../components/StatusBadge';

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentExams, setRecentExams] = useState<ExaminationOverview[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, examsData] = await Promise.all([
        api.getDashboardStats(),
        api.getExaminations({ limit: 10 }),
      ]);
      setStats(statsData);
      setRecentExams(examsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Platform Banner */}
      <div className="bg-gradient-to-r from-[#0F1E36] to-[#1E3459] text-white rounded-xl p-6 sm:p-8 shadow-sm border border-[#C5A059]/40 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="max-w-2xl">
          <div className="flex items-center space-x-2 text-[#D4AF37] text-xs font-semibold uppercase tracking-wider mb-2">
            <span>SEVA FIRST Innovation Challenge 2026</span>
            <span>•</span>
            <span>Emerging Technologies (Sector 9)</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mb-2">
            SCSS SATYA Digital Forensics Screening Platform
          </h1>
          <p className="text-slate-300 text-sm leading-relaxed mb-4">
            A scientifically grounded, explainable digital image screening platform for forensic laboratories,
            insurance investigators, and legal triage. Provides passive-blind non-invasive screening,
            SHA-256 evidence integrity baselines, and qualified human review certification.
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <Link
              to="/new"
              className="inline-flex items-center gap-2 bg-[#C5A059] hover:bg-[#b38f48] text-[#0F1E36] font-semibold text-sm px-4 py-2 rounded-lg shadow transition-colors"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Start New Examination</span>
            </Link>
            <Link
              to="/methodology"
              className="inline-flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white text-sm px-4 py-2 rounded-lg border border-white/20 transition-colors"
            >
              <span>Explore Methodology & Limitations</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>

        {/* Doctrine Card */}
        <div className="bg-[#091322]/80 border border-[#C5A059]/50 rounded-lg p-4 w-full md:w-72 shrink-0 text-xs text-slate-300 space-y-2">
          <div className="flex items-center space-x-2 text-[#D4AF37] font-semibold uppercase tracking-wide">
            <ShieldCheck className="w-4 h-4" />
            <span>Forensic Doctrine</span>
          </div>
          <p className="font-serif italic text-amber-100 text-sm">
            "The tool screens. The expert decides."
          </p>
          <p className="text-slate-400 text-[11px] leading-normal">
            Automated screening output serves as triage assistance, never conclusive legal proof.
          </p>
        </div>
      </div>

      {/* Mandatory Statutory Notice */}
      <div className="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-lg shadow-xs flex items-start space-x-3">
        <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <div className="text-xs text-amber-800 leading-relaxed">
          <strong className="font-semibold">Notice for Forensic Examiners:</strong> This software prototype provides
          preliminary algorithmic screening only. The absence of detected manipulation indicators does not establish that
          an image is authentic. All findings must be corroborated by certified human forensic examiners alongside physical
          evidence and contextual chain of custody.
        </div>
      </div>

      {/* Operational Metrics Cards (Derived from real DB records) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Total Examinations</span>
            <FolderOpen className="w-4 h-4 text-[#0F1E36]" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {loading ? '—' : stats?.total_examinations ?? 0}
          </div>
          <p className="text-[11px] text-slate-500">
            {loading ? '...' : `${stats?.recent_examinations_count ?? 0} ingested in last 24h`}
          </p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Pending Human Review</span>
            <Clock className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-bold text-amber-700">
            {loading ? '—' : stats?.pending_review_count ?? 0}
          </div>
          <p className="text-[11px] text-slate-500">Awaiting examiner assessment</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Examiner Reviewed</span>
            <CheckCircle className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-emerald-700">
            {loading ? '—' : stats?.reviewed_count ?? 0}
          </div>
          <p className="text-[11px] text-slate-500">Formally attested by examiner</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Reports Generated</span>
            <FileText className="w-4 h-4 text-[#C5A059]" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {loading ? '—' : stats?.reports_generated_count ?? 0}
          </div>
          <p className="text-[11px] text-slate-500">ISO/IEC 27037 compliant records</p>
        </div>
      </div>

      {/* Recent Examinations Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/60">
          <div>
            <h2 className="text-base font-semibold text-slate-900">Recent Evidence Ingestions</h2>
            <p className="text-xs text-slate-500">Stored local prototype records with cryptographic digests</p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={loadData}
              disabled={loading}
              className="p-1.5 text-slate-500 hover:text-slate-800 rounded border border-slate-200 hover:bg-white text-xs inline-flex items-center gap-1"
              title="Refresh records"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">Refresh</span>
            </button>
            <Link
              to="/history"
              className="text-xs font-medium text-[#0F1E36] hover:text-[#C5A059] flex items-center gap-1"
            >
              <span>View All</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-rose-50 text-rose-700 text-xs border-b border-rose-100 flex items-center justify-between">
            <span>{error}</span>
            <button onClick={loadData} className="underline font-semibold">Retry</button>
          </div>
        )}

        {recentExams.length === 0 && !loading ? (
          <div className="p-12 text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center mx-auto text-slate-400">
              <FolderOpen className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-semibold text-slate-800">No Examination Records Ingested Yet</h3>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
              Start by uploading a digital image evidence file to run cryptographic hashing and the 4-layer
              screening pipeline.
            </p>
            <Link
              to="/new"
              className="inline-flex items-center gap-2 bg-[#0F1E36] hover:bg-[#162a4d] text-white text-xs font-medium px-4 py-2 rounded-md shadow-xs transition-colors"
            >
              <PlusCircle className="w-4 h-4 text-[#C5A059]" />
              <span>Begin First Examination</span>
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
              <thead className="bg-slate-50 text-slate-600 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-3">Case ID</th>
                  <th className="px-6 py-3">Filename & Dimensions</th>
                  <th className="px-6 py-3">SHA-256 Digest</th>
                  <th className="px-6 py-3">Ingested At (UTC)</th>
                  <th className="px-6 py-3">Human Review Status</th>
                  <th className="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {recentExams.map((exam) => (
                  <tr key={exam.examination_id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-3 font-mono font-medium text-[#0F1E36]">
                      <Link to={`/examinations/${exam.examination_id}`} className="hover:underline">
                        {exam.examination_id}
                      </Link>
                    </td>
                    <td className="px-6 py-3">
                      <div className="font-medium text-slate-800">{exam.original_filename}</div>
                      <div className="text-[11px] text-slate-400">
                        {exam.image_width}x{exam.image_height} px • {(exam.file_size_bytes / 1024).toFixed(1)} KB • {exam.detected_media_type}
                      </div>
                    </td>
                    <td className="px-6 py-3 font-mono text-[11px] text-slate-600 max-w-[140px] truncate" title={exam.sha256_digest}>
                      {exam.sha256_digest.substring(0, 16)}...
                    </td>
                    <td className="px-6 py-3 text-slate-600">
                      {new Date(exam.upload_timestamp).toLocaleString('en-US', { timeZone: 'UTC', hour12: false })}
                    </td>
                    <td className="px-6 py-3">
                      <ReviewBadge status={exam.human_review_status} size="sm" />
                    </td>
                    <td className="px-6 py-3 text-right">
                      <Link
                        to={`/examinations/${exam.examination_id}`}
                        className="inline-flex items-center gap-1 text-[#0F1E36] hover:text-[#C5A059] font-medium bg-slate-100 hover:bg-slate-200 px-2.5 py-1 rounded transition-colors"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Inspect</span>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
