import React, { useState } from 'react';

const AddMovieForm = ({ addMovieRequest }) => {
  const [imdbId, setImdbId] = useState('');
  const [source, setSource] = useState('');

  return (
    <div>
      <div className="col-sm-auto col-md-auto col-lg-auto my-1">
        <input
          onChange={(val) => setImdbId(val.target.value)}
          value={imdbId}
          placeholder="*Copy an IMDB link or IMDB ID"
          type="text"
          className="form-control default-input"
          aria-label=""
          aria-describedby="Copy an IMDB link or IMDB ID"
          autoFocus={true}
          minLength={9}
        />
      </div>

      <div className="col-sm-auto col-md-auto col-lg-auto my-2">
        <textarea
          onChange={(val) => setSource(val.target.value)}
          value={source}
          className="form-control default-input"
          name="torrent_source"
          cols="40"
          rows="8"
          placeholder={'*Copy a torrent magnet or link'}
          style={{
            width: '100%',
          }}
          required
          id="id_torrent_source">
          {' '}
        </textarea>
      </div>
      <div className="col-sm-auto col-md-auto col-lg-auto text-end">
        <button
          onClick={() => addMovieRequest({ imdbId, source })}
          className={'btn btn-light'}>
          Download & Add
        </button>
      </div>
    </div>
  );
};

export default AddMovieForm;
