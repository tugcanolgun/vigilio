import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ErrorPanel from '../common/ErrorPanel';
import { getCSRFToken } from '../background/Torrent';
import InfoPanel from '../common/InfoPanel';
import Modal from '../../stream/index/Modal';
import { getError } from '../common/utils';
import { GearSvg } from '../../svg';

const MovieManagement = ({ movieId }) => {
  const [isContinueMovie, setIsContinueMovie] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [results, setResults] = useState('');
  const [showDeleteEverything, setShowDeleteEverything] = useState(false);

  useEffect(() => {
    getContinueMovie();
  }, []);

  const getContinueMovie = () => {
    axios
      .get(`/api/continue-movie-list?id=${movieId}`)
      .then((response) => {
        response.data &&
          response.data.continue &&
          response.data.continue.length > 0 &&
          setIsContinueMovie(true);
        response.data &&
          response.data.continue &&
          response.data.continue.length === 0 &&
          setIsContinueMovie(false);
      })
      .catch((err) => {
        console.error(err);
        setErrorMessage(getError(err));
      });
  };

  const removeContinueMovie = (command) => {
    setResults('');
    setErrorMessage('');
    axios
      .post(
        `/panel/api/movie-management`,
        {
          movieId: movieId,
          command: command,
        },
        {
          headers: {
            'X-CSRFToken': getCSRFToken(),
          },
        }
      )
      .then((response) => {
        console.log(response.data);
        if (response.data && response.data.operation)
          setResults(response.data.operation);
        else setResults(JSON.stringify(response.data));
        getContinueMovie();
        if (command === 'deleteEverything') location.href = '/panel';
      })
      .catch((err) => {
        console.error(err);
        setErrorMessage(getError(err));
        getContinueMovie();
      });
  };

  const renderErrorMessage = () => {
    if (errorMessage === '') return;

    return (
      <ErrorPanel style={{ fontSize: 'x-large' }}>{errorMessage}</ErrorPanel>
    );
  };

  const renderRemoveContinue = () => {
    if (!isContinueMovie) return;

    return (
      <div className={'row'}>
        <hr />
        <div className={'col'}>
          This video is listed under continue watching.
        </div>
        <div className={'col'}>
          <button
            onClick={() => removeContinueMovie('deleteContinue')}
            className={'btn btn-secondary btn-sm'}>
            Remove video from continue watching
          </button>
        </div>
      </div>
    );
  };

  const renderModalBody = () => (
    <div>
      <span style={{ fontSize: 'large', color: 'red' }}>
        This operation will delete everything related to this movie.
        <br />
        This operation cannot be reverted.
      </span>
    </div>
  );

  const renderRemoveEverything = () => {
    const renderRemoveEverythingButton = () => {
      if (!showDeleteEverything) return;

      return (
        <Modal
          title="Delete the movie?"
          body={renderModalBody()}
          buttonText="Delete"
          refFunc={removeContinueMovie}
          refFuncArgs={'deleteEverything'}>
          <button className={'btn btn-danger btn-sm'}>Delete this movie</button>
        </Modal>
      );
    };
    return (
      <div className={'row mt-3'}>
        <hr />
        <div className={'col'}>
          <p>Remove this movie and everything related to it</p>
        </div>
        <div className={'col'}>
          {!showDeleteEverything && (
            <a onClick={() => setShowDeleteEverything(true)}>
              Click here to reveal the button.
            </a>
          )}
          {renderRemoveEverythingButton()}
        </div>
      </div>
    );
  };

  const renderResults = () => {
    if (results === '') return;

    return <InfoPanel>{results}</InfoPanel>;
  };

  return (
    <div>
      {renderErrorMessage()}
      {renderResults()}
      <div className={'container movie-mng-body px-3'}>
        <h3>
          <GearSvg style={{ marginBottom: 4, marginRight: 10 }} />
          Management tools
        </h3>
        {renderRemoveContinue()}
        {renderRemoveEverything()}
      </div>
    </div>
  );
};

export default MovieManagement;
