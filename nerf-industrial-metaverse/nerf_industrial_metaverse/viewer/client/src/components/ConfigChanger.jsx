import React, { useState } from 'react';
import ConfigInputField from './ConfigInputField'
const ConfigChanger = () => {
  const [newConfig, setNewConfig] = useState({});
  const [configStatus, setConfigStatus] = useState(false);

  const handleChangeConfig = () => {
    // Call the backend API to update the YAML configuration
    fetch('/update_yaml_config', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json;charset=UTF-8' // Updated Content-Type header
      },
      body: JSON.stringify(newConfig)
    })
      .then(response => response.json())
      .then(data => {
        setConfigStatus(true);
        console.log('Config saved successfully');
      })
      .catch(error => {
        setConfigStatus(false);
        console.error('Error saving config:', error);
      });
  };
  if (configStatus) {
    return (
      <div className="mt-3">
        <div className="alert alert-success" role="alert">
          Configs changed successfully!
        </div>
      </div>
    );
  }

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setNewConfig(prevConfig => ({ ...prevConfig, [name]: value }));
  };

  return (
    <div>
      <div>
        <h4 className="my-3">Configurations</h4>
        <ConfigInputField
          label="Video Downsample:"
          id="videoDownsample"
          name="video_downsample"
          value={newConfig.video_downsample || ''}
          onChange={handleInputChange}
          additionalText="Extracts every 2nd frame by default. Increase to extract every nth frame."
        />
        <ConfigInputField
          label="Max Images of Video:"
          id="max_count"
          name="max_count"
          value={newConfig.max_count || ''}
          onChange={handleInputChange}
          additionalText="Up to 380 frames can fit into GPU memory for training."
        />
        <ConfigInputField
          label="N Steps:"
          id="nSteps"
          name="n_steps"
          value={newConfig.n_steps || ''}
          onChange={handleInputChange}
          additionalText="Number of training steps."
        />
        <ConfigInputField
          label="Subsample:"
          id="subsample"
          name="subsample"
          value={newConfig.subsample || ''}
          onChange={handleInputChange}
          additionalText="After running COLMAP, the number of images for training can be reduced."
        />
        <ConfigInputField
          label="aabb_scale:"
          id="aabb_scale"
          name="aabb_scale"
          value={newConfig.aabb_scale || ''}
          onChange={handleInputChange}
          additionalText="Scale factor for larger scenes. 1=Scene fits within a unit cube. [1,2,4,8,16,32,...,128]"
        />
      </div>

      <button className="btn btn-primary" onClick={handleChangeConfig}>
        Save Config
      </button>
      {configStatus && <p>{configStatus}</p>}
    </div>
  );
};

export default ConfigChanger;
