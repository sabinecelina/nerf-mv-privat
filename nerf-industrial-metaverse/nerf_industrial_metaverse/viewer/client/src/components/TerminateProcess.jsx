import React from 'react';

const TerminateProcess = () => {
  const handleTerminateClick = async () => {
    try {
      const response = await fetch('/terminate_colmap_processes', {
        method: 'POST',
      });
      if (response.ok) {
        console.log('Colmap-Prozesse wurden beendet.');
      } else {
        console.log('Fehler beim Beenden der Colmap-Prozesse.');
      }
    } catch (error) {
        console.log('Fehler beim Beenden der Colmap-Prozesse.');
    }
  };

  return (
    <button
      onClick={handleTerminateClick}
      className="btn btn-danger"
      style={{ margin: '10px' }}
    >
      Terminate Process
    </button>
  );
};

export default TerminateProcess;