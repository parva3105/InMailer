import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { CheckCircle, Loader } from 'lucide-react';

const AuthSuccess: React.FC = () => {
  const [searchParams] = useSearchParams();
  const { checkSession } = useAuth();
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const processOAuthSuccess = async () => {
      try {
        setIsProcessing(true);
        console.log('🔄 Starting OAuth success processing...');
        
        // Get email and name from URL params
        const email = searchParams.get('email');
        const name = searchParams.get('name');
        
        console.log('📧 Email from URL:', email);
        console.log('👤 Name from URL:', name);
        
        if (!email || !name) {
          setError('Missing authentication information');
          return;
        }

        // Wait a moment for the backend session to be established
        console.log('⏳ Waiting for backend session to be established...');
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Check if we have a valid session
        console.log('🔍 Checking session...');
        await checkSession();
        
        // Wait a bit more for the session to be fully established
        console.log('⏳ Final wait for session...');
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Redirect to dashboard
        console.log('🚀 Redirecting to dashboard...');
        navigate('/dashboard', { replace: true });
        
      } catch (err: any) {
        console.error('❌ OAuth processing error:', err);
        setError('Failed to complete authentication. Please try again.');
      } finally {
        setIsProcessing(false);
      }
    };

    processOAuthSuccess();
  }, [searchParams, checkSession, navigate]);

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-red-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Authentication Error</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => navigate('/signin')}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          {isProcessing ? (
            <Loader className="w-8 h-8 text-green-600 animate-spin" />
          ) : (
            <CheckCircle className="w-8 h-8 text-green-600" />
          )}
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          {isProcessing ? 'Completing Authentication...' : 'Authentication Successful!'}
        </h1>
        <p className="text-gray-600">
          {isProcessing 
            ? 'Please wait while we complete your sign-in process.'
            : 'Redirecting you to your dashboard...'
          }
        </p>
        
        {isProcessing && (
          <div className="mt-6">
            <div className="animate-pulse space-y-3">
              <div className="h-2 bg-gray-200 rounded w-3/4 mx-auto"></div>
              <div className="h-2 bg-gray-200 rounded w-1/2 mx-auto"></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuthSuccess;
