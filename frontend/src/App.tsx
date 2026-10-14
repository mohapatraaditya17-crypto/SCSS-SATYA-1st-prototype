import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { Dashboard } from './pages/Dashboard';
import { NewExamination } from './pages/NewExamination';
import { ExaminationResults } from './pages/ExaminationResults';
import { ExaminationHistory } from './pages/ExaminationHistory';
import { MethodologyAbout } from './pages/MethodologyAbout';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/new" element={<NewExamination />} />
            <Route path="/examinations/:id" element={<ExaminationResults />} />
            <Route path="/history" element={<ExaminationHistory />} />
            <Route path="/methodology" element={<MethodologyAbout />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
};

export default App;
