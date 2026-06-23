import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Plus, Edit3, Eye, Trash2, Paperclip } from 'lucide-react';
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

const TemplateList: React.FC = () => {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { fetchTemplates(); }, []);

  const fetchTemplates = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/templates`, { credentials: 'include' });
      if (!res.ok) throw new Error('Failed to fetch templates');
      setTemplates(await res.json());
    } catch {
      setError('Could not load templates. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number, name: string) => {
    if (!window.confirm(`Delete template "${name}"?`)) return;
    try {
      const res = await fetch(`${API_BASE_URL}/templates/${id}`, {
        method: 'DELETE',
        credentials: 'include',
      });
      if (!res.ok) {
        const err = await res.json();
        alert(`Failed to delete: ${err.error || 'Please try again.'}`);
        return;
      }
      setTemplates(prev => prev.filter(t => t.id !== id));
    } catch {
      alert('Error deleting template. Please try again.');
    }
  };

  const formatDate = (iso: string) =>
    new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

  return (
    <AppShell>
      <div className="app-container">
        {/* Page header */}
        <div className="page-header">
          <div>
            <h1 className="page-title">Templates</h1>
            <p className="page-description">Browse, create, and manage your email templates</p>
          </div>
          <button
            onClick={() => navigate('/templates/new')}
            className="btn-primary"
          >
            <Plus className="w-4 h-4" />
            New template
          </button>
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-24">
            <div className="spinner" />
          </div>
        )}

        {/* Error */}
        {error && !loading && (
          <div className="card p-8 text-center border-red-500/20">
            <p className="text-sm text-red-400 mb-4">{error}</p>
            <button onClick={fetchTemplates} className="btn-danger">Retry</button>
          </div>
        )}

        {/* Empty state */}
        {!loading && !error && templates.length === 0 && (
          <div className="card">
            <div className="empty-state">
              <div className="empty-state-icon">
                <FileText className="w-5 h-5" />
              </div>
              <p className="empty-state-title">No templates yet</p>
              <p className="empty-state-description mb-6">Create your first template to start sending personalized emails.</p>
              <button
                onClick={() => navigate('/templates/new')}
                className="btn-primary"
              >
                <Plus className="w-4 h-4" />
                Create template
              </button>
            </div>
          </div>
        )}

        {/* Template grid */}
        {!loading && !error && templates.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {templates.map(template => (
              <div key={template.id} className="card p-5 flex flex-col hover:border-white/15 transition-all duration-200">
                {/* Top row */}
                <div className="flex items-start justify-between mb-4">
                  <div className="w-8 h-8 rounded-lg bg-teal-400/10 border border-teal-300/20 flex items-center justify-center flex-shrink-0">
                    <FileText className="w-4 h-4 text-teal-300" />
                  </div>
                  <span className="text-xs text-zinc-600">{formatDate(template.created_at)}</span>
                </div>

                {/* Name & subject */}
                <h3 className="text-sm font-semibold text-zinc-200 truncate mb-1">{template.name}</h3>
                <p className="text-xs text-zinc-500 truncate mb-3">{template.subject}</p>

                {/* Meta */}
                <div className="flex items-center gap-2 flex-wrap mb-4">
                  <span className="badge-zinc">
                    {template.variables.length} var{template.variables.length !== 1 ? 's' : ''}
                  </span>
                  {template.attachment_name && (
                    <span className="badge-green gap-1">
                      <Paperclip className="w-3 h-3" />
                      attachment
                    </span>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 mt-auto pt-4 border-t border-white/[0.08]">
                  <button
                    onClick={() => navigate(`/templates/${template.id}`)}
                    className="flex-1 btn-ghost text-zinc-500 py-2 text-xs"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    View
                  </button>
                  <button
                    onClick={() => navigate(`/templates/${template.id}/edit`)}
                    className="flex-1 btn-secondary text-xs py-2 text-teal-300 border-teal-300/20 bg-teal-400/5 hover:bg-teal-400/10"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(template.id, template.name)}
                    className="p-2 rounded-lg text-zinc-600 hover:text-red-400 hover:bg-red-500/5 transition-all duration-150"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
};

export default TemplateList;
