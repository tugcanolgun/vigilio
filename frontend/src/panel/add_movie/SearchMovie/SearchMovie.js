import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ErrorPanel from '../../common/ErrorPanel';
import Result from '../Result';
import { getError } from '../../common/utils';
import { inject } from '../../../stream/utils';
import { MudParser } from 'mud-parser';

const SearchMovie = ({ mudSource, addMovieRequest }) => {
  const [inputTime, setInputTime] = useState(0);
  const [searchInput, setSearchInput] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const delay = 500;
  const minChar = 3;
  let query = '';

  useEffect(() => {
    const interval = setInterval(() => check(), 500);
    return () => {
      clearInterval(interval);
    };
  }, [inputTime, mudSource]);

  const fetchTitles = () => {
    axios
      .get(inject(mudSource.apiUrl, { searchInput }))
      .then((response) => {
        let results = MudParser(mudSource, response.data);
        setResults(results);
        setLoading(false);
      })
      .catch((err) => {
        setLoading(false);
        console.log(err);
        setErrorMessage(getError(err));
      });
  };

  const check = () => {
    if (searchInput.length < minChar) return;

    if (inputTime !== 0 || Date.now() - inputTime > delay) {
      if (query !== searchInput) {
        console.log(`Searching ${searchInput}`);
        query = searchInput;
        fetchTitles();
      }
    }
  };

  const inputUpdate = (value) => {
    setSearchInput(value);
    setInputTime(Date.now());
    if (value.length > 2) setLoading(true);
  };

  const renderErrorMessage = () => {
    if (errorMessage === '') return;

    return <ErrorPanel>{errorMessage}</ErrorPanel>;
  };

  const renderInput = () => {
    return (
      <div className="input-group mb-3">
        <input
          onChange={(val) => inputUpdate(val.target.value)}
          value={searchInput}
          placeholder="Search a movie title"
          type="text"
          className="form-control default-input"
          aria-label="search a movie title"
          aria-describedby="search a movie title"
          autoFocus={true}
        />
      </div>
    );
  };

  return (
    <div>
      {renderInput()}
      {renderErrorMessage()}
      {loading && (
        <div className={'container'}>
          <div
            className={'row py-3'}
            style={{ backgroundColor: 'rgb(33, 37, 41)' }}>
            <div className={'col'}>Loading...</div>
          </div>
        </div>
      )}
      {!loading && searchInput.length >= minChar && (
        <div className={'container'}>
          <div
            className={'row py-3'}
            style={{ backgroundColor: 'rgb(33, 37, 41)' }}>
            <div className={'col'}>Results</div>
          </div>
          {results &&
            results.map((result) => (
              <Result
                key={result.imdbId}
                downloadFunction={addMovieRequest}
                data={result}
              />
            ))}
        </div>
      )}
    </div>
  );
};

export default SearchMovie;
