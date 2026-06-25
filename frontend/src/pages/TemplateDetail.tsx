import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Edit3, Trash2, Paperclip } from 'lucide-react';
import AppShell from '../components/AppShell';

const API_BASE_URL = (process.env.REACT_APP_API_URL || 'https://inmailer.onrender.com') + '/api';

interface Template {
  id: number;
  name: string;
  subject: string;
  content: string;
  variables: string[];
  attachment_path?: string;
  attachment_name?: string;
  created_at: string;
  updated_at: string;
}

const TemplateDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [template, setTemplate] = useState<Template | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    setError(null);
    fetch(`${API_BASE_URL}/templates/${id}`, { credentials: 'include' })
      .then(res => {
        if (res.status === 404) { setNotFound(true); return null; }
        if (!res.ok) throw new Error('Failed to load template');
        return res.json();
      })
      .then(data => { if (data) setTemplate(data); })
      .catch(() => setError('Could not load template. Please try again.'))
      .finally(() => setLoading(false));
  }, [id]);

  const handleDelete = async () => {
    if (!template) return;
    if (!window.confirm(`Delete template "${template.name}"?`)) return;
    try {
      const res = await fetch(`${API_BASE_URL}/templates/${id}`, { method: 'DELETE', credentials: 'include' });
      if (!res.ok) {
        const err = await res.json();
        alert(`Failed to delete: ${err.error || 'Please try again.'}`);
        return;
      }
      navigate('/templates');
    } catch {
      alert('Error deleting template. Please try again.');
    }
  };

  const formatDate = (iso: string) =>
    new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

  return (
    <AppShell>
      <div className="app-container-narrow">
        {/* Back */}
        <div className="flex items-center gap-3 mb-8">
          <button
            onClick={() => navigate('/templates')}
            className="p-2 rounded-lg text-zinc-500 hover:text-zinc-200 hover:bg-white/[0.055] transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="page-title">Template detail</h1>
            <p className="page-description">View and manage this template</p>
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-24">
            <div className="spinner" />
          </div>
        )}

        {/* Not found */}
        {notFound && !loading && (
          <div className="card p-12 text-center">
            <p className="text-zinc-500 mb-4">Template not found.</p>
            <button onClick={() => navigate('/templates')} className="btn-secondary">
              Back to templates
            </button>
          </div>
        )}

        {/* Error */}
        {error && !loading && !notFound && (
          <div className="card p-8 text-center border-red-500/20">
            <p className="text-sm text-red-400 mb-4">{error}</p>
            <button onClick={() => window.location.reload()} className="btn-danger">Retry</button>
          </div>
        )}

        {/* Template content */}
        {!loading && !error && !notFound && template && (
          <div className="space-y-5">
            {/* Header card */}
            <div className="card p-6">
              <div className="flex items-start justify-between mb-6">
                <h2 className="text-xl font-semibold text-zinc-100">{template.name}</h2>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => navigate(`/templates/${template.id}/edit`)}
                    className="btn-secondary text-xs px-3 py-2 text-teal-300 border-teal-300/20 bg-teal-400/5 hover:bg-teal-400/10"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                    Edit
                  </button>
                  <button onClick={handleDelete} className="btn-danger text-xs px-3 py-2">
                    <Trash2 className="w-3.5 h-3.5" />
                    Delete
                  </button>
                </div>
              </div>

              {/* Meta */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <p className="text-xs text-zinc-600 uppercase tracking-wide font-medium mb-1.5">Subject</p>
                  <p className="text-sm text-zinc-300">{template.subject}</p>
                </div>
                <div>
                  <p className="text-xs text-zinc-600 uppercase tracking-wide font-medium mb-1.5">Created</p>
                  <p className="text-sm text-zinc-300">{formatDate(template.created_at)}</p>
                </div>

                {template.variables.length > 0 && (
                  <div className="sm:col-span-2">
                    <p className="text-xs text-zinc-600 uppercase tracking-wide font-medium mb-2">Variables</p>
                    <div className="flex flex-wrap gap-1.5">
                      {template.variables.map(v => (
                        <span
                          key={v}
                          className="px-2.5 py-1 rounded-full bg-teal-400/10 border border-teal-300/20 text-teal-300 text-xs font-mono font-medium"
                        >
                          {`\${${v}}`}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {template.attachment_name && (
                  <div className="sm:col-span-2">
                    <p className="text-xs text-zinc-600 uppercase tracking-wide font-medium mb-1.5">Attachment</p>
                    <div className="flex items-center gap-2 text-sm text-zinc-400">
                      <Paperclip className="w-3.5 h-3.5 text-zinc-600" />
                      {template.attachment_name}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Content card */}
            <div className="card p-6">
              <p className="text-xs text-zinc-600 uppercase tracking-wide font-medium mb-4">Content</p>
              <pre className="content-mono text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap bg-black/20 border border-white/[0.08] rounded-lg p-5 overflow-x-auto">
                {template.content}
              </pre>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
};

export default TemplateDetail;
