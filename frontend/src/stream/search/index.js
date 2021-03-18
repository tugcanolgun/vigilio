import React, { useEffect, useState } from 'react';
import { render } from 'react-dom';

import axios from 'axios';
import MainCard from '../index/MainCard';
import ErrorPanel from '../../panel/common/ErrorPanel';
import { getError } from '../../panel/common/utils';
import MovieSection from '../categories/MovieSection';

const Index = () => {
  const [fetched, setFetched] = useState(false);
  const [movieDetails, setMovieDetails] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');
  const [relativeWatchPath, setRelativeWatchPath] = useState('');

  useEffect(() => {
    searchMovies();
  }, []);

  const searchMovies = () => {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const query = urlParams.get('query');

    axios
      .get(`/api/movies?query=${query}`)
      .then((response) => {
        response.data &&
          response.data.movies &&
          setMovieDetails(response.data.movies);
        response.data &&
          response.data.relative_watch_path &&
          setRelativeWatchPath(response.data.relative_watch_path);
        setFetched(true);
      })
      .catch((err) => {
        console.error(err);
        setFetched(true);
        setErrorMessage(getError(err));
      });
  };

  const renderLoading = () => {
    if (fetched) return;

    return (
      <div className={'container'}>
        <div className={'row mb-4'}>
          <div className={'col'}>
            <h1>Loading...</h1>
          </div>
        </div>
        <div
          className={
            'row mb-0 justify-content-start justify-content-md-start justify-content-sm-center'
          }>
          <MainCard
            movieDetails={{
              poster_path_small: '/static/image/empty_poster.png',
              movie_content: [],
            }}
            relativePath={'/'}
          />
        </div>
      </div>
    );
  };

  const renderErrorMessage = () => {
    if (errorMessage === '') return;

    return (
      <div className={'container'}>
        <ErrorPanel style={{ fontSize: 'x-large' }}>{errorMessage}</ErrorPanel>
      </div>
    );
  };

  const renderResults = () => {
    if (!fetched && movieDetails.length === 0) return;

    if (fetched && movieDetails.length === 0)
      return (
        <div className="mx-1">
          <h3>No results found.</h3>
        </div>
      );

    return (
      <MovieSection
        title={'Results'}
        movieDetails={movieDetails}
        relativeWatchPath={relativeWatchPath}
      />
    );
  };

  return (
    <div className={'mb-5'}>
      {renderErrorMessage()}
      {renderLoading()}
      {renderResults()}
    </div>
  );
};

render(<Index />, document.getElementById('main'));
