import React, { useState } from 'react';
import MainCard from '../index/MainCard';
import { ArrowUpSvg } from '../../svg';

const MovieSection = ({
  title,
  movieDetails,
  relativeWatchPath,
  refreshFunc = undefined,
}) => {
  const [goToTop, setGoToTop] = useState(false);
  const renderMovies = () => {
    if (movieDetails.length === 0) return;

    return (
      <>
        <div className={'row mb-3'}>
          <div className={'col'}>
            <h1 style={{ display: 'inline-block' }}>
              {title}&nbsp;&nbsp;
              <a
                onMouseEnter={() => setGoToTop(true)}
                onMouseLeave={() => setGoToTop(false)}
                title={'Go to top'}
                href={'#'}>
                <div style={{ display: 'inline-block' }}>
                  <div className="d-flex align-items-center">
                    <ArrowUpSvg
                      style={{ color: goToTop ? '#FFFFFF' : '#686868' }}
                      width={24}
                      height={24}
                    />
                    <span
                      style={{
                        fontSize: 'medium',
                        color: goToTop ? '#AAAAAA' : '#000000',
                      }}>
                      Go to top
                    </span>
                  </div>
                </div>
              </a>
            </h1>
          </div>
        </div>
        <div
          className={
            'row mb-0 justify-content-start justify-content-md-start justify-content-sm-center'
          }>
          {movieDetails.map((movieDetail) => (
            <MainCard
              key={
                movieDetail.id !== undefined
                  ? movieDetail.id
                  : Math.random().toString().substr(2, 8)
              }
              movieDetails={movieDetail}
              refreshMyList={refreshFunc}
              relativePath={relativeWatchPath}
            />
          ))}
        </div>
      </>
    );
  };

  return <div id={title}>{renderMovies()}</div>;
};

export default MovieSection;
