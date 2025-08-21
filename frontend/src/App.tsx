import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import TemplateCreator from './pages/TemplateCreator';
import MailMerge from './pages/MailMerge';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <main>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/templates" element={<TemplateCreator />} />
            <Route path="/merge" element={<MailMerge />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
