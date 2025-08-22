import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeft, Save, Plus, X, Upload, FileText, Trash2 } from 'lucide-react';

const API_BASE_URL = 'http://localhost:5000/api';

const TemplateCreator: React.FC = () => {
  const [templateName, setTemplateName] = useState('');
  const [subject, setSubject] = useState('');
  const [content, setContent] = useState('');
  const [variables, setVariables] = useState(['First_Name', 'Company']);
  const [newVariable, setNewVariable] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [selectedAttachment, setSelectedAttachment] = useState<File | null>(null);
  const [attachmentName, setAttachmentName] = useState<string>('');
  const [editMode, setEditMode] = useState(false);
  const [editingTemplateId, setEditingTemplateId] = useState<string>('');
  const navigate = useNavigate();
  const location = useLocation();

  // Check if we're in edit mode and populate form with existing template data
  useEffect(() => {
    if (location.state?.editMode && location.state?.template) {
      const template = location.state.template;
      setEditMode(true);
      setEditingTemplateId(template.id);
      setTemplateName(template.name);
      setSubject(template.subject);
      setContent(template.content);
      setVariables(template.variables || []);
      if (template.attachment_name) {
        setAttachmentName(template.attachment_name);
      }
    }
  }, [location.state]);

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
      // Check file size (limit to 10MB)
      const maxSize = 10 * 1024 * 1024; // 10MB
      if (file.size > maxSize) {
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
      
      // Set cursor position after the inserted variable
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
      let template;
      
      if (editMode) {
        // Update existing template
        let response;
        
        // If there's a new attachment, send as multipart form data
        if (selectedAttachment) {
          const formData = new FormData();
          formData.append('name', templateName);
          formData.append('subject', subject);
          formData.append('content', content);
          formData.append('variables', JSON.stringify(variables));
          formData.append('file', selectedAttachment);
          
          response = await fetch(`${API_BASE_URL}/templates/${editingTemplateId}`, {
            method: 'PUT',
            credentials: 'include', // Include session cookies
            body: formData,
          });
        } else {
          // No new attachment, send as JSON
          response = await fetch(`${API_BASE_URL}/templates/${editingTemplateId}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include', // Include session cookies
            body: JSON.stringify({
              name: templateName,
              subject: subject,
              content: content,
              variables: variables
            }),
          });
        }

        if (response.ok) {
          const result = await response.json();
          template = result.template; // Extract template from response
        } else {
          const error = await response.json();
          alert(`Error updating template: ${error.error}`);
          return;
        }
      } else {
        // Create new template
        let response;
        
        // If there's an attachment, send as multipart form data
        if (selectedAttachment) {
          const formData = new FormData();
          formData.append('name', templateName);
          formData.append('subject', subject);
          formData.append('content', content);
          formData.append('variables', JSON.stringify(variables));
          formData.append('file', selectedAttachment);
          
          response = await fetch(`${API_BASE_URL}/templates`, {
            method: 'POST',
            credentials: 'include', // Include session cookies
            body: formData,
          });
        } else {
          // No attachment, send as JSON
          response = await fetch(`${API_BASE_URL}/templates`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include', // Include session cookies
            body: JSON.stringify({
              name: templateName,
              subject: subject,
              content: content,
              variables: variables
            }),
          });
        }

        if (response.ok) {
          const result = await response.json();
          template = result.template;
        } else {
          const error = await response.json();
          alert(`Error saving template: ${error.error}`);
          return;
        }
      }
      
      // Show success message
      if (selectedAttachment) {
        alert(editMode ? 'Template with new attachment updated successfully!' : 'Template with attachment saved successfully!');
      } else if (editMode && attachmentName && !selectedAttachment) {
        // In edit mode, if there's an existing attachment and no new one selected, keep the existing
        console.log('🔍 Keeping existing attachment:', attachmentName);
        alert('Template updated successfully! Existing attachment preserved.');
      } else {
        console.log('🔍 No attachment to upload');
        alert(editMode ? 'Template updated successfully!' : 'Template saved successfully!');
      }
      
      navigate('/');
    } catch (error) {
      console.error('Error saving template:', error);
      alert('Error saving template. Please check if the backend server is running.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={() => navigate('/')}
            className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-3xl font-bold text-gray-900">
            {editMode ? 'Edit Email Template' : 'Create Email Template'}
          </h1>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          {/* Template Name */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Template Name
            </label>
            <input
              type="text"
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter template name"
            />
          </div>

          {/* Email Subject */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Subject
            </label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter email subject"
            />
          </div>

          {/* Variables Section */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Dynamic Variables
            </label>
            <div className="flex flex-wrap gap-2 mb-3">
              {variables.map((variable, index) => (
                <div
                  key={index}
                  className="flex items-center gap-2 bg-blue-100 text-blue-800 px-3 py-1 rounded-full"
                >
                  <span className="text-sm font-medium">{`\${${variable}}`}</span>
                  <button
                    onClick={() => removeVariable(index)}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newVariable}
                onChange={(e) => setNewVariable(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Add new variable"
                onKeyPress={(e) => e.key === 'Enter' && addVariable()}
              />
              <button
                onClick={addVariable}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Add
              </button>
            </div>
          </div>

          {/* Email Content */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Content
            </label>
            <div className="mb-3">
              <p className="text-sm text-gray-600 mb-2">Click on a variable to insert it into your content:</p>
              <p className="text-xs text-gray-500 mb-2">
                💡 Tip: Your CSV has columns "First Name" and "Company". Use $First_Name and $Company in your template.
              </p>
              <div className="flex flex-wrap gap-2">
                {variables.map((variable) => (
                  <button
                    key={variable}
                    onClick={() => insertVariable(variable)}
                    className="px-3 py-1 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors text-sm"
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
              rows={12}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              placeholder="Write your email content here. Use $VariableName to insert dynamic content."
            />
          </div>

          {/* Attachment Section */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Attachment (Optional)
            </label>
            <p className="text-sm text-gray-600 mb-3">
              Add a resume, portfolio, or any document that will be automatically attached to emails sent with this template.
            </p>
            
            {/* Show existing attachment if editing */}
            {editMode && attachmentName && !selectedAttachment && (
              <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-blue-800 text-sm">
                  📎 Current attachment: <span className="font-medium">{attachmentName}</span>
                </p>
                <p className="text-blue-700 text-xs mt-1">
                  Upload a new file to replace the current attachment, or leave empty to keep the existing one
                </p>
              </div>
            )}
            
            {!selectedAttachment ? (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                <input
                  type="file"
                  accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
                  onChange={handleAttachmentUpload}
                  className="hidden"
                  id="attachment-upload"
                />
                <label htmlFor="attachment-upload" className="cursor-pointer">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 mb-2">
                    <span className="font-medium text-blue-600">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-sm text-gray-500">PDF, DOC, DOCX, TXT, Images supported</p>
                </label>
              </div>
            ) : (
              <div className="border border-green-200 rounded-lg p-4 bg-green-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <FileText className="w-8 h-8 text-green-600" />
                    <div>
                      <p className="text-green-800 font-medium">{attachmentName}</p>
                      <p className="text-green-700 text-sm">
                        {(selectedAttachment.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={removeAttachment}
                    className="p-2 text-green-600 hover:text-green-800 hover:bg-green-100 rounded-lg transition-colors"
                    title="Remove attachment"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            )}
            
            <p className="text-xs text-gray-500 mt-2">
              💡 Tip: This attachment will be automatically included with every email sent using this template.
            </p>
            <p className="text-xs text-gray-500">
              📎 Supported formats: PDF, DOC, DOCX, TXT, JPG, JPEG, PNG (Max size: 10MB)
            </p>
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {isSaving ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  {editMode ? 'Update Template' : 'Save Template'}
                </>
              )}
            </button>
          </div>
        </div>
      </div>
      
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

export default TemplateCreator;
