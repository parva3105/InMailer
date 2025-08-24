import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Mail, Upload, FileText, LogIn, UserPlus, Send, BarChart3, Users, Zap } from 'lucide-react';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  // If user is already authenticated, redirect to dashboard
  React.useEffect(() => {
    if (user) {
      navigate('/dashboard');
    }
  }, [user, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                <Mail className="w-5 h-5 text-blue-600" />
              </div>
              <h1 className="text-xl font-semibold text-gray-900">InMailer</h1>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => navigate('/signin')}
                className="flex items-center space-x-2 px-4 py-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <LogIn className="w-4 h-4" />
                <span>Sign In</span>
              </button>
              
              <button
                onClick={() => navigate('/signup')}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <UserPlus className="w-4 h-4" />
                <span>Sign Up</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="flex-1 flex items-center justify-center py-12">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-16">
            <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Mail className="w-10 h-10 text-blue-600" />
            </div>
            
            <h1 className="text-5xl font-bold text-gray-900 mb-4">InMailer</h1>
            <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              The simplest way to send personalized email outreach campaigns. Create templates, upload contacts, and track results - all in one place.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center max-w-md mx-auto">
              <button
                onClick={() => navigate('/signup')}
                className="bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 font-medium"
              >
                <UserPlus className="w-5 h-5" />
                Get Started Free
              </button>
              
              <button
                onClick={() => navigate('/signin')}
                className="bg-gray-100 text-gray-700 py-3 px-6 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center gap-2 font-medium"
              >
                <LogIn className="w-5 h-5" />
                Sign In
              </button>
            </div>
          </div>

          {/* How It Works Section */}
          <div className="bg-white rounded-3xl shadow-2xl p-8 md:p-12">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">How InMailer Works</h2>
              <p className="text-gray-600 text-lg max-w-2xl mx-auto">
                Send professional email campaigns in just 3 simple steps. No technical expertise required.
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {/* Step 1 */}
              <div className="text-center group">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <FileText className="w-8 h-8 text-white" />
                </div>
                <div className="bg-blue-50 rounded-xl p-6 h-full">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">1. Create Templates</h3>
                  <p className="text-gray-600 text-sm">
                    Design beautiful email templates with personalization variables like {'{name}'} and {'{company}'}.
                  </p>
                </div>
              </div>

              {/* Step 2 */}
              <div className="text-center group">
                <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <Upload className="w-8 h-8 text-white" />
                </div>
                <div className="bg-green-50 rounded-xl p-6 h-full">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">2. Upload Contacts</h3>
                  <p className="text-gray-600 text-sm">
                    Import your contact list via CSV file. Include names, emails, and any custom fields[UpComing] you want to use.
                  </p>
                </div>
              </div>

              {/* Step 3 */}
              <div className="text-center group">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <Send className="w-8 h-8 text-white" />
                </div>
                <div className="bg-purple-50 rounded-xl p-6 h-full">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">3. Send Mail</h3>
                  <p className="text-gray-600 text-sm">
                    Send your personalized email to your recruiter. Each recipient gets a customized message through Gmail.
                  </p>
                </div>
              </div>


            </div>

            {/* Features Highlight */}
            <div className="mt-12 pt-8 border-t border-gray-200">
              <div className="grid md:grid-cols-3 gap-6 text-center">
                <div className="flex flex-col items-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-3">
                    <Zap className="w-6 h-6 text-blue-600" />
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-1">Lightning Fast</h4>
                  <p className="text-gray-600 text-sm">Send hundreds of personalized emails in seconds</p>
                </div>
                
                <div className="flex flex-col items-center">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-3">
                    <Users className="w-6 h-6 text-green-600" />
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-1">Personal Touch</h4>
                  <p className="text-gray-600 text-sm">Every email is personalized with recipient data</p>
                </div>
                
                <div className="flex flex-col items-center">
                  <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mb-3">
                    <Mail className="w-6 h-6 text-purple-600" />
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-1">Gmail Integration</h4>
                  <p className="text-gray-600 text-sm">Sends through your Gmail account securely</p>
                </div>
              </div>
            </div>

            {/* CTA Section */}
            <div className="mt-12 text-center">
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Ready to get started?</h3>
                <p className="text-gray-600 mb-6 max-w-md mx-auto">
                  Join thousands of professionals who trust InMailer for their email outreach campaigns.
                </p>
                <button
                  onClick={() => navigate('/signup')}
                  className="bg-blue-600 text-white py-3 px-8 rounded-lg hover:bg-blue-700 transition-colors font-medium inline-flex items-center gap-2"
                >
                  <UserPlus className="w-5 h-5" />
                  Start Free Today
                </button>
              </div>
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
