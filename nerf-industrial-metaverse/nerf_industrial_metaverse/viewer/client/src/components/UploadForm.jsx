import React, { useState } from 'react';
import LogViewer from './LogViewer';
import HandleTraining from './HandleTraining';

const UploadForm = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState('');
  const [showButtons, setShowButtons] = useState(false);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = () => {
    if (!selectedFile) {
      setUploadStatus('No file selected.');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    setUploadProgress(0);
    setUploadStatus('Uploading...');

    fetch('/upload', {
      method: 'POST',
      body: formData,
      onUploadProgress: (progressEvent) => {
        const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100);
        setUploadProgress(progress);
      },
    })
      .then((response) => {
        if (response.ok) {
          setUploadStatus('File uploaded successfully!');
          setShowButtons(true);
        } else {
          setUploadStatus('Upload failed.');
        }
      })
      .catch((error) => {
        setUploadStatus('Upload failed.');
        console.error(error);
      });
  };

  return (
    <div>
      <input type="file" className="form-control mb-3" onChange={handleFileChange} />
      <button className="btn btn-primary" onClick={handleUpload}>
        Upload
      </button>
      {uploadProgress > 0 && (
        <div className="progress mt-3">
          <div
            className="progress-bar"
            role="progressbar"
            style={{ width: `${uploadProgress}%` }}
            aria-valuenow={uploadProgress}
            aria-valuemin="0"
            aria-valuemax="100"
          >
            {uploadProgress}%
          </div>
        </div>
      )}
      {uploadStatus && (
        <div className={`mt-3 alert ${uploadStatus === 'File uploaded successfully!' ? 'alert-success' : 'alert-danger'}`} role="alert">
          {uploadStatus}
        </div>
      )}
      {showButtons && (
        <HandleTraining />
      )}
      <LogViewer />
    </div>
  );
};

export default UploadForm;
