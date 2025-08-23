import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Mail, Send, ArrowLeft, AlertCircle, CheckCircle } from 'lucide-react';
import axios from 'axios';

const TestEmail: React.FC = () => {
  const [formData, setFormData] = useState({
    to_email: '',
    subject: 'Test Email from InMailer',
    body: 'This is a test email to verify your email configuration is working properly.',
    attachment_path: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage(null);

    try {
      const response = await axios.post('/api/send-gmail', formData);
      
      setMessage({
        type: 'success',
        text: `Test email sent successfully! Message ID: ${response.data.message_id}`
      });
      
      // Clear form
      setFormData({
        to_email: '',
        subject: 'Test Email from InMailer',
        body: 'This is a test email to verify your email configuration is working properly.',
        attachment_path: ''
      });
      
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.response?.data?.error || 'Failed to send test email'
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <button
                onClick={() => navigate('/dashboard')}
                className="mr-4 p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              
              <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
                <Mail className="w-5 h-5 text-purple-600" />
              </div>
              <h1 className="text-xl font-semibold text-gray-900">Send Test Email</h1>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="text-sm text-gray-600">
                Logged in as <span className="font-medium text-gray-900">{user?.name}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Mail className="w-8 h-8 text-purple-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Send Test Email</h2>
            <p className="text-gray-600">
              Test your email configuration and templates before sending to your contact list.
            </p>
          </div>

          {/* Message */}
          {message && (
            <div className={`mb-6 p-4 rounded-lg flex items-center gap-3 ${
              message.type === 'success' 
                ? 'bg-green-50 border border-green-200' 
                : 'bg-red-50 border border-red-200'
            }`}>
              {message.type === 'success' ? (
                <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
              )}
              <p className={`text-sm ${
                message.type === 'success' ? 'text-green-700' : 'text-red-700'
              }`}>
                {message.text}
              </p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* To Email */}
            <div>
              <label htmlFor="to_email" className="block text-sm font-medium text-gray-700 mb-2">
                To Email Address
              </label>
              <input
                id="to_email"
                name="to_email"
                type="email"
                value={formData.to_email}
                onChange={handleInputChange}
                className="block w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors"
                placeholder="Enter recipient email address"
                required
              />
              <p className="mt-1 text-sm text-gray-500">
                Enter your own email address to test the system
              </p>
            </div>

            {/* Subject */}
            <div>
              <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-2">
                Subject Line
              </label>
              <input
                id="subject"
                name="subject"
                type="text"
                value={formData.subject}
                onChange={handleInputChange}
                className="block w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors"
                placeholder="Enter email subject"
                required
              />
            </div>

            {/* Body */}
            <div>
              <label htmlFor="body" className="block text-sm font-medium text-gray-700 mb-2">
                Email Body
              </label>
              <textarea
                id="body"
                name="body"
                rows={6}
                value={formData.body}
                onChange={handleInputChange}
                className="block w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors resize-none"
                placeholder="Enter email body content"
                required
              />
            </div>

            {/* Attachment Path (Optional) */}
            <div>
              <label htmlFor="attachment_path" className="block text-sm font-medium text-gray-700 mb-2">
                Attachment Path (Optional)
              </label>
              <input
                id="attachment_path"
                name="attachment_path"
                type="text"
                value={formData.attachment_path}
                onChange={handleInputChange}
                className="block w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors"
                placeholder="e.g., Templates/attachments/ParvaShah_Resume.pdf"
              />
              <p className="mt-1 text-sm text-gray-500">
                Leave empty for no attachment, or specify the path to an existing file
              </p>
            </div>

            {/* Submit Button */}
            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              
              <button
                type="submit"
                disabled={isLoading}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Sending...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Send Test Email
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Help Section */}
          <div className="mt-8 p-6 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">💡 Tips for Testing</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• Use your own email address to receive the test email</li>
              <li>• Check both your inbox and spam folder</li>
              <li>• Test with and without attachments to verify both scenarios</li>
              <li>• Verify that the email content and formatting are correct</li>
              <li>• Check that attachments open properly</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
};

export default TestEmail;
