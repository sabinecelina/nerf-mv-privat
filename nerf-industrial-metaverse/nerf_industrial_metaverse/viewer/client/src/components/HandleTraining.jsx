import React, { useState } from 'react';
import ConfigChanger from './ConfigChanger';

const HandleTraining = () => {
    const [showConfigChanger, setShowConfigChanger] = useState(false);
    const [startButtonDisabled, setStartButtonDisabled] = useState(false);
    const [configButtonDisabled, setConfigButtonDisabled] = useState(false);

    const handleStartTraining = () => {
        setStartButtonDisabled(true); 
        
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
            })
            .finally(() => {
                setTimeout(() => {
                    setStartButtonDisabled(false);
                }, 5000);
            });
    };

    const handleChangeConfigs = () => {
        setConfigButtonDisabled(true); 
        
        setShowConfigChanger((prevShowConfigChanger) => !prevShowConfigChanger);

        setTimeout(() => {
            setConfigButtonDisabled(false);
        }, 5000);
    };

    const handleSaveConfigs = () => {
        setShowConfigChanger(false);
    };

    return (
        <div>{showConfigChanger && <ConfigChanger onSave={handleSaveConfigs} />}
            <div className="mt-3">
                <button className="btn btn-primary m-2" onClick={handleStartTraining} disabled={startButtonDisabled}>
                    Start Training
                </button>
                <button className="btn btn-secondary" onClick={handleChangeConfigs} disabled={configButtonDisabled}>
                    Change Configs
                </button>
            </div>
        </div>
    );
};

export default HandleTraining;
