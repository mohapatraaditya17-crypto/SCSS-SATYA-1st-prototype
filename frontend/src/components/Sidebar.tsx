import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { api } from '../services/api';

interface NavItem {
  path: string;
  label: string;
  sublabel: string;
  icon: string;
  badgeKey?: string;
}

const NAV_ITEMS: NavItem[] = [
  { path: '/',            label: 'Dashboard',          sublabel: 'Overview & Stats',       icon: '◈' },
  { path: '/new',         label: 'New Examination',    sublabel: 'Submit Evidence',         icon: '⊕' },
  { path: '/history',     label: 'Examination Vault',  sublabel: 'Case Archive',            icon: '▦' },
  { path: '/methodology', label: 'Methodology',        sublabel: 'Algorithms & Science',    icon: '⊛' },
];

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const [engineStatus, setEngineStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [engineVersion, setEngineVersion] = useState<string>('1.0.0');
  const [pendingCount, setPendingCount] = useState<number>(0);

  useEffect(() => {
    api.getHealth()
      .then((data) => {
        setEngineStatus('online');
        setEngineVersion(data.version || '1.0.0');
      })
      .catch(() => setEngineStatus('offline'));

    api.getDashboardStats()
      .then((stats) => setPendingCount(stats.pending_review_count || 0))
      .catch(() => {});
  }, []);

  return (
    <aside className="sidebar" role="navigation" aria-label="Primary navigation">

      {/* Brand */}
      <Link to="/" className="brand">
        <div className="brand-mark" aria-hidden="true">S</div>
        <div>
          <strong>SCSS SATYA</strong>
          <small>Sure Clue Scientific Solutions</small>
        </div>
      </Link>

      {/* Workspace info */}
      <div className="workspace-label">
        FORENSIC WORKSPACE
        <span>v{engineVersion}</span>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => {
          const isActive = location.pathname === item.path ||
            (item.path === '/history' && location.pathname.startsWith('/examinations'));
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item${isActive ? ' active' : ''}`}
              aria-current={isActive ? 'page' : undefined}
            >
              <span className="nav-icon" aria-hidden="true">{item.icon}</span>
              <span>
                <span style={{ display: 'block', fontSize: 12 }}>{item.label}</span>
                <span style={{ display: 'block', fontSize: 9, color: 'var(--muted)', marginTop: 2 }}>
                  {item.sublabel}
                </span>
              </span>
              {item.path === '/history' && pendingCount > 0 && (
                <span className="nav-badge" aria-label={`${pendingCount} pending reviews`}>
                  {pendingCount}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div className="sidebar-bottom">
        {/* Engine status card */}
        <div className="system-card">
          <div className="system-top">
            <span className={engineStatus === 'online' ? 'pulse' : ''} aria-hidden="true" />
            <span>
              {engineStatus === 'online'
                ? 'Analysis Engine'
                : engineStatus === 'checking'
                ? 'Connecting…'
                : 'Engine Offline'}
            </span>
            <em>{engineStatus === 'online' ? 'LIVE' : engineStatus === 'checking' ? '…' : 'ERR'}</em>
          </div>
          <p>
            {engineStatus === 'online'
              ? `Pipeline v${engineVersion} • 15-test forensic suite active`
              : 'Attempting to reach SATYA analysis backend.'}
          </p>
        </div>

        {/* Examiner identity stub */}
        <div className="user-card">
          <div className="avatar" aria-hidden="true">EX</div>
          <div>
            <strong>Forensic Examiner</strong>
            <small>Human review required</small>
          </div>
        </div>
      </div>
    </aside>
  );
};
