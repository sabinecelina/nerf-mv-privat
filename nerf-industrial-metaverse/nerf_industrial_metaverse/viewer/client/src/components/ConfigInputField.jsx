import React from 'react';

const ConfigInputField = ({
  label,
  id,
  name,
  value,
  onChange,
  additionalText,
}) => {
  return (
    <div className="form-group row my-2">
      <label htmlFor={id} className="col-sm-2 col-form-label">
        {label}
      </label>
      <div className="col-sm-2">
        <input
          type="number"
          className="form-control"
          id={id}
          name={name}
          value={value || ''}
          onChange={onChange}
        />
      </div>
      <div className="col-sm-8 col-form-label">
        <p>{additionalText}</p>
      </div>
    </div>
  );
};

export default ConfigInputField;
