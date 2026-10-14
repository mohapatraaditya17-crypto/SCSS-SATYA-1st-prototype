import type {
  ExaminationDetail,
  ExaminationOverview,
  DashboardStats,
  IntegrityCheckResult,
} from '../types/examination';

const API_BASE = '/api';

export const api = {
  async getHealth(): Promise<{ status: string; version: string; pipeline_version: string }> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  },

  async getDashboardStats(): Promise<DashboardStats> {
    const res = await fetch(`${API_BASE}/dashboard/stats`);
    if (!res.ok) throw new Error('Failed to load dashboard statistics');
    return res.json();
  },

  async getExaminations(params?: {
    search?: string;
    status?: string;
    review_status?: string;
    limit?: number;
    offset?: number;
  }): Promise<ExaminationOverview[]> {
    const query = new URLSearchParams();
    if (params?.search) query.set('search', params.search);
    if (params?.status) query.set('status', params.status);
    if (params?.review_status) query.set('review_status', params.review_status);
    if (params?.limit) query.set('limit', params.limit.toString());
    if (params?.offset) query.set('offset', params.offset.toString());

    const url = `${API_BASE}/examinations${query.toString() ? '?' + query.toString() : ''}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to load examination history');
    return res.json();
  },

  async getExamination(id: string): Promise<ExaminationDetail> {
    const res = await fetch(`${API_BASE}/examinations/${encodeURIComponent(id)}`);
    if (!res.ok) {
      if (res.status === 404) throw new Error(`Examination '${id}' not found.`);
      throw new Error('Failed to retrieve examination details');
    }
    return res.json();
  },

  async uploadEvidence(file: File): Promise<ExaminationDetail> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/examinations`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Failed to screen image evidence');
    }

    return res.json();
  },

  async checkIntegrity(id: string): Promise<IntegrityCheckResult> {
    const res = await fetch(`${API_BASE}/examinations/${encodeURIComponent(id)}/integrity`);
    if (!res.ok) throw new Error('Integrity check request failed');
    return res.json();
  },

  async submitReview(
    id: string,
    reviewData: {
      reviewer_name: string;
      reviewer_designation: string;
      reviewer_organization?: string;
      decision: string;
      notes: string;
      attestation: boolean;
    }
  ): Promise<ExaminationDetail> {
    const res = await fetch(`${API_BASE}/examinations/${encodeURIComponent(id)}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reviewData),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to record review' }));
      throw new Error(err.detail || 'Failed to record human review');
    }

    return res.json();
  },

  getReportPdfUrl(id: string): string {
    return `${API_BASE}/examinations/${encodeURIComponent(id)}/report.pdf`;
  },

  getReportJsonUrl(id: string): string {
    return `${API_BASE}/examinations/${encodeURIComponent(id)}/report`;
  },

  getImageUrl(id: string): string {
    return `${API_BASE}/examinations/${encodeURIComponent(id)}/image`;
  },

  getVisualizationUrl(id: string, visType: string): string {
    return `${API_BASE}/examinations/${encodeURIComponent(id)}/visualizations/${encodeURIComponent(visType)}`;
  },
};
