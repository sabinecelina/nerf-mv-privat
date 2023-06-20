import React from 'react';


const CheckConnection = (props) => {


  return (
    <div className="text-center">
      <p className={`connection-status ${props.isConnected ? 'connected' : 'not-connected'}`}>
        Checking connection to server: {props.isConnected ? 'connected' : 'not connected'}
      </p>
    </div>
  );
};

export default CheckConnection;
