import React from 'react';
import { AlertTriangle, CheckCircle2, HelpCircle, XCircle, Clock, ShieldCheck, Search } from 'lucide-react';

interface IndicatorBadgeProps {
  indicator: 'indicator_detected' | 'no_indicator_detected' | 'inconclusive' | 'test_unavailable' | 'test_failed' | string;
  label?: string;
  size?: 'sm' | 'md';
}

export const IndicatorBadge: React.FC<IndicatorBadgeProps> = ({ indicator, label, size = 'md' }) => {
  const isSm = size === 'sm';
  const sizeClasses = isSm ? 'text-[11px] px-2 py-0.5' : 'text-xs px-2.5 py-1';
  const iconSize = isSm ? 'w-3 h-3' : 'w-3.5 h-3.5';

  switch (indicator) {
    case 'indicator_detected':
      return (
        <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-rose-50 text-rose-700 border border-rose-200 ${sizeClasses}`}>
          <AlertTriangle className={iconSize} />
          <span>{label || 'Indicator detected'}</span>
        </span>
      );
    case 'no_indicator_detected':
      return (
        <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 ${sizeClasses}`}>
          <CheckCircle2 className={iconSize} />
          <span>{label || 'No indicator detected by this test'}</span>
        </span>
      );
    case 'inconclusive':
      return (
        <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-amber-50 text-amber-700 border border-amber-200 ${sizeClasses}`}>
          <HelpCircle className={iconSize} />
          <span>{label || 'Inconclusive'}</span>
        </span>
      );
    case 'test_unavailable':
      return (
        <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-slate-100 text-slate-600 border border-slate-200 ${sizeClasses}`}>
          <HelpCircle className={iconSize} />
          <span>{label || 'Test unavailable'}</span>
        </span>
      );
    case 'test_failed':
    default:
      return (
        <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-red-50 text-red-600 border border-red-200 ${sizeClasses}`}>
          <XCircle className={iconSize} />
          <span>{label || 'Test failed'}</span>
        </span>
      );
  }
};

interface ReviewBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

export const ReviewBadge: React.FC<ReviewBadgeProps> = ({ status, size = 'md' }) => {
  const isSm = size === 'sm';
  const sizeClasses = isSm ? 'text-[11px] px-2 py-0.5' : 'text-xs px-2.5 py-1';
  const iconSize = isSm ? 'w-3 h-3' : 'w-3.5 h-3.5';

  switch (status) {
    case 'pending':
      return (
        <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-slate-100 text-slate-700 border border-slate-300 ${sizeClasses}`}>
          <Clock className={iconSize} />
          <span>Pending Review</span>
        </span>
      );
    case 'requires_further_examination':
      return (
        <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-amber-50 text-amber-800 border border-amber-300 ${sizeClasses}`}>
          <Search className={iconSize} />
          <span>Requires Further Examination</span>
        </span>
      );
    case 'reviewed_no_indicators':
      return (
        <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-emerald-50 text-emerald-800 border border-emerald-300 ${sizeClasses}`}>
          <ShieldCheck className={iconSize} />
          <span>Reviewed (No Indicators)</span>
        </span>
      );
    case 'reviewed_manipulation_suspected':
      return (
        <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-rose-50 text-rose-800 border border-rose-300 ${sizeClasses}`}>
          <AlertTriangle className={iconSize} />
          <span>Reviewed (Manipulation Suspected)</span>
        </span>
      );
    case 'reviewed_inconclusive':
      return (
        <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-sky-50 text-sky-800 border border-sky-300 ${sizeClasses}`}>
          <HelpCircle className={iconSize} />
          <span>Reviewed (Inconclusive)</span>
        </span>
      );
    default:
      return (
        <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-slate-100 text-slate-600 border border-slate-200 ${sizeClasses}`}>
          <span>{status.replace(/_/g, ' ')}</span>
        </span>
      );
  }
};
