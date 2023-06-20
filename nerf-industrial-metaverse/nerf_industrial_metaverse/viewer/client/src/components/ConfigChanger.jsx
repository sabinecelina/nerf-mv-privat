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
        <h4 classname="my-3">Training Configurations</h4>
        <ConfigInputField
          label="N Steps:"
          id="nSteps"
          name="n_steps"
          value={newConfig.n_steps || ''}
          onChange={handleInputChange}
          additionalText="Number of steps, default 20000"
        />
        <h4 classname="my-3">Json Configurations</h4>
        <ConfigInputField
          label="Subsample:"
          id="subsample"
          name="subsample"
          value={newConfig.subsample || ''}
          onChange={handleInputChange}
          additionalText="Subsample Images. e.g. 10 - Use every 10th image for training (prevent: out of allocated memory)"
        />
        <ConfigInputField
          label="aabb_scale:"
          id="aabb_scale"
          name="aabb_scale"
          value={newConfig.aabb_scale || ''}
          onChange={handleInputChange}
          additionalText="Large scene scale factor. 1=scene fits in unit cube; power of 2 up to 128, choices=[1, 2, 4, 8, 16, 32..., 128]"
        />
        <h4 classname="my-3">Only for Video Input</h4>
        <ConfigInputField
          label="Video Downsample:"
          id="videoDownsample"
          name="video_downsample"
          value={newConfig.video_downsample || ''}
          onChange={handleInputChange}
          additionalText="FPS downsample ratio, default 1 (no image will skipped)"
        />
        <ConfigInputField
          label="Image Downsample:"
          id="imageDownsample"
          name="image_downsample"
          value={newConfig.image_downsample || ''}
          onChange={handleInputChange}
          additionalText="Image rescale downsample ratio, default 1 (no resize)"
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
