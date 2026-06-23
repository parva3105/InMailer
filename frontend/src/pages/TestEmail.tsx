import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Send, AlertCircle, CheckCircle } from 'lucide-react';
import axios from 'axios';
import AppShell from '../components/AppShell';

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
    <AppShell>
      <div className="px-6 py-8 max-w-2xl mx-auto w-full">
        {/* Header */}
        <div className="mb-8">
          <h1 className="page-title">Test Email</h1>
          <p className="page-description">
            Verify your setup and templates before sending to your contact list
          </p>
        </div>

        {/* Form card */}
        <div className="card p-6">
          {/* Sending as */}
          <div className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg bg-zinc-800/60 border border-zinc-700/50 mb-6">
            <div className="w-6 h-6 rounded-full bg-indigo-500/15 border border-indigo-500/25 flex items-center justify-center flex-shrink-0">
              <span className="text-xs font-bold text-indigo-400">
                {user?.name?.charAt(0)?.toUpperCase() ?? 'U'}
              </span>
            </div>
            <div>
              <span className="text-xs text-zinc-600">Sending as </span>
              <span className="text-xs font-medium text-zinc-300">{user?.name}</span>
            </div>
          </div>

          {/* Status message */}
          {message && (
            <div className={`mb-6 p-3.5 rounded-lg flex items-start gap-3 border ${
              message.type === 'success'
                ? 'bg-emerald-500/8 border-emerald-500/20'
                : 'bg-red-500/8 border-red-500/20'
            }`}>
              {message.type === 'success' ? (
                <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
              ) : (
                <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
              )}
              <p className={`text-xs leading-relaxed ${
                message.type === 'success' ? 'text-emerald-400' : 'text-red-400'
              }`}>
                {message.text}
              </p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="to_email" className="form-label">Recipient email</label>
              <input
                id="to_email"
                name="to_email"
                type="email"
                value={formData.to_email}
                onChange={handleInputChange}
                className="input"
                placeholder="Enter recipient email address"
                required
              />
              <p className="form-hint">Enter your own email address to test the system</p>
            </div>

            <div>
              <label htmlFor="subject" className="form-label">Subject</label>
              <input
                id="subject"
                name="subject"
                type="text"
                value={formData.subject}
                onChange={handleInputChange}
                className="input"
                placeholder="Enter email subject"
                required
              />
            </div>

            <div>
              <label htmlFor="body" className="form-label">Email body</label>
              <textarea
                id="body"
                name="body"
                rows={7}
                value={formData.body}
                onChange={handleInputChange}
                className="input content-mono resize-none"
                placeholder="Enter email body content"
                required
              />
            </div>

            <div>
              <label htmlFor="attachment_path" className="form-label">
                Attachment path
                <span className="ml-2 text-xs text-zinc-600 font-normal">(optional)</span>
              </label>
              <input
                id="attachment_path"
                name="attachment_path"
                type="text"
                value={formData.attachment_path}
                onChange={handleInputChange}
                className="input"
                placeholder="e.g. Templates/attachments/resume.pdf"
              />
              <p className="form-hint">Leave empty for no attachment, or specify the path to an existing file</p>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-2 border-t border-zinc-800">
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="btn-ghost text-zinc-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary px-6"
              >
                {isLoading ? (
                  <>
                    <div className="spinner w-4 h-4" style={{ width: 16, height: 16, borderWidth: 2 }} />
                    Sending…
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Send test email
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Tips */}
        <div className="mt-5 card p-5">
          <p className="text-xs font-semibold text-zinc-400 uppercase tracking-wide mb-3">Tips for testing</p>
          <ul className="space-y-2">
            {[
              'Use your own email address to receive the test',
              'Check both inbox and spam folder',
              'Test with and without attachments',
              'Verify email content and formatting look correct',
              'Ensure attachments open correctly',
            ].map((tip) => (
              <li key={tip} className="flex items-start gap-2.5 text-xs text-zinc-500">
                <div className="w-1.5 h-1.5 rounded-full bg-zinc-700 mt-1.5 flex-shrink-0" />
                {tip}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </AppShell>
  );
};

export default TestEmail;
