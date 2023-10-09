import React, { useEffect, useState } from 'react';
import { socket } from './socket';

const LogViewer = () => {
  const [logMessages, setLogMessages] = useState([]);

  useEffect(() => {
    socket.on('log_message', (data) => {
      setLogMessages((prevMessages) => {
        let updatedMessages = [...prevMessages];

        if (
          data.level === 'TRAINING' ||
          data.level === 'RENDERING' ||
          data.level === 'COLMAP'
        ) {
          const index = updatedMessages.findIndex((log) => log.level === data.level);

          if (index !== -1) {
            updatedMessages[index] = {
              timestamp: data.timestamp,
              level: data.level,
              message: data.message,
            };
          } else {
            updatedMessages = [
              {
                timestamp: data.timestamp,
                level: data.level,
                message: data.message,
              },
              ...updatedMessages,
            ];
          }
        } else {
          updatedMessages = [
            {
              timestamp: data.timestamp,
              level: data.level,
              message: data.message,
            },
            ...updatedMessages,
          ];
        }

        return updatedMessages;
      });
    });

    if (logMessages.length === 0) {
      fetchInitialLogMessages();
    }

    // Start a timer to fetch logs periodically
    const timer = setInterval(fetchLogMessages, 5000); // Fetch logs every 5 seconds

    return () => {
      socket.off('log_message');
      clearInterval(timer); // Clean up the timer when the component unmounts
    };
  }, []);

  const fetchInitialLogMessages = async () => {
    const initialLogMessages = [
      {
        timestamp: '-----------------------',
        level: 'INFO',
        message: 'Logs from the video to nerf trainer',
      },
      // Add more initial log messages if needed
    ];

    initialLogMessages.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    setLogMessages(initialLogMessages);
  };

  const fetchLogMessages = async () => {
    try {
      // Fetch latest log messages here and update the state
    } catch (error) {
      console.error('Error fetching latest logs:', error);
    }
  };

  return (
    <div className="card mt-3">
      <div className="card-body">
        {logMessages.map((log, index) => (
          <div key={index}>
            <span style={{ color: 'blue' }}>{log.timestamp}</span> |{' '}
            {log.level === 'INFO' && <span style={{ color: 'blue' }}>{log.level}</span>}
            {log.level === 'TRAINING' && <span style={{ color: 'green' }}>{log.level}</span>}
            {log.level === 'RENDERING' && <span style={{ color: 'orange' }}>{log.level}</span>}
            {log.level === 'COLMAP' && <span style={{ color: 'purple' }}>{log.level}</span>}
            - <span style={{ color: 'black' }}>{log.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LogViewer;
