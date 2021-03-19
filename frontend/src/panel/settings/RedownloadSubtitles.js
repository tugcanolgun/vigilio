import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { getCSRFToken } from '../background/Torrent';
import { getError } from '../common/utils';
import ErrorPanel from '../common/ErrorPanel';
import InfoPanel from '../common/InfoPanel';

const RedownloadSubtitles = () => {
  const [fetched, setFetched] = useState(false);
  const [selected, setSelected] = useState([]);
  const [movies, setMovies] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');
  const [infoMessage, setInfoMessage] = useState('');
  const [searchText, setSearchText] = useState('');

  useEffect(() => {
    fetchMovies();
  }, []);

  const fetchMovies = () => {
    axios
      .get('/api/movies')
      .then((response) => {
        response.data &&
          response.data.movies &&
          setMovies(response.data.movies);
        setFetched(true);
      })
      .catch((err) => {
        setFetched(true);
        setErrorMessage(getError(err));
        console.error(err);
      });
  };

  const addToSelected = (val) => {
    if (selected.find((i) => i === val)) return;

    setSelected([...selected, val]);
  };

  const removeFromSelected = (val) => {
    if (!isIn(val)) return;

    const temp = selected;
    const index = temp.indexOf(val);
    if (index > -1) {
      temp.splice(index, 1);
    }

    setSelected(temp.slice());
  };

  const redownloadSubtitles = () => {
    setInfoMessage('');
    setErrorMessage('');
    console.log('redownloading...');
    axios
      .post(
        '/panel/api/redownload-subtitles',
        {
          movieIds: selected,
        },
        {
          headers: {
            'X-CSRFToken': getCSRFToken(),
          },
        }
      )
      .then((response) => {
        setInfoMessage('Subtitles are being re-downloaded.');
      })
      .catch((err) => {
        setErrorMessage(getError(err));
      });
  };

  const renderSelected = () => {
    return (
      <div className={'container my-4'}>
        <h4 style={{ display: 'inline-block' }}>
          {selected.length} Selected&nbsp;&nbsp;
          {selected.length !== 0 ? (
            <button
              onClick={() => redownloadSubtitles()}
              className={'btn btn-sm btn-outline-light mx-2 mb-2'}>
              Redownload Subtitles
            </button>
          ) : null}
        </h4>
      </div>
    );
  };

  const isIn = (val) => {
    return selected.find((i) => i === val) !== undefined;
  };

  const renderSearchBar = () => {
    return (
      <div
        style={{ maxWidth: 700, paddingBottom: 10 }}
        className={'d-flex justify-content-end'}>
        <input
          onChange={(val) => setSearchText(val.target.value)}
          value={searchText}
          placeholder="Search a movie"
          type="text"
          className="form-control default-input"
          style={{ paddingLeft: 10 }}
          aria-label="Search a movie"
          aria-describedby="Search a movie"
          autoFocus={true}
        />
        <button
          onClick={() => setSelected([])}
          className={'btn btn-dark btn-sm mx-2'}>
          Select None
        </button>
        <button
          onClick={() => {
            var movieIds = [];
            movies.map((movie) => movieIds.push(movie.id));
            setSelected(movieIds.slice());
          }}
          className={'btn btn-dark btn-sm'}>
          Select All
        </button>
      </div>
    );
  };

  const renderMovies = () => {
    if (!fetched) return <h2>Loading...</h2>;

    if (movies.length === 0) return <h2>No movies</h2>;

    return (
      <div>
        {movies
          .filter((mov) =>
            mov.title.toLowerCase().includes(searchText.toLowerCase())
          )
          .map((mov) => {
            return (
              <div
                key={mov.id}
                onClick={() => {
                  if (isIn(mov.id)) removeFromSelected(mov.id);
                  else addToSelected(mov.id);
                }}
                className={
                  'd-flex justify-content-between px-3 py-2 border-bottom'
                }
                style={{
                  backgroundColor: isIn(mov.id) ? '#828282' : '#232323',
                  maxWidth: 700,
                }}>
                <div style={{ display: 'inline' }}>
                  <input
                    type="checkbox"
                    checked={isIn(mov.id)}
                    readOnly={true}
                    onClick={() => null}
                  />
                  &nbsp;&nbsp;<a title={`Add ${mov.title}`}>{mov.title}</a>
                </div>
                <span>{mov.release_date.slice(0, 4)}</span>
              </div>
            );
          })}
      </div>
    );
  };

  const renderErrorMessage = () => {
    if (errorMessage === '') return;

    return <ErrorPanel>{errorMessage}</ErrorPanel>;
  };

  const renderInfoMessage = () => {
    if (infoMessage === '') return;

    return <InfoPanel>{infoMessage}</InfoPanel>;
  };

  return (
    <div>
      <h2>Re-download subtitles</h2>
      <h4 style={{ color: '#FFFF00' }}>
        This is an intensive operation. Be cautious.
      </h4>
      {renderSelected()}
      {renderErrorMessage()}
      {renderInfoMessage()}
      {renderSearchBar()}
      {renderMovies()}
    </div>
  );
};

export default RedownloadSubtitles;
