import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Save, Plus, X, Upload, FileText, Trash2 } from 'lucide-react';
import AppShell from '../components/AppShell';

const API_BASE_URL = (process.env.REACT_APP_API_URL || 'https://inmailer.onrender.com') + '/api';

const TemplateCreator: React.FC = () => {
  const [templateName, setTemplateName] = useState('');
  const [subject, setSubject] = useState('');
  const [content, setContent] = useState('');
  const [variables, setVariables] = useState(['First_Name', 'Company']);
  const [newVariable, setNewVariable] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [selectedAttachment, setSelectedAttachment] = useState<File | null>(null);
  const [attachmentName, setAttachmentName] = useState<string>('');
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const editMode = !!id;

  useEffect(() => {
    if (id) {
      fetch(`${API_BASE_URL}/templates/${id}`, { credentials: 'include' })
        .then(res => res.json())
        .then(template => {
          setTemplateName(template.name);
          setSubject(template.subject);
          setContent(template.content);
          setVariables(template.variables || []);
          if (template.attachment_name) setAttachmentName(template.attachment_name);
        })
        .catch(err => console.error('Error loading template:', err));
    }
  }, [id]);

  const addVariable = () => {
    if (newVariable.trim() && !variables.includes(newVariable.trim())) {
      setVariables([...variables, newVariable.trim()]);
      setNewVariable('');
    }
  };

  const removeVariable = (index: number) => {
    setVariables(variables.filter((_, i) => i !== index));
  };

  const handleAttachmentUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        alert('File size too large. Please select a file smaller than 10MB.');
        return;
      }
      setSelectedAttachment(file);
      setAttachmentName(file.name);
    }
  };

  const removeAttachment = () => {
    setSelectedAttachment(null);
    setAttachmentName('');
  };

  const insertVariable = (variable: string) => {
    const textarea = document.getElementById('content') as HTMLTextAreaElement;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newContent = content.substring(0, start) + `\${${variable}}` + content.substring(end);
      setContent(newContent);
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(start + variable.length + 3, start + variable.length + 3);
      }, 0);
    }
  };

  const handleSave = async () => {
    if (!templateName.trim() || !subject.trim() || !content.trim()) {
      alert('Please fill in all fields');
      return;
    }
    setIsSaving(true);
    try {
      const url = editMode
        ? `${API_BASE_URL}/templates/${id}`
        : `${API_BASE_URL}/templates`;
      const method = editMode ? 'PUT' : 'POST';

      let response: Response;
      if (selectedAttachment) {
        const formData = new FormData();
        formData.append('name', templateName);
        formData.append('subject', subject);
        formData.append('content', content);
        formData.append('variables', JSON.stringify(variables));
        formData.append('file', selectedAttachment);
        response = await fetch(url, { method, credentials: 'include', body: formData });
      } else {
        response = await fetch(url, {
          method,
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ name: templateName, subject, content, variables }),
        });
      }

      if (response.ok) {
        navigate('/templates');
      } else {
        const error = await response.json();
        alert(`Error saving template: ${error.error}`);
      }
    } catch (error) {
      console.error('Error saving template:', error);
      alert('Error saving template. Please check if the backend server is running.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <AppShell>
      <div className="app-container-narrow">
        {/* Back + title */}
        <div className="flex items-center gap-3 mb-8">
          <button
            onClick={() => navigate('/templates')}
            className="p-2 rounded-lg text-zinc-500 hover:text-zinc-200 hover:bg-white/[0.055] transition-all duration-150"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="page-title">{editMode ? 'Edit template' : 'New template'}</h1>
            <p className="page-description">{editMode ? 'Update your email template' : 'Create a reusable email template'}</p>
          </div>
        </div>

        {/* Form */}
        <div className="space-y-6">
          {/* Template name */}
          <div className="card p-6">
            <div className="space-y-5">
              <div>
                <label className="form-label">Template name</label>
                <input
                  type="text"
                  value={templateName}
                  onChange={(e) => setTemplateName(e.target.value)}
                  className="input"
                  placeholder="e.g. Job Application - SWE"
                />
              </div>
              <div>
                <label className="form-label">Email subject</label>
                <input
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  className="input"
                  placeholder="e.g. Exploring opportunities at {Company}"
                />
              </div>
            </div>
          </div>

          {/* Variables */}
          <div className="card p-6">
            <label className="form-label">Dynamic variables</label>
            <p className="form-hint mb-4">Click a variable in your content area to insert it. Your CSV columns map to these variables.</p>
            <div className="flex flex-wrap gap-2 mb-4">
              {variables.map((variable, index) => (
                <div
                  key={index}
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-teal-400/10 border border-teal-300/20 text-teal-300 text-xs font-medium"
                >
                  <span className="font-mono">{`\${${variable}}`}</span>
                  <button
                    onClick={() => removeVariable(index)}
                    className="text-teal-400 hover:text-teal-200 transition-colors ml-0.5"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newVariable}
                onChange={(e) => setNewVariable(e.target.value)}
                className="input flex-1"
                placeholder="Add variable name..."
                onKeyPress={(e) => e.key === 'Enter' && addVariable()}
              />
              <button onClick={addVariable} className="btn-secondary">
                <Plus className="w-4 h-4" />
                Add
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="card p-6">
            <label className="form-label">Email content</label>
            <div className="mb-3">
              <p className="form-hint mb-2.5">Click a variable to insert it at your cursor position:</p>
              <div className="flex flex-wrap gap-2">
                {variables.map((variable) => (
                  <button
                    key={variable}
                    onClick={() => insertVariable(variable)}
                    className="px-2.5 py-1 rounded-md bg-white/[0.055] border border-white/10 text-zinc-400 text-xs font-mono
                               hover:bg-white/[0.08] hover:text-zinc-200 hover:border-white/15 transition-all duration-150"
                  >
                    {`\${${variable}}`}
                  </button>
                ))}
              </div>
            </div>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={14}
              className="input content-mono resize-y"
              placeholder={`Hi \${First_Name},\n\nI came across ${`\${Company}`} and was really impressed by your work in...\n\nBest regards,\n[Your name]`}
            />
          </div>

          {/* Attachment */}
          <div className="card p-6">
            <label className="form-label">Attachment (optional)</label>
            <p className="form-hint mb-4">
              Add a resume, portfolio, or document that will be automatically attached to every email sent with this template.
            </p>

            {editMode && attachmentName && !selectedAttachment && (
              <div className="mb-4 p-3 rounded-lg bg-teal-400/5 border border-teal-300/20">
                <p className="text-xs text-teal-300">
                  Current attachment: <span className="font-medium">{attachmentName}</span>
                </p>
                <p className="text-xs text-zinc-600 mt-0.5">Upload a new file to replace it, or leave empty to keep.</p>
              </div>
            )}

            {!selectedAttachment ? (
              <div className="upload-zone">
                <input
                  type="file"
                  accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
                  onChange={handleAttachmentUpload}
                  className="hidden"
                  id="attachment-upload"
                />
                <label htmlFor="attachment-upload" className="cursor-pointer flex flex-col items-center">
                  <div className="w-10 h-10 rounded-xl bg-white/[0.055] border border-white/10 flex items-center justify-center mb-3">
                    <Upload className="w-5 h-5 text-zinc-500" />
                  </div>
                  <p className="text-sm text-zinc-400 mb-1">
                    <span className="text-teal-300 font-medium">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-xs text-zinc-600">PDF, DOC, DOCX, TXT, Images - Max 10 MB</p>
                </label>
              </div>
            ) : (
              <div className="flex items-center justify-between p-4 rounded-lg bg-emerald-500/5 border border-emerald-500/20">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                    <FileText className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-zinc-200">{attachmentName}</p>
                    <p className="text-xs text-zinc-500">{(selectedAttachment.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                </div>
                <button
                  onClick={removeAttachment}
                  className="p-2 rounded-lg text-zinc-600 hover:text-red-400 hover:bg-red-500/5 transition-all"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>

          {/* Save */}
          <div className="flex items-center justify-between pt-2">
            <button
              onClick={() => navigate('/templates')}
              className="btn-ghost text-zinc-500"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="btn-primary px-6"
            >
              {isSaving ? (
                <>
                  <div className="spinner w-4 h-4" style={{ width: 16, height: 16, borderWidth: 2 }} />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  {editMode ? 'Update template' : 'Save template'}
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </AppShell>
  );
};

export default TemplateCreator;
