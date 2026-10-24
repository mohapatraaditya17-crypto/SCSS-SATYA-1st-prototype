import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { NewExamination } from './pages/NewExamination';
import { ExaminationResults } from './pages/ExaminationResults';
import { ExaminationHistory } from './pages/ExaminationHistory';
import { MethodologyAbout } from './pages/MethodologyAbout';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="app-shell">
        {/* Fixed sidebar navigation — Ea_code_ad design */}
        <Sidebar />

        {/* Main content area (offset by sidebar width via CSS) */}
        <div className="main-content">
          <Routes>
            <Route path="/"                   element={<Dashboard />} />
            <Route path="/new"                element={<NewExamination />} />
            <Route path="/examinations/:id"   element={<ExaminationResults />} />
            <Route path="/history"            element={<ExaminationHistory />} />
            <Route path="/methodology"        element={<MethodologyAbout />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
};

export default App;
