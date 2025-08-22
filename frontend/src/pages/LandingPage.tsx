import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Upload, FileText } from 'lucide-react';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col">
      {/* Main Content - Centered */}
      <div className="flex-1 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full mx-4">
          <div className="text-center">
            <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Mail className="w-10 h-10 text-blue-600" />
            </div>
            
            <h1 className="text-3xl font-bold text-gray-900 mb-2">InMailer</h1>
            <p className="text-gray-600 mb-8">
              Create templates, upload CSV files, and send personalized emails in minutes.
            </p>
            
            <div className="space-y-3">
              <button
                onClick={() => navigate('/templates')}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
              >
                <FileText className="w-5 h-5" />
                Create Template
              </button>
              
              <button
                onClick={() => navigate('/merge')}
                className="w-full bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
              >
                <Upload className="w-5 h-5" />
                Start InMailer
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Footer - At Bottom */}
      <footer className="border-t border-gray-200 bg-white">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="text-center text-gray-600">
            <p className="text-sm">
              © 2024 Made by{' '}
              <a 
                href="https://www.linkedin.com/in/parva3105" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 font-medium transition-colors underline decoration-blue-300 hover:decoration-blue-600"
              >
                Parva Shah
              </a>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
