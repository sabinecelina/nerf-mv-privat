import React, { useEffect, useState } from 'react';
import { socket } from './socket';

const LogViewer = (props) => {
  const [logMessages, setLogMessages] = useState([]);

  useEffect(() => {
    socket.on('log_message', (data) => {
      setLogMessages((prevMessages) => {
        let updatedMessages = [...prevMessages];

        if (
          data.level === 'TRAINING' ||
          data.level === 'RENDERING' ||
          data.level === 'COLMAP' // Add 'COLMAP' to the condition
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

    return () => {
      socket.off('log_message');
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
