import React, { useState } from 'react';
import SettingRow from './SettingRow';
import axios from 'axios';
import { getCSRFToken } from '../background/Torrent';
import { getError } from '../common/utils';
import ErrorPanel from '../common/ErrorPanel';
import InfoPanel from '../common/InfoPanel';
import { isEmpty } from '../../stream/utils';

const DotenvSettings = ({ settings, fetchSettings }) => {
  const [errorMessage, setErrorMessage] = useState('');
  const [infoMessage, setInfoMessage] = useState('');

  const saveDotenvs = (val) => {
    setInfoMessage('');
    if (isEmpty(val)) return;

    axios
      .post(
        '/panel/api/global-settings',
        {
          dotenv: val,
        },
        {
          headers: {
            'X-CSRFToken': getCSRFToken(),
          },
        }
      )
      .then((response) => {
        setInfoMessage(`${Object.keys(val)[0]} setting has been saved.`);
        setTimeout(() => fetchSettings(), 2000);
      })
      .catch((err) => {
        setErrorMessage(getError(err));
      });
  };

  const renderRows = () => {
    if (settings === undefined || isEmpty(settings)) return;

    return (
      <tbody>
        {Object.keys(settings).map((keyName, i) => (
          <SettingRow
            key={i}
            keyName={keyName}
            value={settings[keyName]}
            refFunction={saveDotenvs}
          />
        ))}
      </tbody>
    );
  };

  const renderErrorMessage = () => {
    if (errorMessage === '') return;

    return <ErrorPanel>{errorMessage}</ErrorPanel>;
  };

  const renderInfoMessage = () => {
    if (infoMessage === '') return;

    return <InfoPanel>{infoMessage}</InfoPanel>;
  };

  return (
    <div>
      <h2>Environment Settings</h2>
      <h4 style={{ color: '#FFFF00' }}>
        Changing these settings may cause the system to not work properly. Be
        very cautious.
      </h4>
      <p>
        Some of these settings requires the system to be restarted in order to
        take affect.
      </p>
      {renderErrorMessage()}
      {renderInfoMessage()}
      <table className="table table-dark table-hover">
        <thead>
          <tr>
            <th scope="col">Setting</th>
            <th scope="col">Value</th>
            <th scope="col">Action</th>
          </tr>
        </thead>
        {renderRows()}
      </table>
    </div>
  );
};

export default DotenvSettings;
