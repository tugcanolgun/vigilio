import { render } from 'react-dom';
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import AddMovieForm from './AddMovieForm';
import { getCSRFToken } from '../background/Torrent';
import InfoPanel from '../common/InfoPanel';
import ErrorPanel from '../common/ErrorPanel';
import { getError } from '../common/utils';
import SearchMovieIndex from './SearchMovie';
import { getLocal, setLocal } from '../../stream/utils';

const Index = () => {
  const tabs = ['Search', 'Add manually'];
  const [process, setProcess] = useState(getLocal('addMovieTabPref', tabs[0]));
  const [errorMessage, setErrorMessage] = useState('');
  const [results, setResults] = useState('');

  useEffect(() => {
    setLocal('addMovieTabPref', process);
  }, [process]);

  const addMovieRequest = ({ imdbId, source }) => {
    if (source === '' || imdbId === '') {
      if (source === '') setErrorMessage('Source cannot be empty.');
      else if (imdbId === '')
        setErrorMessage('IMDB ID or IMDB link is required.');
      return;
    }

    setErrorMessage('');
    setResults('');
    axios
      .post(
        '/panel/api/add-movie',
        {
          imdbId,
          source,
        },
        {
          headers: {
            'X-CSRFToken': getCSRFToken(),
          },
        }
      )
      .then((response) => {
        console.log(response.data);
        if (response.data && response.data.operation)
          setResults(response.data.operation);
        else setResults(JSON.stringify(response.data));
      })
      .catch((err) => {
        console.error(err);
        setErrorMessage(getError(err));
      });
  };

  const renderResults = () => {
    if (results === '') return;

    return (
      <InfoPanel>
        <p>{results}</p>
        <p>
          Go to{' '}
          <a href={'/panel/background-management/'}>Background Management</a>
        </p>
      </InfoPanel>
    );
  };

  const renderErrorMessage = () => {
    if (errorMessage === '') return;

    return (
      <ErrorPanel style={{ fontSize: 'x-large' }}>{errorMessage}</ErrorPanel>
    );
  };

  const renderProcess = () => {
    switch (process) {
      case 'Search':
        return <SearchMovieIndex addMovieRequest={addMovieRequest} />;
      case 'Add manually':
        return <AddMovieForm addMovieRequest={addMovieRequest} />;
      default:
        return <AddMovieForm addMovieRequest={addMovieRequest} />;
    }
  };

  const renderHeader = () => {
    return (
      <ul className="nav nav-tabs mb-4">
        {tabs.map((t) => {
          const active = t === process ? 'active' : '';
          return (
            <li key={t} className="nav-item">
              <a
                onClick={() => setProcess(t)}
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

  return (
    <div>
      {renderHeader()}
      {renderResults()}
      {renderErrorMessage()}
      <div style={{ marginBottom: 14, marginLeft: 6 }}></div>
      {renderProcess()}
    </div>
  );
};

render(<Index />, document.getElementById('root'));
