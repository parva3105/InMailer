import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import LandingPage from './pages/LandingPage';
import SignIn from './pages/SignIn';
import SignUp from './pages/SignUp';
import Dashboard from './pages/Dashboard';
import TemplateCreator from './pages/TemplateCreator';
import MailMerge from './pages/MailMerge';
import TestEmail from './pages/TestEmail';
import AuthSuccess from './pages/AuthSuccess';
import { Analytics } from "@vercel/analytics/react"

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <main>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/signin" element={<SignIn />} />
              <Route path="/signup" element={<SignUp />} />
              <Route path="/auth/success" element={<AuthSuccess />} />
              
              {/* Protected Routes */}
              <Route path="/dashboard" element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } />
              <Route path="/templates" element={
                <ProtectedRoute>
                  <TemplateCreator />
                </ProtectedRoute>
              } />
              <Route path="/merge" element={
                <ProtectedRoute>
                  <MailMerge />
                </ProtectedRoute>
              } />
              <Route path="/test-email" element={
                <ProtectedRoute>
                  <TestEmail />
                </ProtectedRoute>
              } />
            </Routes>
            <Analytics />
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
