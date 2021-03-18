import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { getError } from '../common/utils';
import { PlayFillSvg } from '../../svg';
import AddToListButton from '../../stream/index/AddToListButton';

const Detail = ({ movieId }) => {
  const [movieDetail, setMovieDetail] = useState({});
  const [relativeWatchPath, setRelativeWatchPath] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    fetchMovie();
  }, []);

  const fetchMovie = () => {
    axios
      .get(`/api/movies?id=${movieId}`)
      .then((response) => {
        if (response.data.movies.length === 0) {
          setErrorMessage('Movie details could not be fetched.');
          return;
        }

        setMovieDetail(response.data.movies[0]);
        setRelativeWatchPath(response.data.relative_watch_path);
      })
      .catch((err) => {
        console.error(err);
        setErrorMessage(getError(err));
      });
  };

  const getResolutionText = (resolutionWidth) => {
    if (resolutionWidth > 2000) return '4K';
    else if (resolutionWidth <= 2000 && resolutionWidth > 1500) return 'HD';
    else if (resolutionWidth <= 1500 && resolutionWidth > 0) return 'HDTV';
    else return '';
  };

  const renderResolutionBadge = () => {
    return movieDetail.movie_content.map((content) =>
      content.resolution_width !== 0 ? (
        <span key={content.created_at} className={'border rounded p-1'}>
          <b>{getResolutionText(content.resolution_width)}</b>
        </span>
      ) : null
    );
  };

  const MovieDetails = () => {
    if (movieDetail.movie_content === undefined) return;

    return (
      <div
        className={'div-background mt-4 px-0 py-3'}
        style={{
          backgroundColor: '#1b1b2f',
          position: 'relative',
          backgroundImage: `linear-gradient(to bottom, rgba(68,68,68,0.91), rgba(17,17,17,0.91)), url(${movieDetail.backdrop_path_big})`,
        }}>
        <div>
          <div
            className={'row align-items-center justify-content-center'}
            style={{ height: '100%' }}>
            <div className={'col-md-3 col-xs-6'}>
              <img
                className={'rounded img-thumbnail'}
                src={movieDetail.poster_path_big}
                width="100%"
              />
            </div>
            <div className={'col-md-6 col-xs-9'}>
              <h1>{movieDetail.title}</h1>
              <div
                className={'d-flex justify-content-between mt-1'}
                style={{ width: '100%' }}>
                {renderResolutionBadge()}
                <span style={{ color: 'yellow' }}>
                  IMDB: {movieDetail.imdb_score}
                </span>
                <span>{Math.floor(movieDetail.duration / 60)} mins</span>
              </div>
              <h3 className={'mt-1'}>Overview</h3>
              <p>{movieDetail.description}</p>

              <div className={'row'}>
                <div className={'col'}>
                  <a
                    title={'Play'}
                    href={`${relativeWatchPath}${movieId}`}
                    className={'btn btn-sm btn-outline-secondary rounded-pill'}
                    style={{ paddingBottom: 4 }}>
                    <PlayFillSvg style={{ color: '#9affde' }} />
                  </a>
                </div>
                <div className={'col'}>
                  <AddToListButton
                    movieId={movieDetail.id}
                    myList={movieDetail.my_list}
                    refreshMyList={fetchMovie}
                  />{' '}
                  &nbsp;
                  {movieDetail.my_list === null
                    ? 'Add to My List'
                    : 'Remove from My List'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderErrorMessage = () => {
    if (errorMessage === '') return;

    return (
      <div className={'my-3'}>
        <span
          className={'border border-danger'}
          style={{ color: 'red', fontSize: 'xx-large' }}>
          {errorMessage}
        </span>
      </div>
    );
  };

  return (
    <div>
      {renderErrorMessage()}
      {MovieDetails()}
    </div>
  );
};

export default Detail;
