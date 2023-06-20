import React, { useState } from 'react';
import LogViewer from './LogViewer';
import ConfigChanger from './ConfigChanger';

const UploadForm = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState('');
  const [showButtons, setShowButtons] = useState(false);
  const [trainingMessage, setTrainingMessage] = useState('');
  const [showConfigChanger, setShowConfigChanger] = useState(false); // Added state variable

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

  const handleStartTraining = () => {
    setTrainingMessage(true);
    fetch('/start-training', {
      method: 'POST',
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Failed to start training.');
        }
      })
      .then((data) => {
        const { status, message } = data;
        if (status === 'success') {
          console.log(message);
        } else {
          console.error(message);
        }
      })
      .catch((error) => {
        console.error(error);
      });
  };

  const handleChangeConfigs = () => {
    setShowConfigChanger((prevShowConfigChanger) => !prevShowConfigChanger);
  };

  const handleSaveConfigs = () => {
    // Logic for saving the configs goes here...
    setShowConfigChanger(false);
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
      {showConfigChanger && <ConfigChanger onSave={handleSaveConfigs} />}
      {showButtons && (
        <div className="mt-3">
          <button className="btn btn-primary me-2" onClick={handleStartTraining}>
            Start Training
          </button>
          <button className="btn btn-secondary" onClick={handleChangeConfigs}>
            Change Configs
          </button>
        </div>
      )}
      {trainingMessage && (
        <LogViewer />
      )}
    </div>
  );
};

export default UploadForm;
