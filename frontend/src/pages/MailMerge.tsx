import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Upload, FileText, Send, Eye, Download, Trash2, Edit3 } from 'lucide-react';

const API_BASE_URL = 'http://localhost:5000/api';

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
  contact_summary: {
    name: string;
    email: string;
    company: string;
  };
}

const MailMerge: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [previewData, setPreviewData] = useState<PreviewResult[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [isLoadingTemplates, setIsLoadingTemplates] = useState(true);
  const navigate = useNavigate();

  // Load templates from backend
  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/templates`, {
        credentials: 'include' // Include session cookies
      });
      if (response.ok) {
        const data = await response.json();
        setTemplates(data);
      } else {
        console.error('Failed to fetch templates');
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    } finally {
      setIsLoadingTemplates(false);
    }
  };

  const deleteTemplate = async (templateId: string, templateName: string) => {
    if (window.confirm(`Are you sure you want to delete the template "${templateName}"?`)) {
      try {
        const response = await fetch(`${API_BASE_URL}/templates/${templateId}`, {
          method: 'DELETE',
          credentials: 'include', // Include session cookies
        });
        
        if (response.ok) {
          // Remove template from local state
          setTemplates(prev => prev.filter(t => t.id !== templateId));
          
          // If the deleted template was selected, clear selection
          if (selectedTemplate?.id === templateId) {
            setSelectedTemplate(null);
          }
          
          // Clear preview data if it was for the deleted template
          if (selectedTemplate?.id === templateId) {
            setPreviewData([]);
          }
          
          console.log('Template deleted successfully');
        } else {
          console.error('Failed to delete template');
          alert('Failed to delete template. Please try again.');
        }
      } catch (error) {
        console.error('Error deleting template:', error);
        alert('Error deleting template. Please try again.');
      }
    }
  };

  const editTemplate = (template: Template) => {
    console.log('🔍 Edit template called with:', template);
    console.log('🔍 Template ID in editTemplate:', template.id, 'Type:', typeof template.id);
    
    // Navigate to template creator with template data
    navigate('/templates', { 
      state: { 
        editMode: true, 
        template: template 
      } 
    });
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
        headers.forEach((header, index) => {
          contact[header] = values[index] || '';
        });
        return contact;
      });
      setContacts(data);
      // Clear preview data when new CSV is uploaded
      setPreviewData([]);
    };
    reader.readAsText(file);
  };

  const handleTemplateSelect = (template: Template) => {
    setSelectedTemplate(template);
  };

  const generatePreview = async () => {
    if (!selectedTemplate || contacts.length === 0) return;

    setIsProcessing(true);
    
    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('template_id', selectedTemplate.id);
      formData.append('csv_file', selectedFile!);

      const response = await fetch(`${API_BASE_URL}/mail-merge`, {
        method: 'POST',
        credentials: 'include', // Include session cookies
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setPreviewData(result.results);
      } else {
        const error = await response.json();
        alert(`Error generating preview: ${error.error}`);
      }
    } catch (error) {
      console.error('Error generating preview:', error);
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
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Important: Include session cookies
        body: JSON.stringify({
          template_id: selectedTemplate.id,
          contacts: contacts
        }),
      });

      if (response.ok) {
        await response.json(); // Consume response without assigning to unused variable
        alert(`Successfully processed ${contacts.length} emails!`);
        navigate('/');
      } else {
        const error = await response.json();
        alert(`Error sending emails: ${error.error}`);
      }
    } catch (error) {
      console.error('Error sending emails:', error);
      alert('Error sending emails. Please check if the backend server is running.');
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

  // Helper function to get contact display info
  const getContactDisplayInfo = (contact: Contact) => {
    return {
      name: contact.Name || contact.name || contact['First Name'] || contact['first_name'] || 'Unknown',
      email: contact.Email || contact.email || 'No email'
    };
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={() => navigate('/')}
            className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-3xl font-bold text-gray-900">InMailer</h1>
        </div>

        {/* Sender Name Information */}
        <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0">
              <svg className="w-5 h-5 text-green-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-medium text-green-800">How Sender Name Works</h3>
              <p className="text-sm text-green-700 mt-1">
                Your emails will show your name from the database as the sender, but they are sent from your authenticated Gmail account. 
                This is a Gmail API limitation - the actual sending account cannot be changed, only the display name.
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Upload & Template Selection */}
          <div className="space-y-6">
            {/* CSV Upload */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">1. Upload Contacts</h2>
              
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="csv-upload"
                />
                <label htmlFor="csv-upload" className="cursor-pointer">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 mb-2">
                    <span className="font-medium text-blue-600">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-sm text-gray-500">CSV files only</p>
                </label>
              </div>

              {selectedFile && (
                <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-green-800 text-sm">
                    ✓ {selectedFile.name} uploaded successfully
                  </p>
                  <p className="text-green-700 text-xs mt-1">
                    {contacts.length} contacts found
                  </p>
                </div>
              )}

              <button
                onClick={downloadSampleCSV}
                className="mt-4 text-sm text-blue-600 hover:text-blue-800 flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download sample CSV format
              </button>
            </div>

                         {/* Template Selection */}
             <div className="bg-white rounded-xl shadow-sm p-6">
               <div className="flex items-center justify-between mb-4">
                 <h2 className="text-xl font-semibold text-gray-900">2. Select Template</h2>
                 <button
                   onClick={() => navigate('/templates')}
                   className="px-3 py-1 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                 >
                   + New Template
                 </button>
               </div>
               
               {isLoadingTemplates ? (
                 <div className="text-center py-8">
                   <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                   <p className="text-gray-500">Loading templates...</p>
                 </div>
               ) : templates.length === 0 ? (
                 <div className="text-center py-8 text-gray-500">
                   <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                   <p>No templates available</p>
                   <p className="text-sm mt-2">Create a template first to get started</p>
                   <button
                     onClick={() => navigate('/templates')}
                     className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                   >
                     Create Template
                   </button>
                 </div>
               ) : (
                 <div className="max-h-64 overflow-y-auto space-y-3 pr-2">
                   {templates.map((template) => (
                     <div
                       key={template.id}
                       className={`p-4 border rounded-lg transition-colors ${
                         selectedTemplate?.id === template.id
                           ? 'border-blue-500 bg-blue-50'
                           : 'border-gray-200 hover:border-gray-300'
                       }`}
                     >
                       <div className="flex items-center justify-between">
                         <div 
                           className="flex-1 cursor-pointer"
                           onClick={() => handleTemplateSelect(template)}
                         >
                           <h3 className="font-medium text-gray-900">{template.name}</h3>
                           <p className="text-sm text-gray-600 mt-1">{template.subject}</p>
                           <p className="text-xs text-gray-500 mt-1">
                             Variables: {template.variables.join(', ')}
                           </p>
                           {template.attachment_name && (
                             <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
                               📎 {template.attachment_name}
                             </p>
                           )}
                         </div>
                         <div className="flex items-center gap-2">
                           <FileText className="w-5 h-5 text-gray-400" />
                           <button
                             onClick={(e) => {
                               e.stopPropagation();
                               editTemplate(template);
                             }}
                             onMouseDown={(e) => e.stopPropagation()}
                             className="p-1 text-blue-500 hover:text-blue-700 hover:bg-blue-50 rounded transition-colors"
                             title="Edit template"
                           >
                             <Edit3 className="w-4 h-4" />
                           </button>
                           <button
                             onClick={(e) => {
                               e.stopPropagation();
                               deleteTemplate(template.id, template.name);
                             }}
                             onMouseDown={(e) => e.stopPropagation()}
                             className="p-1 text-red-500 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
                             title="Delete template"
                           >
                             <Trash2 className="w-4 h-4" />
                           </button>
                         </div>
                       </div>
                     </div>
                   ))}
                 </div>
               )}
             </div>

            {/* Action Buttons */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">3. Preview & Send</h2>
              
              <div className="space-y-3">
                <button
                  onClick={generatePreview}
                  disabled={!selectedTemplate || contacts.length === 0 || isProcessing}
                  className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                >
                  <Eye className="w-5 h-5" />
                  Generate Preview
                </button>

                <button
                  onClick={handleSendEmails}
                  disabled={!selectedTemplate || contacts.length === 0 || isProcessing}
                  className="w-full px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                >
                  {isProcessing ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Processing...
                    </>
                  ) : (
                    <>
                      <Send className="w-5 h-5" />
                      Send {contacts.length} Emails
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Right Column - Preview */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Preview</h2>
              {previewData.length > 0 && (
                <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                  {previewData.length} of {contacts.length} contacts
                </span>
              )}
            </div>
            
            {/* Preview Summary */}
            {previewData.length > 0 && selectedTemplate && (
              <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-blue-900">Template: {selectedTemplate.name}</h3>
                    <p className="text-sm text-blue-700 mt-1">
                      Showing preview for first {previewData.length} contacts
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-blue-600 font-medium">
                      {contacts.length} total contacts
                    </p>
                    <p className="text-xs text-blue-500">
                      Variables will be replaced with actual data
                    </p>
                  </div>
                </div>
              </div>
            )}
            
            {previewData.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>Upload a CSV file and select a template to see preview</p>
              </div>
            ) : (
              <div className="h-[600px] overflow-y-auto space-y-4 pr-2">
                {previewData.map((result, index) => {
                  // Enhanced contact name extraction - handle various CSV column name formats
                  const contactName = result.contact_summary?.name || 
                    result.contact?.First_Name || 
                    result.contact?.first_name || 
                    result.contact?.Name || 
                    result.contact?.name ||
                    result.contact?.['First Name'] ||
                    result.contact?.['first name'] ||
                    result.contact?.['First_Name'] ||
                    result.contact?.['firstName'] ||
                    result.contact?.['FirstName'] ||
                    'Unknown';
                  
                  const contactEmail = result.contact_summary?.email || 
                    result.contact?.Email || 
                    result.contact?.email || 
                    result.contact?.['Email Address'] ||
                    result.contact?.['email address'] ||
                    result.contact?.['EmailAddress'] ||
                    'No email';
                  
                  const contactCompany = result.contact_summary?.company || 
                    result.contact?.Company || 
                    result.contact?.company || 
                    result.contact?.['Company Name'] ||
                    result.contact?.['company name'] ||
                    result.contact?.['CompanyName'] ||
                    result.contact?.['Organization'] ||
                    result.contact?.['organization'] ||
                    'No company';
                  
                  const subject = result.subject || 'No subject';
                  const contentPreview = result.content_preview || result.content?.substring(0, 150) + '...' || 'No content';
                  
                  return (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      {/* Contact Header */}
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h4 className="font-medium text-gray-900">
                            {contactName}
                          </h4>
                          <p className="text-xs text-gray-500">
                            {contactEmail}
                          </p>
                          {contactCompany !== 'No company' && (
                            <p className="text-xs text-blue-600">
                              {contactCompany}
                            </p>
                          )}
                        </div>
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          result.status === 'preview' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'
                        }`}>
                          {result.status}
                        </span>
                      </div>
                      
                      {/* Subject Line */}
                      <div className="mb-3 p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Subject:</p>
                        <p className="text-sm font-medium text-gray-900">{subject}</p>
                      </div>
                      
                      {/* Email Content Preview */}
                      <div className="mb-3 p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Content Preview:</p>
                        <p className="text-sm text-gray-700 whitespace-pre-line leading-relaxed">
                          {contentPreview}
                        </p>
                      </div>
                      
                      {/* Attachment */}
                      {selectedTemplate?.attachment_name && (
                        <div className="mt-3 pt-3 border-t border-gray-100">
                          <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Attachment:</p>
                          <p className="text-sm text-green-600 flex items-center gap-1">
                            📎 {selectedTemplate.attachment_name}
                          </p>
                        </div>
                      )}
                    </div>
                  );
                })}
                
                {previewData.length > 5 && (
                  <div className="text-center py-4 border-t border-gray-100">
                    <p className="text-sm text-gray-500">
                      Scroll to see all {previewData.length} previews
                    </p>
                  </div>
                )}
                
                {contacts.length > previewData.length && (
                  <p className="text-center text-sm text-gray-500 py-2">
                    ... and {contacts.length - previewData.length} more contacts
                  </p>
                )}
              </div>
            )}
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
 
 export default MailMerge;
