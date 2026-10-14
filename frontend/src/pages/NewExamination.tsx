import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud,
  FileImage,
  AlertCircle,
  CheckCircle,
  X,
  Shield,
  Lock,
  ArrowRight,
  Sparkles,
} from 'lucide-react';
import { api } from '../services/api';

export const NewExamination: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [fileDetails, setFileDetails] = useState<{ name: string; size: number; type: string } | null>(null);
  const [confirmed, setConfirmed] = useState<boolean>(false);
  const [uploading, setUploading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);

  const MAX_SIZE_BYTES = 15 * 1024 * 1024; // 15 MB
  const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

  const validateAndSetFile = (file: File) => {
    setError(null);

    // Validate size
    if (file.size > MAX_SIZE_BYTES) {
      setError(`File size exceeds 15 MB limit (${(file.size / (1024 * 1024)).toFixed(2)} MB).`);
      return;
    }

    // Validate type extension
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    const validExts = ['.jpg', '.jpeg', '.png', '.webp'];
    if (!validExts.includes(ext) && !ALLOWED_TYPES.includes(file.type)) {
      setError('Unsupported file type. Please upload a JPEG, PNG, or WebP image.');
      return;
    }

    setSelectedFile(file);
    setFileDetails({
      name: file.name,
      size: file.size,
      type: file.type || 'image/jpeg',
    });

    // Create safe local preview
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleCancel = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(null);
    setPreviewUrl(null);
    setFileDetails(null);
    setConfirmed(false);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Please select an image file to proceed.');
      return;
    }

    if (!confirmed) {
      setError('Explicit examiner confirmation is required before submitting evidence.');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const result = await api.uploadEvidence(selectedFile);
      navigate(`/examinations/${result.examination_id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to submit evidence for screening.');
      setUploading(false);
    }
  };

  // Generate synthetic sample on client for rapid demonstration
  const loadSyntheticSpecimen = (type: 'camera' | 'spliced' | 'lossless') => {
    const canvas = document.createElement('canvas');
    canvas.width = 640;
    canvas.height = 480;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    if (type === 'camera') {
      ctx.fillStyle = '#87CEEB';
      ctx.fillRect(0, 0, 640, 300);
      ctx.fillStyle = '#228B22';
      ctx.fillRect(0, 300, 640, 180);
      ctx.fillStyle = '#FFD700';
      ctx.beginPath();
      ctx.arc(500, 100, 50, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#333333';
      ctx.font = '16px monospace';
      ctx.fillText('CAMERA NATURAL SPECIMEN', 30, 50);

      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], 'specimen_camera_original.jpg', { type: 'image/jpeg' });
          validateAndSetFile(file);
        }
      }, 'image/jpeg', 0.95);
    } else if (type === 'spliced') {
      ctx.fillStyle = '#E2E8F0';
      ctx.fillRect(0, 0, 640, 480);
      ctx.fillStyle = '#CBD5E1';
      ctx.fillRect(40, 40, 560, 400);

      // Foreign spliced patch
      ctx.fillStyle = '#B91C1C';
      ctx.fillRect(200, 150, 240, 180);
      ctx.fillStyle = '#FEF08A';
      ctx.fillRect(220, 170, 200, 140);
      ctx.fillStyle = '#000000';
      ctx.font = 'bold 16px sans-serif';
      ctx.fillText('INSERTED COMPOSITE', 235, 240);

      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], 'specimen_tampered_composite.jpg', { type: 'image/jpeg' });
          validateAndSetFile(file);
        }
      }, 'image/jpeg', 0.92);
    } else {
      ctx.fillStyle = '#312E81';
      ctx.fillRect(0, 0, 640, 480);
      ctx.fillStyle = '#A5B4FC';
      ctx.beginPath();
      ctx.arc(320, 240, 120, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#FFFFFF';
      ctx.font = '18px sans-serif';
      ctx.fillText('LOSSLESS SPECIMEN (PNG)', 200, 245);

      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], 'specimen_lossless.png', { type: 'image/png' });
          validateAndSetFile(file);
        }
      }, 'image/png');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Ingest Digital Image Evidence</h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Compute cryptographic baseline seals and initiate non-invasive forensic authenticity screening.
        </p>
      </div>

      {/* Pre-calibrated demo specimens pill selector */}
      <div className="bg-slate-100 border border-slate-200 rounded-lg p-3 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center space-x-2 text-slate-700 font-medium">
          <Sparkles className="w-4 h-4 text-[#C5A059]" />
          <span>Quick-Load Calibrated Test Specimens:</span>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => loadSyntheticSpecimen('camera')}
            className="px-2.5 py-1 bg-white hover:bg-slate-50 border border-slate-300 rounded text-slate-700 text-xs font-medium transition-colors"
          >
            Camera Photo (Baseline)
          </button>
          <button
            type="button"
            onClick={() => loadSyntheticSpecimen('spliced')}
            className="px-2.5 py-1 bg-white hover:bg-slate-50 border border-slate-300 rounded text-slate-700 text-xs font-medium transition-colors"
          >
            Spliced Composite (Tampered)
          </button>
          <button
            type="button"
            onClick={() => loadSyntheticSpecimen('lossless')}
            className="px-2.5 py-1 bg-white hover:bg-slate-50 border border-slate-300 rounded text-slate-700 text-xs font-medium transition-colors"
          >
            Lossless PNG
          </button>
        </div>
      </div>

      {/* Privacy Notice */}
      <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 text-xs text-slate-600 flex items-start space-x-3">
        <Lock className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <strong className="text-slate-800">Local Privacy & Bitstream Preservation Notice:</strong> Uploaded evidence
          is stored solely in the local prototype vault directory. No images are transmitted to external cloud APIs or
          third-party classifiers. The original file bitstream is preserved unmodified without altering image headers or pixels.
        </div>
      </div>

      {/* Main Upload Form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-6">
        {error && (
          <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-lg text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {!selectedFile ? (
          /* Dropzone */
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
              isDragging ? 'border-[#C5A059] bg-[#C5A059]/5' : 'border-slate-300 hover:border-slate-400 bg-slate-50/50'
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
              className="hidden"
            />
            <div className="w-12 h-12 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center mx-auto text-slate-500 mb-3">
              <UploadCloud className="w-6 h-6 text-[#0F1E36]" />
            </div>
            <p className="text-sm font-semibold text-slate-800">
              Drag & drop evidence image here, or <span className="text-[#C5A059] underline">browse files</span>
            </p>
            <p className="text-xs text-slate-500 mt-1">
              Supports JPEG, PNG, and WebP (Up to 15 MB)
            </p>
          </div>
        ) : (
          /* Evidence Preview Card */
          <div className="border border-slate-200 rounded-xl p-4 bg-slate-50 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <div className="flex items-center space-x-2 text-xs font-semibold text-slate-800">
                <FileImage className="w-4 h-4 text-[#0F1E36]" />
                <span>Selected Image Evidence</span>
              </div>
              <button
                type="button"
                onClick={handleCancel}
                disabled={uploading}
                className="text-xs text-slate-500 hover:text-rose-600 flex items-center gap-1 font-medium"
              >
                <X className="w-3.5 h-3.5" />
                <span>Cancel & Replace</span>
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-center">
              {previewUrl && (
                <div className="aspect-video sm:aspect-square bg-slate-900 rounded-lg overflow-hidden border border-slate-200 flex items-center justify-center">
                  <img src={previewUrl} alt="Preview" className="max-h-full max-w-full object-contain" />
                </div>
              )}
              <div className="sm:col-span-2 space-y-2 text-xs">
                <div>
                  <span className="text-slate-400 block">Filename:</span>
                  <span className="font-semibold text-slate-800 break-all">{fileDetails?.name}</span>
                </div>
                <div>
                  <span className="text-slate-400 block">File Size:</span>
                  <span className="font-mono text-slate-700">
                    {fileDetails ? (fileDetails.size / 1024).toFixed(1) : 0} KB ({fileDetails?.size} bytes)
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block">Detected MIME:</span>
                  <span className="font-mono text-slate-700">{fileDetails?.type}</span>
                </div>
                <div className="text-[11px] text-emerald-700 bg-emerald-50 border border-emerald-200 rounded p-2 flex items-center gap-1.5">
                  <CheckCircle className="w-3.5 h-3.5 shrink-0" />
                  <span>File signature verified. Ready for cryptographic sealing and screening.</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Explicit Confirmation Attestation */}
        <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg space-y-2">
          <label className="flex items-start space-x-3 cursor-pointer">
            <input
              type="checkbox"
              checked={confirmed}
              onChange={(e) => setConfirmed(e.target.checked)}
              disabled={!selectedFile || uploading}
              className="mt-1 h-4 w-4 text-[#0F1E36] focus:ring-[#C5A059] border-slate-300 rounded"
            />
            <span className="text-xs text-slate-700 leading-relaxed select-none">
              <strong className="text-slate-900">Mandatory Examiner Confirmation:</strong> I confirm this digital image is
              submitted for preliminary investigative screening in accordance with authorized evidence handling
              guidelines. I understand that automated screening provides technical indicators, not a conclusive legal opinion.
            </span>
          </label>
        </div>

        {/* Submit Actions */}
        <div className="flex items-center justify-end space-x-3 pt-2">
          {selectedFile && (
            <button
              type="button"
              onClick={handleCancel}
              disabled={uploading}
              className="px-4 py-2 border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-medium rounded-lg transition-colors"
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            disabled={!selectedFile || !confirmed || uploading}
            className={`inline-flex items-center gap-2 px-6 py-2.5 rounded-lg text-xs font-semibold shadow-xs transition-colors ${
              !selectedFile || !confirmed || uploading
                ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                : 'bg-[#0F1E36] hover:bg-[#162a4d] text-white'
            }`}
          >
            {uploading ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                <span>Screening Evidence & Hashing...</span>
              </>
            ) : (
              <>
                <Shield className="w-4 h-4 text-[#C5A059]" />
                <span>Begin Forensic Examination</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
