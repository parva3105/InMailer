import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Send, Eye, Download, Trash2, Edit3, Calendar, CheckCircle, ChevronRight } from 'lucide-react';
import AppShell from '../components/AppShell';

const API_BASE_URL = (process.env.REACT_APP_API_URL || 'https://inmailer.onrender.com') + '/api';

interface Template {
  id: string;
  name: string;
  subject: string;
  content: string;
  variables: string[];
  attachment_path?: string;
  attachment_name?: string;
}

interface Contact {
  [key: string]: string;
}

interface PreviewResult {
  contact: Contact;
  subject: string;
  content: string;
  content_preview: string;
  status: string;
  error?: string;
  contact_summary: { name: string; email: string; company: string; };
}

const MailMerge: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [previewData, setPreviewData] = useState<PreviewResult[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [isLoadingTemplates, setIsLoadingTemplates] = useState(true);
  const [isScheduled, setIsScheduled] = useState(false);
  const [scheduledAt, setScheduledAt] = useState('');
  const [campaignName, setCampaignName] = useState('');
  const navigate = useNavigate();

  useEffect(() => { fetchTemplates(); }, []);

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/templates`, { credentials: 'include' });
      if (response.ok) setTemplates(await response.json());
    } catch (error) {
      console.error('Error fetching templates:', error);
    } finally {
      setIsLoadingTemplates(false);
    }
  };

  const deleteTemplate = async (templateId: string, templateName: string) => {
    if (!window.confirm(`Delete template "${templateName}"?`)) return;
    try {
      const response = await fetch(`${API_BASE_URL}/templates/${templateId}`, {
        method: 'DELETE',
        credentials: 'include',
      });
      if (response.ok) {
        setTemplates(prev => prev.filter(t => t.id !== templateId));
        if (selectedTemplate?.id === templateId) {
          setSelectedTemplate(null);
          setPreviewData([]);
        }
      } else {
        const errorData = await response.json();
        alert(`Failed to delete: ${errorData.error || 'Please try again.'}`);
      }
    } catch {
      alert('Error deleting template. Please try again.');
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'text/csv') {
      setSelectedFile(file);
      parseCSV(file);
    } else {
      alert('Please select a valid CSV file');
    }
  };

  const parseCSV = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const lines = text.split('\n');
      const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
      const data = lines.slice(1).filter(line => line.trim()).map(line => {
        const values = line.split(',').map(v => v.trim().replace(/"/g, ''));
        const contact: Contact = {};
        headers.forEach((header, index) => { contact[header] = values[index] || ''; });
        return contact;
      });
      setContacts(data);
      setPreviewData([]);
    };
    reader.readAsText(file);
  };

  const generatePreview = async () => {
    if (!selectedTemplate || contacts.length === 0) return;
    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append('template_id', selectedTemplate.id);
      formData.append('csv_file', selectedFile!);
      const response = await fetch(`${API_BASE_URL}/mail-merge`, {
        method: 'POST',
        credentials: 'include',
        body: formData,
      });
      if (response.ok) {
        const result = await response.json();
        setPreviewData(result.results);
      } else {
        const error = await response.json();
        alert(`Error generating preview: ${error.error}`);
      }
    } catch {
      alert('Error generating preview. Please check if the backend server is running.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSendEmails = async () => {
    if (!selectedTemplate || contacts.length === 0) {
      alert('Please select a template and upload contacts');
      return;
    }
    setIsProcessing(true);
    try {
      const response = await fetch(`${API_BASE_URL}/send-emails`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ template_id: selectedTemplate.id, contacts }),
      });
      if (response.ok) {
        alert(`Successfully processed ${contacts.length} emails!`);
        navigate('/dashboard');
      } else {
        const error = await response.json();
        if (error.action === 'reauth_required' || error.action === 'sign_in_required') {
          alert(`Authentication Error: ${error.error}\n\n${error.details || ''}\n\nPlease sign out and sign in again.`);
        } else {
          alert(`Error sending emails: ${error.error}`);
        }
      }
    } catch {
      alert('Error sending emails. Please check if the backend server is running.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleScheduleSend = async () => {
    if (!selectedTemplate || contacts.length === 0) { alert('Please select a template and upload contacts'); return; }
    if (!scheduledAt) { alert('Please select a scheduled send time'); return; }
    setIsProcessing(true);
    try {
      const response = await fetch(`${API_BASE_URL}/send-emails`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          template_id: selectedTemplate.id,
          contacts,
          scheduled_at: new Date(scheduledAt).toISOString(),
          campaign_name: campaignName || `Campaign – ${new Date(scheduledAt).toLocaleString()}`,
        }),
      });
      if (response.ok) {
        alert(`Campaign scheduled for ${new Date(scheduledAt).toLocaleString()}!`);
        navigate('/dashboard');
      } else {
        const error = await response.json();
        alert(`Error scheduling: ${error.error}`);
      }
    } catch {
      alert('Error scheduling send. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const downloadSampleCSV = () => {
    const sampleData = 'Name,Company,Email\nJohn Doe,Acme Corp,john@acme.com\nJane Smith,Tech Inc,jane@tech.com';
    const blob = new Blob([sampleData], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_contacts.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const Step = ({ n, label }: { n: string; label: string }) => (
    <div className="flex items-center gap-2 mb-4">
      <div className="w-6 h-6 rounded-full bg-indigo-500/15 border border-indigo-500/25 flex items-center justify-center flex-shrink-0">
        <span className="text-xs font-bold text-indigo-400">{n}</span>
      </div>
      <span className="text-sm font-semibold text-zinc-200">{label}</span>
    </div>
  );

  return (
    <AppShell>
      <div className="px-6 py-8 max-w-6xl mx-auto w-full">
        {/* Header */}
        <div className="mb-8">
          <h1 className="page-title">Mail Merge</h1>
          <p className="page-description">Upload contacts, select a template, and send personalized campaigns</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left column */}
          <div className="space-y-5">
            {/* CSV Upload */}
            <div className="card p-6">
              <Step n="1" label="Upload contacts" />

              {!selectedFile ? (
                <div className="upload-zone">
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="csv-upload"
                  />
                  <label htmlFor="csv-upload" className="cursor-pointer flex flex-col items-center">
                    <div className="w-10 h-10 rounded-xl bg-zinc-800 border border-zinc-700 flex items-center justify-center mb-3">
                      <Upload className="w-5 h-5 text-zinc-500" />
                    </div>
                    <p className="text-sm text-zinc-400 mb-1">
                      <span className="text-indigo-400 font-medium">Click to upload</span> or drag and drop
                    </p>
                    <p className="text-xs text-zinc-600">CSV files only</p>
                  </label>
                </div>
              ) : (
                <div className="flex items-center gap-3 p-4 rounded-lg bg-emerald-500/5 border border-emerald-500/20">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center flex-shrink-0">
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-zinc-200 truncate">{selectedFile.name}</p>
                    <p className="text-xs text-zinc-500">{contacts.length} contacts found</p>
                  </div>
                  <button
                    onClick={() => { setSelectedFile(null); setContacts([]); setPreviewData([]); }}
                    className="p-1.5 rounded text-zinc-600 hover:text-red-400 transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}

              <button
                onClick={downloadSampleCSV}
                className="mt-3 flex items-center gap-1.5 text-xs text-zinc-600 hover:text-indigo-400 transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                Download sample CSV format
              </button>
            </div>

            {/* Template Selection */}
            <div className="card p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-indigo-500/15 border border-indigo-500/25 flex items-center justify-center flex-shrink-0">
                    <span className="text-xs font-bold text-indigo-400">2</span>
                  </div>
                  <span className="text-sm font-semibold text-zinc-200">Select template</span>
                </div>
                <button
                  onClick={() => navigate('/templates/new')}
                  className="btn-secondary text-xs px-2.5 py-1.5"
                >
                  + New
                </button>
              </div>

              {isLoadingTemplates ? (
                <div className="flex items-center justify-center py-8">
                  <div className="spinner" />
                </div>
              ) : templates.length === 0 ? (
                <div className="empty-state py-8">
                  <div className="empty-state-icon">
                    <FileText className="w-5 h-5" />
                  </div>
                  <p className="empty-state-title text-sm">No templates</p>
                  <p className="empty-state-description text-xs mb-4">Create a template first</p>
                  <button
                    onClick={() => navigate('/templates/new')}
                    className="btn-primary text-xs px-3 py-2"
                  >
                    Create template
                  </button>
                </div>
              ) : (
                <div className="max-h-60 overflow-y-auto space-y-2 pr-1">
                  {templates.map((template) => (
                    <div
                      key={template.id}
                      className={`p-3.5 rounded-lg border cursor-pointer transition-all duration-150 ${
                        selectedTemplate?.id === template.id
                          ? 'border-indigo-500/40 bg-indigo-500/8'
                          : 'border-zinc-800 hover:border-zinc-700'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0" onClick={() => setSelectedTemplate(template)}>
                          <p className="text-sm font-medium text-zinc-200 truncate">{template.name}</p>
                          <p className="text-xs text-zinc-500 truncate mt-0.5">{template.subject}</p>
                          {template.attachment_name && (
                            <p className="text-xs text-emerald-500 mt-0.5">📎 {template.attachment_name}</p>
                          )}
                        </div>
                        <div className="flex items-center gap-1.5 ml-2">
                          {selectedTemplate?.id === template.id && (
                            <div className="w-4 h-4 rounded-full bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center">
                              <div className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
                            </div>
                          )}
                          <button
                            onClick={(e) => { e.stopPropagation(); navigate(`/templates/${template.id}/edit`); }}
                            className="p-1 rounded text-zinc-600 hover:text-indigo-400 hover:bg-indigo-500/5 transition-colors"
                          >
                            <Edit3 className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={(e) => { e.stopPropagation(); deleteTemplate(template.id, template.name); }}
                            className="p-1 rounded text-zinc-600 hover:text-red-400 hover:bg-red-500/5 transition-colors"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="card p-6">
              <Step n="3" label="Preview & send" />

              <div className="space-y-3">
                <button
                  onClick={generatePreview}
                  disabled={!selectedTemplate || contacts.length === 0 || isProcessing}
                  className="btn-secondary w-full"
                >
                  <Eye className="w-4 h-4" />
                  Generate preview
                </button>

                {!isScheduled && (
                  <button
                    onClick={handleSendEmails}
                    disabled={!selectedTemplate || contacts.length === 0 || isProcessing}
                    className="btn-success w-full"
                  >
                    {isProcessing ? (
                      <>
                        <div className="spinner w-4 h-4" style={{ width: 16, height: 16, borderWidth: 2, borderTopColor: 'white' }} />
                        Processing…
                      </>
                    ) : (
                      <>
                        <Send className="w-4 h-4" />
                        Send {contacts.length > 0 ? contacts.length : ''} emails
                      </>
                    )}
                  </button>
                )}

                {/* Schedule toggle */}
                <div className="rounded-lg border border-zinc-800 p-4">
                  <button
                    onClick={() => setIsScheduled(v => !v)}
                    className="flex items-center justify-between w-full mb-0"
                  >
                    <div className="flex items-center gap-2.5">
                      <Calendar className="w-4 h-4 text-zinc-500" />
                      <span className="text-sm font-medium text-zinc-300">Schedule for later</span>
                    </div>
                    <div className={`w-9 h-5 rounded-full border transition-colors duration-200 flex items-center px-0.5 ${isScheduled ? 'bg-indigo-600 border-indigo-500' : 'bg-zinc-800 border-zinc-700'}`}>
                      <div className={`w-4 h-4 bg-white rounded-full shadow-sm transition-transform duration-200 ${isScheduled ? 'translate-x-4' : 'translate-x-0'}`} />
                    </div>
                  </button>

                  {isScheduled && (
                    <div className="mt-4 space-y-3">
                      <div>
                        <label className="form-label text-xs">Campaign name (optional)</label>
                        <input
                          type="text"
                          placeholder="e.g. Q2 Outreach"
                          value={campaignName}
                          onChange={e => setCampaignName(e.target.value)}
                          className="input"
                        />
                      </div>
                      <div>
                        <label className="form-label text-xs">Send at</label>
                        <input
                          type="datetime-local"
                          value={scheduledAt}
                          min={new Date(Date.now() + 60000).toISOString().slice(0, 16)}
                          onChange={e => setScheduledAt(e.target.value)}
                          className="input"
                        />
                      </div>
                      <button
                        onClick={handleScheduleSend}
                        disabled={!selectedTemplate || contacts.length === 0 || !scheduledAt || isProcessing}
                        className="btn-primary w-full"
                      >
                        {isProcessing ? (
                          <><div className="spinner w-4 h-4" style={{ width: 16, height: 16, borderWidth: 2 }} /> Scheduling…</>
                        ) : (
                          <><Calendar className="w-4 h-4" /> Schedule {contacts.length > 0 ? contacts.length : ''} emails</>
                        )}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Right column — Preview */}
          <div className="card p-6 flex flex-col">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-sm font-semibold text-zinc-200">Preview</h2>
              {previewData.length > 0 && (
                <span className="badge-zinc">{previewData.length} of {contacts.length}</span>
              )}
            </div>

            {previewData.length > 0 && selectedTemplate && (
              <div className="mb-4 p-3 rounded-lg bg-indigo-500/5 border border-indigo-500/20">
                <p className="text-xs font-medium text-indigo-400">{selectedTemplate.name}</p>
                <p className="text-xs text-zinc-600 mt-0.5">Showing preview for first {previewData.length} contacts</p>
              </div>
            )}

            {previewData.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center text-center py-16">
                <div className="w-10 h-10 rounded-xl bg-zinc-800 border border-zinc-700 flex items-center justify-center mb-3">
                  <Eye className="w-5 h-5 text-zinc-600" />
                </div>
                <p className="text-sm text-zinc-500">Upload a CSV and select a template, then generate a preview</p>
              </div>
            ) : (
              <div className="flex-1 overflow-y-auto space-y-3 pr-1">
                {previewData.map((result, index) => {
                  const contactName = result.contact_summary?.name || result.contact?.First_Name || result.contact?.first_name || result.contact?.Name || result.contact?.name || 'Unknown';
                  const contactEmail = result.contact_summary?.email || result.contact?.Email || result.contact?.email || 'No email';
                  const contactCompany = result.contact_summary?.company || result.contact?.Company || result.contact?.company || '';
                  const subject = result.subject || 'No subject';
                  const contentPreview = result.content_preview || result.content?.substring(0, 150) + '...' || 'No content';

                  return (
                    <div key={index} className="rounded-lg border border-zinc-800 p-4 hover:border-zinc-700 transition-colors">
                      {/* Contact header */}
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <p className="text-sm font-medium text-zinc-200">{contactName}</p>
                          <p className="text-xs text-zinc-500 mt-0.5">{contactEmail}</p>
                          {contactCompany && (
                            <p className="text-xs text-indigo-400 mt-0.5">{contactCompany}</p>
                          )}
                        </div>
                        <span className={`badge text-xs ${result.status === 'preview' ? 'badge-indigo' : 'badge-zinc'}`}>
                          {result.status}
                        </span>
                      </div>

                      {/* Subject */}
                      <div className="mb-2.5 px-3 py-2 rounded-md bg-zinc-950/60 border border-zinc-800">
                        <p className="text-xs text-zinc-600 mb-0.5 uppercase tracking-wide">Subject</p>
                        <p className="text-xs font-medium text-zinc-300">{subject}</p>
                      </div>

                      {/* Preview */}
                      <div className="px-3 py-2 rounded-md bg-zinc-950/60 border border-zinc-800">
                        <p className="text-xs text-zinc-600 mb-1 uppercase tracking-wide">Preview</p>
                        <p className="text-xs text-zinc-400 leading-relaxed whitespace-pre-line">{contentPreview}</p>
                      </div>

                      {selectedTemplate?.attachment_name && (
                        <div className="mt-2.5 flex items-center gap-1.5 text-xs text-emerald-500">
                          <span>📎</span> {selectedTemplate.attachment_name}
                        </div>
                      )}
                    </div>
                  );
                })}

                {contacts.length > previewData.length && (
                  <div className="flex items-center gap-2 py-3 text-xs text-zinc-600">
                    <ChevronRight className="w-3.5 h-3.5" />
                    and {contacts.length - previewData.length} more contacts
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
};

export default MailMerge;
