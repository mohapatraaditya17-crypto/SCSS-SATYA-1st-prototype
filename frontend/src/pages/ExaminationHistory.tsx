import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Search,
  History,
  Eye,
  Download,
  RefreshCw,
} from 'lucide-react';
import { api } from '../services/api';
import type { ExaminationOverview } from '../types/examination';
import { ReviewBadge } from '../components/StatusBadge';

export const ExaminationHistory: React.FC = () => {
  const [examinations, setExaminations] = useState<ExaminationOverview[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState<string>('');
  const [reviewFilter, setReviewFilter] = useState<string>('');

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getExaminations({
        search: search.trim() || undefined,
        review_status: reviewFilter || undefined,
        limit: 100,
      });
      setExaminations(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load examination repository');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [reviewFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadData();
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Examination Vault Repository</h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Searchable historical archive of evidence screenings, cryptographic seals, and reviewer opinions.
          </p>
        </div>
        <button
          onClick={loadData}
          disabled={loading}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-300 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50 shadow-2xs self-start"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-4 space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by Case ID, Filename, or SHA-256 Digest..."
              className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-1 focus:ring-[#C5A059] focus:border-[#C5A059]"
            />
          </div>

          <div className="flex items-center space-x-2">
            <select
              value={reviewFilter}
              onChange={(e) => setReviewFilter(e.target.value)}
              className="px-3 py-2 border border-slate-300 rounded-lg text-xs bg-white focus:ring-1 focus:ring-[#C5A059]"
            >
              <option value="">All Review Statuses</option>
              <option value="pending">Pending Review</option>
              <option value="reviewed_no_indicators">Reviewed (No Indicators)</option>
              <option value="requires_further_examination">Requires Further Exam</option>
              <option value="reviewed_manipulation_suspected">Manipulation Suspected</option>
              <option value="reviewed_inconclusive">Inconclusive</option>
            </select>

            <button
              type="submit"
              className="px-4 py-2 bg-[#0F1E36] hover:bg-[#162a4d] text-white rounded-lg text-xs font-semibold shadow-xs"
            >
              Filter
            </button>
          </div>
        </form>
      </div>

      {/* History Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        {error && (
          <div className="p-4 bg-rose-50 text-rose-700 text-xs border-b border-rose-100 flex items-center justify-between">
            <span>{error}</span>
            <button onClick={loadData} className="underline font-semibold">Retry</button>
          </div>
        )}

        {examinations.length === 0 && !loading ? (
          <div className="p-12 text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center mx-auto text-slate-400">
              <History className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-semibold text-slate-800">No Historical Examinations Match</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              No examination records found matching the current search query or filter criteria.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
              <thead className="bg-slate-50 text-slate-600 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-3">Case ID</th>
                  <th className="px-6 py-3">Original Filename & Type</th>
                  <th className="px-6 py-3">SHA-256 Digest</th>
                  <th className="px-6 py-3">Uploaded (UTC)</th>
                  <th className="px-6 py-3">Review Status</th>
                  <th className="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {examinations.map((exam) => (
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
                    <td className="px-6 py-3 text-right space-x-2">
                      <Link
                        to={`/examinations/${exam.examination_id}`}
                        className="inline-flex items-center gap-1 text-[#0F1E36] hover:text-[#C5A059] font-medium bg-slate-100 hover:bg-slate-200 px-2.5 py-1 rounded transition-colors"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Inspect</span>
                      </Link>
                      <a
                        href={api.getReportPdfUrl(exam.examination_id)}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-slate-600 hover:text-slate-900 font-medium bg-slate-100 hover:bg-slate-200 px-2 py-1 rounded transition-colors"
                        title="Download PDF"
                      >
                        <Download className="w-3.5 h-3.5" />
                      </a>
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
