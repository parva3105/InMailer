import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Mail, Upload, FileText, LogOut, User, Settings } from 'lucide-react';

interface DashboardStats {
  template_count: number;
  emails_sent: number;
  orphaned_emails: number;
}

const Dashboard: React.FC = () => {
  const { user, signout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats>({ template_count: 0, emails_sent: 0, orphaned_emails: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchDashboardStats();
    }
  }, [user]);

  useEffect(() => {
    // Refresh stats when user returns to the dashboard tab/window
    const handleFocus = () => {
      if (user) {
        fetchDashboardStats();
      }
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [user]);

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      console.log('🔍 Fetching dashboard stats...');
      
      // Use the same endpoint that works for Mail Merge page
      const url = 'http://localhost:5000/api/templates';
      console.log('🔍 Making request to:', url);
      console.log('🔍 Full URL would be:', url);
      
      const response = await fetch(url, {
        credentials: 'include'
      });
      
      console.log('🔍 Response status:', response.status);
      console.log('🔍 Response headers:', Object.fromEntries(response.headers.entries()));
      
      if (response.ok) {
        const templates = await response.json();
        console.log('🔍 Templates response:', templates);
        console.log('🔍 Template count:', templates.length);
        
        // Get email stats separately
        const emailResponse = await fetch('/api/user/stats', {
          credentials: 'include'
        });
        
        let emailStats = { sent_emails: 0 };
        if (emailResponse.ok) {
          emailStats = await emailResponse.json();
          console.log('🔍 Email stats response:', emailStats);
        }
        
        // Update stats with template count from templates endpoint
        const newStats = {
          template_count: templates.length,
          emails_sent: emailStats.sent_emails || 0,
          orphaned_emails: 0 // We'll keep this as 0 for now since it's not critical
        };
        
        console.log('🔍 Setting new stats:', newStats);
        setStats(newStats);
      } else {
        console.error('Failed to fetch dashboard stats, status:', response.status);
        
        // Get the actual response to see what's being returned
        try {
          const responseText = await response.text();
          console.error('🔍 Response text (first 200 chars):', responseText.substring(0, 200));
          
          if (responseText.includes('<!DOCTYPE')) {
            console.error('❌ Server returned HTML instead of JSON - backend server might not be running or endpoint is wrong');
          }
        } catch (e) {
          console.error('Could not read error response:', e);
        }
      }
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    await signout();
    navigate('/');
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                <Mail className="w-5 h-5 text-blue-600" />
              </div>
              <h1 className="text-xl font-semibold text-gray-900">InMailer</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-blue-600" />
                </div>
                <div className="text-sm">
                  <p className="font-medium text-gray-900">{user.name}</p>
                  <p className="text-gray-500">{user.email}</p>
                </div>
              </div>
              
              <button
                onClick={handleSignOut}
                className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span>Sign Out</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Welcome back, {user.name}! 👋
          </h2>
          <p className="text-gray-600">
            You're one Mail away from you're tech breakthrough !
          </p>
        </div>

        {/* Quick Actions Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Create Template */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Create Template</h3>
            <p className="text-gray-600 mb-4">
              Design beautiful email templates with personalized variables and attachments.
            </p>
            <button
              onClick={() => navigate('/templates')}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Get Started
            </button>
          </div>

          {/* Start Mail Merge */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <Upload className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Start Mail Merge</h3>
            <p className="text-gray-600 mb-4">
              Upload your contact list and send personalized emails to multiple recipients.
            </p>
            <button
              onClick={() => navigate('/merge')}
              className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors"
            >
              Get Started
            </button>
          </div>

          {/* Send Test Email */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <Mail className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Send Test Email</h3>
            <p className="text-gray-600 mb-4">
              Test your email setup and templates before sending to your contact list.
            </p>
            <button
              onClick={() => navigate('/test-email')}
              className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors"
            >
              Send Test
            </button>
          </div>
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                  <FileText className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">Templates</p>
                  {loading ? (
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                  ) : (
                    <p className="text-2xl font-bold text-gray-900">{stats.template_count}</p>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
                <Mail className="w-5 h-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Emails Sent</p>
                {loading ? (
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600"></div>
                ) : (
                  <p className="text-2xl font-bold text-gray-900">{stats.emails_sent}</p>
                )}
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center mb-3">
              <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center mr-3">
                <FileText className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Orphaned Emails</p>
                {loading ? (
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-orange-600"></div>
                ) : (
                  <p className="text-2xl font-bold text-gray-900">{stats.orphaned_emails}</p>
                )}
              </div>
            </div>
            {!loading && stats.orphaned_emails > 0 && (
              <p className="text-xs text-orange-600 mt-2">
                Emails sent with deleted templates
              </p>
            )}
          </div>
        </div>
      </main>
      {/* Footer */}
      <footer className="mt-16 border-t border-gray-200 bg-white">
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

export default Dashboard;
