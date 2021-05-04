import * as React from 'react';
import { useEffect, useState } from 'react';
import axios from 'axios';
import MainCard from './MainCard';
import { getError } from '../../panel/common/utils';
import ErrorPanel from '../../panel/common/ErrorPanel';
import MovieSection from '../categories/MovieSection';
import NoMovies from './NoMovies';

const Main = () => {
  const [continueWatchingMovies, setContinueWatchingMovies] = useState({});
  const [continueMovieIds, setContinueMovieIds] = useState([]);
  const [movieDetails, setMovieDetails] = useState([]);
  const [relativeWatchPath, setRelativeWatchPath] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [fetched, setFetched] = useState(false);

  useEffect(() => {
    fetchContinueMovieList();
    fetchMovieList();
  }, []);

  const refreshMyList = () => {
    fetchContinueMovieList();
    fetchMovieList();
  };

  const fetchMovieList = () => {
    axios
      .get('/api/movies')
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
        setFetched(true);
        setErrorMessage(getError(err));
        console.error(err);
      });
  };

  const fetchContinueMovieList = () => {
    axios
      .get('/api/continue-movie-list')
      .then((response) => {
        setContinueWatchingMovies(response.data.continue);
        setRelativeWatchPath(response.data.relative_watch_path);
        return response.data.continue;
      })
      .then((movies) => {
        var movieIds = [];
        movies.map((movie) => movieIds.push(movie.movie.id));
        setContinueMovieIds(movieIds);
      })
      .catch((err) => {
        console.error(err);
        setErrorMessage(getError(err));
      });
  };

  const renderContinueWatching = () => {
    if (continueMovieIds.length === 0) return;

    return (
      <>
        <div className={'row mb-4'}>
          <div className={'col'}>
            <h1>Continue Watching</h1>
          </div>
        </div>
        <div className={'row mb-0'}>
          {continueWatchingMovies.map((continueMovie) => (
            <MainCard
              key={
                continueMovie.user.toString() +
                continueMovie.movie.id.toString()
              }
              movieDetails={continueMovie.movie}
              relativePath={relativeWatchPath}
              continueMovie={{
                currentSecond: continueMovie.current_second,
                remainingSeconds: continueMovie.remaining_seconds,
              }}
              refreshMyList={refreshMyList}
            />
          ))}
        </div>
      </>
    );
  };

  const renderMyList = () => {
    if (fetched && movieDetails.length === 0) return;

    if (movieDetails.length === 0) return;

    let tmpMyList = movieDetails.filter((detail) => detail.my_list !== null);
    if (tmpMyList === undefined || tmpMyList.length === 0) return;

    tmpMyList = JSON.parse(JSON.stringify(tmpMyList));
    tmpMyList.sort((a, b) => {
      const f = new Date(a.my_list.created_at);
      const s = new Date(b.my_list.created_at);
      return f < s ? 1 : -1;
    });

    return (
      <MovieSection
        title={'My List'}
        movieDetails={tmpMyList}
        relativeWatchPath={relativeWatchPath}
        refreshFunc={refreshMyList}
      />
    );
  };

  const renderPopularMovies = () => {
    if (fetched && movieDetails.length === 0 && continueMovieIds.length === 0)
      return <NoMovies />;

    if (movieDetails.length === 0) return;

    var tempMovieDetails = [];
    movieDetails.map((movieDetail) => {
      if (!continueMovieIds.includes(movieDetail.id)) {
        tempMovieDetails.push(movieDetail);
      }
    });

    if (tempMovieDetails.length === 0) return;

    return (
      <MovieSection
        title={'Popular Movies'}
        movieDetails={tempMovieDetails}
        refreshFunc={refreshMyList}
        relativeWatchPath={relativeWatchPath}
      />
    );
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
      <ErrorPanel style={{ fontSize: 'x-large' }}>{errorMessage}</ErrorPanel>
    );
  };

  return (
    <div className={'mb-5'}>
      {renderErrorMessage()}
      {renderContinueWatching()}
      {renderMyList()}
      {renderPopularMovies()}
      {renderLoading()}
    </div>
  );
};

export default Main;
