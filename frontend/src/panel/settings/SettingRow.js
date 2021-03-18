import React, { useEffect, useState } from 'react';

const SettingRow = ({ keyName, value, refFunction = null }) => {
  const [showInput, setShowInput] = useState(false);
  const [input, setInput] = useState('');

  useEffect(() => {
    setInput(value);
  }, [value]);

  const saveSetting = () => {
    setShowInput(false);
    if (refFunction !== null) refFunction({ [keyName]: input });
  };

  const renderValue = () => {
    if (showInput)
      return (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            saveSetting();
          }}>
          <input
            onChange={(val) => setInput(val.target.value)}
            value={input}
            placeholder="Change the setting"
            type="text"
            className="form-control default-input"
            style={{
              fontSize: 'medium',
              paddingLeft: 10,
              backgroundColor: '#AAAAAA',
              color: '#000000',
            }}
            aria-label="Change the setting"
            aria-describedby="Change the setting"
            autoFocus={true}
          />
        </form>
      );

    return <span>{value}</span>;
  };

  const renderAction = () => {
    if (showInput)
      return (
        <button
          onClick={() => saveSetting()}
          className={'btn btn-sm btn-light'}>
          Save
        </button>
      );

    return (
      <button
        onClick={() => setShowInput(true)}
        className={'btn btn-sm btn-outline-light'}>
        Change
      </button>
    );
  };

  return (
    <tr>
      <td>{keyName}</td>
      <td>{renderValue()}</td>
      <td>{renderAction()}</td>
    </tr>
  );
};

export default SettingRow;
