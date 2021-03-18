import React, { useRef, useState } from 'react';
import { GearSvg, PlayFillSvg } from '../../svg';
import AddToListButton from './AddToListButton';
import { isEmpty } from '../utils';

const MainCard = ({
  movieDetails,
  relativePath,
  continueMovie = {},
  refreshMyList = undefined,
}) => {
  const [mouseOn, setMouseOn] = useState(false);
  const mouseOnDiv = useRef(null);

  const getResolutionText = () => {
    let resolutionWidth = 0;
    movieDetails.movie_content.map((content) => {
      if (content.resolution_width > resolutionWidth)
        resolutionWidth = content.resolution_width;
    });

    if (resolutionWidth > 2000) return '4K';
    else if (resolutionWidth <= 2000 && resolutionWidth > 1500) return 'HD';
    else if (resolutionWidth <= 1500 && resolutionWidth > 0) return 'HDTV';
    else return '';
  };

  const renderProgressBar = () => {
    if (isEmpty(continueMovie)) return;
    let percent = Math.floor(
      (continueMovie.currentSecond * 100) /
        (continueMovie.currentSecond + continueMovie.remainingSeconds)
    );
    return (
      <div
        className={'progress'}
        style={{
          height: '6px',
          borderRadius: 0,
          backgroundColor: '#5b5c5e',
          color: '#d2102a',
        }}>
        <div
          className={'progress-bar'}
          role={'progressbar'}
          style={{ width: `${percent}%` }}
          aria-valuenow={percent}
          aria-valuemin={'0'}
          aria-valuemax={'100'}>
          {' '}
        </div>
      </div>
    );
  };

  const renderResolutionBadge = () => {
    let text = getResolutionText();

    if (text === '') return;

    return (
      <div
        className={'border rounded p-1'}
        style={{
          fontSize: 'x-small',
          position: 'absolute',
          top: 5,
          right: 5,
          textShadow: '1px 1px #222',
        }}>
        <b>{text}</b>
      </div>
    );
  };

  const renderImdbRatingBadge = () => {
    if (movieDetails.imdb_score === undefined) return;

    return (
      <div
        className={'p-1'}
        style={{
          position: 'absolute',
          bottom: 10,
          left: 5,
          textShadow: '1px 1px #222',
        }}>
        <div className={'d-flex align-items-center'}>
          <img
            width={'14'}
            src={
              'https://m.media-amazon.com/images/G/01/imdb/images/plugins/imdb_star_22x21-2889147855._CB471827797_.png'
            }
          />
          &nbsp;{movieDetails.imdb_score}
        </div>
      </div>
    );
  };

  const renderReleaseYearBadge = () => {
    if (movieDetails.release_date === undefined) return;

    return (
      <div
        className={'p-1'}
        style={{
          position: 'absolute',
          bottom: 10,
          right: 5,
          textShadow: '1px 1px #222',
        }}>
        {movieDetails.release_date.slice(0, 4)}
      </div>
    );
  };

  const renderControls = () => {
    return (
      <div
        style={{
          backgroundColor: 'rgb(35, 35, 35)',
          position: 'absolute',
          bottom: 0,
          width: '100%',
          zIndex: 10,
        }}>
        <div className={'px-2 py-2 d-flex justify-content-between'}>
          <a
            title={'Play'}
            href={`/watch/${movieDetails.id}`}
            className={'btn btn-sm btn-outline-secondary rounded-pill'}
            style={{ paddingBottom: 4 }}>
            <PlayFillSvg style={{ color: '#9affde' }} />
          </a>
          <AddToListButton
            movieId={movieDetails.id}
            myList={movieDetails.my_list}
            refreshMyList={refreshMyList}
          />
          <a
            title={'Manage movie'}
            href={`/panel/movie-detail/${movieDetails.id}`}
            className={'btn btn-sm btn-outline-secondary rounded-pill'}
            style={{ paddingBottom: 4 }}>
            <GearSvg width={20} height={20} style={{ color: '#9affde' }} />
          </a>
        </div>
      </div>
    );
  };

  const renderOverTitle = () => {
    return (
      <div
        style={{
          position: 'absolute',
          bottom: '20%',
          left: 5,
          right: 5,
          zIndex: 5,
        }}
        className={'text-center'}>
        <span style={{ fontSize: 'x-large', textShadow: '2px 2px #111' }}>
          {movieDetails.title}
        </span>
      </div>
    );
  };

  const renderMouseOn = () => {
    if (mouseOnDiv.current !== null) {
      if (!mouseOn) mouseOnDiv.current.style.display = 'none';
      else mouseOnDiv.current.style.display = 'block';
    }

    if (movieDetails.id === undefined) return;

    return (
      <div style={{ display: 'none' }} ref={mouseOnDiv}>
        <a href={`${relativePath}${movieDetails.id}`}>
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              backgroundColor: 'rgba(80, 80, 80, 0.2)',
            }}>
            {' '}
          </div>
          {renderOverTitle()}
        </a>
        {renderControls()}
      </div>
    );
  };

  return (
    <div
      className={
        'col px-0 mb-4 mx-2 col-sm-auto col-md-auto col-lg-auto glow-on-hover'
      }
      onTouchStart={() => setMouseOn(true)}
      onMouseEnter={() => setMouseOn(true)}
      onMouseLeave={() => setMouseOn(false)}
      style={{
        maxWidth: 200,
        minWidth: 160,
        backgroundColor: '#2d2d2d',
        position: 'relative',
      }}>
      <a
        href={`${relativePath}${
          movieDetails.id !== undefined ? movieDetails.id : ''
        }`}>
        <img src={movieDetails.poster_path_small} width="100%" />
        {renderImdbRatingBadge()}
        {renderResolutionBadge()}
        {renderReleaseYearBadge()}
        {renderProgressBar()}
      </a>
      {renderMouseOn()}
    </div>
  );
};

export default MainCard;
