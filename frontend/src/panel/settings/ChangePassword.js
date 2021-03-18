import React, { useState } from 'react';
import axios from 'axios';
import { getCSRFToken } from '../background/Torrent';
import { getError } from '../common/utils';
import ErrorPanel from '../common/ErrorPanel';
import InfoPanel from '../common/InfoPanel';

const ChangePassword = () => {
  const [password1, setPassword1] = useState('');
  const [password2, setPassword2] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [infoMessage, setInfoMessage] = useState('');

  const isPasswordWrong = () => {
    if (password1 !== password2) {
      setErrorMessage('Passwords do not match.');
      return true;
    }

    if (password1.length < 8) {
      setErrorMessage('Password needs to be at least 8 characters.');
      return true;
    }
  };

  const changePasswordRequest = () => {
    setErrorMessage('');
    if (isPasswordWrong()) return;

    axios
      .post(
        '/panel/api/user/change-password',
        {
          currentPassword: 'adminadmin',
          newPassword: password1,
        },
        {
          headers: {
            'X-CSRFToken': getCSRFToken(),
          },
        }
      )
      .then((response) => {
        if (response.data && response.data.operation)
          setInfoMessage(response.data.operation);
        else setInfoMessage(JSON.stringify(response.data));
        setTimeout(() => {
          console.log('fetching the settings again');
          window.location.href = '/';
        }, 2000);
      })
      .catch((err) => {
        setErrorMessage(getError(err));
      });
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
      <h3>Change admin password.</h3>
      <h4 className={'mb-5'}>
        <span style={{ color: '#FFFF00' }}>
          In order to use the system, please change the default admin password.
        </span>
      </h4>
      <div>
        <span>The password has to be at least 8 characters.</span>
        {renderErrorMessage()}
        {renderInfoMessage()}
        <form onSubmit={(e) => e.preventDefault()}>
          <input
            onChange={(val) => setPassword1(val.target.value)}
            value={password1}
            placeholder="Password"
            type="password"
            className="form-control default-input my-1"
            aria-label="Enter password"
            aria-describedby="enter password"
            autoFocus={true}
          />
          <input
            onChange={(val) => setPassword2(val.target.value)}
            value={password2}
            placeholder="Repeat password"
            type="password"
            className="form-control default-input my-2"
            aria-label="Repeat password"
            aria-describedby="repeat password"
          />
          <button
            onClick={() => changePasswordRequest()}
            className={'btn btn-lg btn-light mt-3'}>
            Change
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChangePassword;
