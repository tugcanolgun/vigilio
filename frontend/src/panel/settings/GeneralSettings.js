import React, { useEffect, useState } from 'react';
import DotenvSettings from './DotenvSettings';
import SetMovieDb from './SetMovieDb';
import SubtitleLanguages from './SubtitleLanguages';
import RedownloadSubtitles from './RedownloadSubtitles';
import { getLocal, setLocal } from '../../stream/utils';
import MudSources from './MudSources/MudSources';

const GeneralSettings = ({ fetchSettings, settings }) => {
  const tabs = [
    'Environment Settings',
    'Search Sources',
    'Subtitle Languages',
    'Redownload Subtitles',
  ];
  const [tab, setTab] = useState(getLocal('settingsTabPref', tabs[0]));
  settings.dotenv &&
    settings.dotenv.MOVIEDB_API !== undefined &&
    tabs.push('MovieDB Key');

  useEffect(() => {
    setLocal('settingsTabPref', tab);
  }, [tab]);

  const renderHeader = () => {
    return (
      <ul className="nav nav-tabs mb-4">
        {tabs.map((t) => {
          const active = t === tab ? 'active' : '';
          return (
            <li key={t} className="nav-item">
              <a
                onClick={() => setTab(t)}
                className={'nav-link ' + active}
                aria-current="page"
                href="#">
                {t}
              </a>
            </li>
          );
        })}
      </ul>
    );
  };

  const renderPage = () => {
    switch (tab) {
      case 'Environment Settings':
        return (
          <DotenvSettings
            fetchSettings={fetchSettings}
            settings={settings.dotenv}
          />
        );
      case 'MovieDB Key':
        return (
          <SetMovieDb
            fetchSettings={fetchSettings}
            movieDbKey={settings.dotenv && settings.dotenv.MOVIEDB_API}
            message={'The API Key has been stored.'}
          />
        );
      case 'Subtitle Languages':
        return (
          <SubtitleLanguages
            fetchSettings={fetchSettings}
            subtitles={settings.dotenv && settings.dotenv.SUBTITLE_LANGS}
          />
        );
      case 'Search Sources':
        return <MudSources />;
      case 'Redownload Subtitles':
        return <RedownloadSubtitles />;
      default:
        return (
          <DotenvSettings
            fetchSettings={fetchSettings}
            settings={settings.dotenv}
          />
        );
    }
  };

  return (
    <div>
      {renderHeader()}
      {renderPage()}
    </div>
  );
};

export default GeneralSettings;
