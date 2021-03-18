import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { getError } from '../../common/utils';
import { getLocal, setLocal } from '../../../stream/utils';
import ErrorPanel from '../../common/ErrorPanel';
import SearchMovie from './SearchMovie';

const SearchMovieIndex = ({ addMovieRequest }) => {
  const [fetched, setFetched] = useState(false);
  const [mudSources, setMudSources] = useState([]);
  const [selectedMudSource, setSelectedMudSource] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    if (!fetched) fetchSources();

    if (mudSources.length !== 0) selectSource();
  }, [mudSources]);

  const fetchSources = () => {
    axios
      .get('/panel/api/mud-sources')
      .then((response) => {
        setFetched(true);
        setMudSources(response.data);
      })
      .catch((err) => {
        console.log(err);
        setFetched(true);
        setErrorMessage(getError(err));
      });
  };

  const processSource = (val) => {
    let temp = JSON.parse(JSON.stringify(val));
    temp.source = JSON.parse(val.source.replace(/\'/g, '"'));
    return temp;
  };

  const selectSource = (id = null) => {
    let sId = id !== null ? id : getLocal('selectedSource', null);
    if (sId !== null) {
      let sel = mudSources.find((i) => i.id === sId);
      if (sel !== undefined) {
        setSelectedMudSource(processSource(sel));
        setLocal('selectedSource', sId);
        return;
      }
    }

    setLocal('selectedSource', mudSources[0].id);
    setSelectedMudSource(processSource(mudSources[0]));
  };

  const renderChoices = () => {
    if (!fetched) return;

    if (mudSources.length === 0)
      return (
        <div>
          <h3>There are no sources</h3>
          Please add sources in the&nbsp;
          <a
            onClick={() => {
              setLocal('settingsTabPref', 'Search Sources');
              window.location.href = '/panel/settings/';
            }}
            style={{ textDecoration: 'underline' }}>
            settings
          </a>
          .
        </div>
      );

    return (
      <div className="dropdown mb-3">
        <button
          className="btn btn-sm btn-light dropdown-toggle"
          type="button"
          id="dropdownMenuButton2"
          data-bs-toggle="dropdown"
          aria-expanded="false">
          {selectedMudSource === null
            ? 'Choose a source'
            : selectedMudSource.name}
        </button>
        <ul
          className="dropdown-menu dropdown-menu-dark"
          aria-labelledby="dropdownMenuButton2">
          {mudSources.map((source) => {
            return (
              <li key={source.id}>
                <a
                  className={
                    'dropdown-item ' +
                    (selectedMudSource !== null &&
                    source.id === selectedMudSource.id
                      ? 'active'
                      : '')
                  }
                  onClick={() => selectSource(source.id)}
                  href="#">
                  {source.name}
                </a>
              </li>
            );
          })}
        </ul>
      </div>
    );
  };

  const renderErrorMessage = () => {
    if (errorMessage === '') return;

    return <ErrorPanel>{errorMessage}</ErrorPanel>;
  };

  return (
    <div>
      {renderErrorMessage()}
      {renderChoices()}
      {selectedMudSource !== null ? (
        <SearchMovie
          mudSource={selectedMudSource.source}
          addMovieRequest={addMovieRequest}
        />
      ) : null}
    </div>
  );
};

export default SearchMovieIndex;
