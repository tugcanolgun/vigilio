import { render } from 'react-dom';
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { getError } from '../common/utils';
import ChangePassword from '../settings/ChangePassword';
import SetMovieDb from '../settings/SetMovieDb';
import SubtitleLanguages from '../settings/SubtitleLanguages';
import ErrorPanel from '../common/ErrorPanel';
import { isEmpty } from '../../stream/utils';

const Index = () => {
  const [settings, setSettings] = useState({});
  const [fetched, setFetched] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = () => {
    axios
      .get('/panel/api/global-settings')
      .then((response) => {
        setSettings(response.data);
        setFetched(true);
      })
      .catch((err) => {
        console.log(err);
        setErrorMessage(getError(err));
        setFetched(true);
      });
  };

  const renderSuccess = () => {
    setTimeout(() => {
      const urlParams = new URLSearchParams(window.location.search);
      let next = urlParams.get('next');
      if (next === null) next = '/';

      window.location.href = next;
    }, 2000);

    return (
      <div>
        <h1>Setup complete!</h1>
        <p>You are being redirected...</p>
      </div>
    );
  };

  const renderPage = () => {
    if (!fetched && isEmpty(settings)) return <h3>Loading...</h3>;

    if (fetched && isEmpty(settings))
      return <h3>There is a problem. No settings are fetched.</h3>;

    if (settings.forcePasswordChange) return <ChangePassword />;

    if (settings.dotenv && settings.dotenv.MOVIEDB_API === '')
      return <SetMovieDb fetchSettings={fetchSettings} />;

    if (settings.dotenv && settings.dotenv.SUBTITLE_LANGS === '')
      return <SubtitleLanguages fetchSettings={fetchSettings} />;

    return renderSuccess();
  };

  const renderErrorMessage = () => {
    if (errorMessage === '') return;

    return <ErrorPanel>{errorMessage}</ErrorPanel>;
  };

  return (
    <div className={'my-5'}>
      <h1>Initial Setup</h1>
      <hr />
      {renderErrorMessage()}
      {renderPage()}
    </div>
  );
};

render(<Index />, document.getElementById('root'));
