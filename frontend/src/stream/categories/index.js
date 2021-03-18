import React, { useEffect, useState } from 'react';
import { render } from 'react-dom';

import MovieSection from './MovieSection';
import axios from 'axios';
import ErrorPanel from '../../panel/common/ErrorPanel';
import { getError } from '../../panel/common/utils';
import NoMovies from '../index/NoMovies';

const Index = () => {
  const [categories, setCategories] = useState([]);
  const [fetched, setFetched] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [relativeWatchPath, setRelativeWatchPath] = useState('');

  useEffect(() => {
    fetchMovieList();
  }, []);

  const fetchMovieList = () => {
    axios
      .get('/api/categories')
      .then((response) => {
        response.data &&
          response.data.categories &&
          setCategories(response.data.categories);
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
      <MovieSection
        title={'Loading...'}
        movieDetails={[
          {
            poster_path_small: '/static/image/empty_poster.png',
            movie_content: [],
          },
        ]}
        relativeWatchPath={'#'}
      />
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

  const renderNoMovies = () => {
    if (fetched) {
      const exists = categories.find((i) => i.movies && i.movies.length !== 0);
      if (exists === undefined) return <NoMovies />;
    }
  };

  const renderJumpList = () => {
    if (!fetched) return;

    if (categories.find((i) => i.movies.length !== 0) === undefined) return;

    return (
      <div className={'d-flex flex-wrap justify-content-start mb-2'}>
        Jump to category &nbsp;|&nbsp;&nbsp;
        {categories.map((category) => {
          if (category.movies && category.movies.length === 0) return;

          return (
            <div className={'bd-highlight text-nowrap'}>
              <a href={`#${category.name}`}>{category.name}</a>
              &nbsp;&nbsp;
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className={'mb-5'}>
      {renderErrorMessage()}
      {renderLoading()}
      {renderNoMovies()}
      {renderJumpList()}
      {categories.map((category) => (
        <MovieSection
          key={category.name}
          title={category.name}
          movieDetails={category.movies}
          relativeWatchPath={relativeWatchPath}
          refreshFunc={fetchMovieList}
        />
      ))}
    </div>
  );
};

render(<Index />, document.getElementById('main'));
