import React, { useState } from 'react';
import { Upload, Loader2, AlertCircle, CheckCircle2, X } from 'lucide-react';

const DocumentUploadApp = () => {
  const [formData, setFormData] = useState({
    provider: '',
    documentName: '',
    category: 'Board Certifications',
    expirationDate: '',
    alertReminder: '60 Days Before Expiration',
    notes: ''
  });
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  // All document categories
  const categories = [
    'Board Certifications',
    'Curriculum Vitae',
    'DEA License',
    'Drivers License',
    'Fellowship',
    'Government ID',
    'Hospital Affiliations',
    'Internship',
    'Liability Insurance',
    'Medical Education and Training',
    'Medical School',
    'Other Certificate',
    'Passport',
    'Peer Reference',
    'Residency',
    'Specialty Info',
    'State Applications',
    'State Licenses',
    'Work History'
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === 'expirationDate') {
      const formattedDate = formatDateInput(value);
      setFormData(prev => ({
        ...prev,
        [name]: formattedDate
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const formatDateInput = (value) => {
    let cleaned = value.replace(/[^\d-]/g, '');
    
    if (cleaned.length >= 2 && cleaned.charAt(2) !== '-') {
      cleaned = cleaned.slice(0, 2) + '-' + cleaned.slice(2);
    }
    if (cleaned.length >= 5 && cleaned.charAt(5) !== '-') {
      cleaned = cleaned.slice(0, 5) + '-' + cleaned.slice(5);
    }
    
    cleaned = cleaned.slice(0, 10);
    return cleaned;
  };

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      console.log("File selected:", selectedFile.name);
      setFile(selectedFile);
      handleUpload(selectedFile);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
      handleUpload(droppedFile);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleDragEnter = (event) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const getDocumentCategory = (documentType, stateCode) => {
    const categoryMap = {
      'State Medical License': 'State Licenses',
      'DEA License': 'DEA License',
      'Board Certification': 'Board Certifications',
      'Medical Education': 'Medical Education and Training',
      'Hospital Affiliation': 'Hospital Affiliations',
      'Other Certificate': 'Other Certificate'
    };

    const baseCategory = categoryMap[documentType] || 'Other Certificate';
    console.log(`Mapping document type: ${documentType} to category: ${baseCategory}`);
    return baseCategory;
  };

  const handleUpload = async (selectedFile) => {
    const fileToUpload = selectedFile || file;
    if (!fileToUpload) {
      return;
    }

    setLoading(true);
    setError(null);
    setUploadSuccess(false);

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('file', fileToUpload);

      const response = await fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formDataToSend
      });

      const data = await response.json();
      console.log("Server response:", data);

      if (!response.ok || data.error) {
        throw new Error(data.error || "Failed to process document");
      }

      setFormData(prevData => ({
        ...prevData,
        provider: data.provider || prevData.provider,
        documentName: data.documentName || prevData.documentName,
        category: getDocumentCategory(data.documentType, data.stateCode),
        expirationDate: data.expirationDate || prevData.expirationDate
      }));
      setUploadSuccess(true);
    } catch (error) {
      console.error("Upload error:", error);
      setError(error.message || "Error uploading file. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const clearFile = () => {
    setFile(null);
    setError(null);
    setUploadSuccess(false);
  };

  const handleSave = () => {
    if (!formData.provider.trim() || !formData.documentName.trim()) {
      setError('Provider and Document Name are required fields');
      return;
    }
    console.log('Saving form data:', formData);
    // Add your save logic here
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-6xl mx-auto bg-white rounded-lg shadow-sm">
        <div className="flex flex-col lg:flex-row p-6">
          {/* Left Form Section */}
          <div className="flex-1 lg:pr-8">
            <h2 className="text-xl font-semibold mb-6">Add Document</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block mb-1 text-sm font-medium">
                  <span className="text-red-500">*</span> Provider
                </label>
                <input
                  type="text"
                  name="provider"
                  className="w-full p-2.5 border rounded-lg focus:ring-2 focus:ring-purple-300 focus:border-purple-500 outline-none"
                  value={formData.provider}
                  onChange={handleChange}
                  required
                />
              </div>

              <div>
                <label className="block mb-1 text-sm font-medium">
                  <span className="text-red-500">*</span> Document Name
                </label>
                <input
                  type="text"
                  name="documentName"
                  className="w-full p-2.5 border rounded-lg focus:ring-2 focus:ring-purple-300 focus:border-purple-500 outline-none"
                  value={formData.documentName}
                  onChange={handleChange}
                  required
                />
              </div>

              <div>
                <label className="block mb-1 text-sm font-medium">Category</label>
                <select
                  name="category"
                  className="w-full p-2.5 border rounded-lg bg-white focus:ring-2 focus:ring-purple-300 focus:border-purple-500 outline-none"
                  value={formData.category}
                  onChange={handleChange}
                >
                  {categories.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block mb-1 text-sm font-medium">Expiration date</label>
                <input
                  type="text"
                  name="expirationDate"
                  className="w-full p-2.5 border rounded-lg focus:ring-2 focus:ring-purple-300 focus:border-purple-500 outline-none"
                  value={formData.expirationDate}
                  onChange={handleChange}
                  placeholder="MM-DD-YYYY"
                />
              </div>

              <div>
                <label className="block mb-1 text-sm font-medium">Expiration Alert Reminder</label>
                <select
                  name="alertReminder"
                  className="w-full p-2.5 border rounded-lg bg-white focus:ring-2 focus:ring-purple-300 focus:border-purple-500 outline-none"
                  value={formData.alertReminder}
                  onChange={handleChange}
                >
                  <option value="60 Days Before Expiration">60 Days Before Expiration</option>
                  <option value="30 Days Before Expiration">30 Days Before Expiration</option>
                  <option value="15 Days Before Expiration">15 Days Before Expiration</option>
                </select>
              </div>

              <div>
                <label className="block mb-1 text-sm font-medium">Notes</label>
                <textarea
                  name="notes"
                  className="w-full p-2.5 border rounded-lg h-24 resize-none focus:ring-2 focus:ring-purple-300 focus:border-purple-500 outline-none"
                  value={formData.notes}
                  onChange={handleChange}
                  placeholder="Add any additional notes..."
                />
              </div>
            </div>
          </div>

          {/* Right Upload Section */}
          <div className="flex-1 lg:pl-8 mt-6 lg:mt-0">
            <h2 className="text-xl font-semibold mb-6">Supporting Documents</h2>
            
            <div 
              className={`border-2 border-dashed rounded-lg p-8 transition-colors relative
                ${loading ? 'opacity-75' : ''}
                ${error ? 'border-red-300 bg-red-50' : 'border-purple-200 hover:border-purple-300 bg-purple-50'}`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragEnter={handleDragEnter}
            >
              <div className="flex flex-col items-center justify-center text-center">
                {loading ? (
                  <Loader2 className="w-12 h-12 text-purple-500 animate-spin mb-4" />
                ) : (
                  <Upload className="w-12 h-12 text-purple-400 mb-4" />
                )}
                
                <p className="mb-2 text-gray-700">
                  Drag and Drop your file here
                </p>
                <p className="text-gray-500 text-sm mb-4">OR</p>
                <label className="bg-purple-600 text-white px-4 py-2 rounded-lg cursor-pointer hover:bg-purple-700 transition-colors">
                  Select a File
                  <input
                    type="file"
                    onChange={handleFileChange}
                    className="hidden"
                    accept=".jpg,.jpeg,.png,.pdf,.docx"
                    disabled={loading}
                  />
                </label>
                
                {file && (
                  <div className="mt-4 p-3 bg-white rounded-lg border flex items-center gap-2">
                    <span className="text-sm text-gray-600 truncate max-w-xs">
                      {file.name}
                    </span>
                    <button
                      onClick={clearFile}
                      className="text-gray-400 hover:text-gray-600"
                      disabled={loading}
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                )}
                
                <p className="mt-4 text-xs text-gray-500">
                  Supported formats: JPG, PNG, PDF, DOCX (Max 10MB)
                </p>
              </div>
            </div>

            {error && (
              <div className="mt-4 p-3 bg-red-50 rounded-lg flex items-start gap-2">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <span className="text-sm text-red-700">{error}</span>
              </div>
            )}

            {uploadSuccess && (
              <div className="mt-4 p-3 bg-green-50 rounded-lg flex items-start gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                <span className="text-sm text-green-700">File uploaded successfully</span>
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-end gap-3 p-6 bg-gray-50 rounded-b-lg border-t">
          <button 
            type="button" 
            className="px-4 py-2 text-purple-600 hover:text-purple-700 transition-colors disabled:opacity-50"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="button"
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
            onClick={handleSave}
            disabled={loading}
          >
            {loading ? 'Processing...' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentUploadApp;