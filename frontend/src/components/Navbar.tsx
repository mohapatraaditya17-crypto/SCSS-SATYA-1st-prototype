import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShieldCheck, PlusCircle, History, BookOpen, Activity } from 'lucide-react';
import { api } from '../services/api';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const [engineStatus, setEngineStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [engineVersion, setEngineVersion] = useState<string>('1.0.0');

  useEffect(() => {
    api.getHealth()
      .then((data) => {
        setEngineStatus('online');
        setEngineVersion(data.version || '1.0.0');
      })
      .catch(() => setEngineStatus('offline'));
  }, []);

  const navLinks = [
    { path: '/', label: 'Dashboard', icon: Activity },
    { path: '/new', label: 'New Examination', icon: PlusCircle },
    { path: '/history', label: 'Examination Vault', icon: History },
    { path: '/methodology', label: 'Methodology & About', icon: BookOpen },
  ];

  return (
    <header className="bg-[#0F1E36] text-white border-b-2 border-[#C5A059] shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Info */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded bg-[#162a4d] border border-[#C5A059] flex items-center justify-center text-[#C5A059] shadow-inner">
              <ShieldCheck className="w-6 h-6 transition-transform group-hover:scale-105" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-wider text-white">SCSS SATYA</span>
                <span className="text-[10px] bg-[#C5A059]/20 text-[#D4AF37] px-1.5 py-0.5 rounded font-mono font-semibold border border-[#C5A059]/40">
                  FORENSIC TRIAGE
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                Sure Clue Scientific Solutions • Image Authenticity Screening
              </p>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="flex space-x-1 sm:space-x-2">
            {navLinks.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs sm:text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-[#1e3459] text-[#D4AF37] border-b-2 border-[#C5A059]'
                      : 'text-slate-300 hover:text-white hover:bg-[#162a4d]'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Engine Status Badge */}
          <div className="hidden lg:flex items-center space-x-2 bg-[#091322] px-3 py-1 rounded-full border border-slate-700/60 text-xs">
            <span
              className={`w-2 h-2 rounded-full ${
                engineStatus === 'online'
                  ? 'bg-emerald-400 animate-pulse'
                  : engineStatus === 'checking'
                  ? 'bg-amber-400'
                  : 'bg-rose-500'
              }`}
            />
            <span className="text-slate-400 font-mono">
              {engineStatus === 'online' ? `Engine v${engineVersion}` : 'Checking Engine...'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
