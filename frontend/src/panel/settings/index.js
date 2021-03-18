import { render } from 'react-dom';
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { getError } from '../common/utils';
import ChangePassword from './ChangePassword';
import ErrorPanel from '../common/ErrorPanel';
import SetMovieDb from './SetMovieDb';
import SubtitleLanguages from './SubtitleLanguages';
import GeneralSettings from './GeneralSettings';
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

  const renderPage = () => {
    if (!fetched && isEmpty(settings)) return <h3>Loading...</h3>;

    if (fetched && isEmpty(settings))
      return <h3>There is a problem. No settings are fetched.</h3>;

    if (settings.forcePasswordChange) return <ChangePassword />;

    if (settings.dotenv && settings.dotenv.MOVIEDB_API === '')
      return (
        <SetMovieDb
          fetchSettings={fetchSettings}
          message={'The API Key has been stored. Moving to the next step.'}
        />
      );

    if (settings.dotenv && settings.dotenv.SUBTITLE_LANGS === '')
      return <SubtitleLanguages fetchSettings={fetchSettings} />;

    return (
      <GeneralSettings fetchSettings={fetchSettings} settings={settings} />
    );
  };

  const renderErrorMessage = () => {
    if (errorMessage === '') return;

    return <ErrorPanel>{errorMessage}</ErrorPanel>;
  };

  return (
    <div className={'mb-5'}>
      {renderErrorMessage()}
      {renderPage()}
    </div>
  );
};

render(<Index />, document.getElementById('root'));
