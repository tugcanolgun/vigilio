import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ErrorPanel from '../common/ErrorPanel';
import InfoPanel from '../common/InfoPanel';
import { getError } from '../common/utils';
import { getCSRFToken } from '../background/Torrent';

const SetMovieDb = ({
  fetchSettings,
  movieDbKey = '',
  message = 'The API Key has been stored.',
}) => {
  const [apiKey, setApiKey] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [infoMessage, setInfoMessage] = useState('');

  useEffect(() => {
    setApiKey(movieDbKey);
  }, [movieDbKey]);

  const saveGlobalSettings = () => {
    setInfoMessage('');
    axios
      .post(
        '/panel/api/global-settings',
        {
          dotenv: { MOVIEDB_API: apiKey },
        },
        {
          headers: {
            'X-CSRFToken': getCSRFToken(),
          },
        }
      )
      .then((response) => {
        setInfoMessage(message);
        setTimeout(() => fetchSettings(), 2000);
      })
      .catch((err) => {
        setErrorMessage(getError(err));
      });
  };

  const checkMovieDb = () => {
    if (apiKey === '') {
      setErrorMessage('A valid API key is required.');
      return;
    }

    setErrorMessage('');
    setInfoMessage('');

    axios
      .get(`https://api.themoviedb.org/3/movie/76341?api_key=${apiKey}`)
      .then(() => {
        setInfoMessage('Key is successful. Saving the key...');
        saveGlobalSettings();
      })
      .catch((err) => {
        setErrorMessage(getError(err) + '\n\nKey is invalid. Try again.');
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
      <h2>MovieDB API key</h2>
      <span>
        You can read the instructions how to acquire a key from&nbsp;
        <a
          title={'Link to moviedb API page'}
          href={
            'https://developers.themoviedb.org/3/getting-started/introduction'
          }
          target={'_blank'}>
          here
        </a>
        .
      </span>
      {renderErrorMessage()}
      {renderInfoMessage()}
      <form onSubmit={(e) => e.preventDefault()}>
        <div className={'row my-3'}>
          <div className={'col'}>
            <input
              onChange={(val) => setApiKey(val.target.value)}
              value={apiKey}
              placeholder="MovieDB Api key"
              type="text"
              className="form-control default-input"
              aria-label="Moviedb api key"
              aria-describedby="Moviedb api key"
              autoFocus={true}
            />
          </div>
          <div className={'col-1'}>
            <button
              onClick={() => checkMovieDb()}
              className={'btn btn-lg btn-light'}>
              Try
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default SetMovieDb;
