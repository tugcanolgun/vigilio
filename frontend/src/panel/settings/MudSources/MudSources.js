import React, { useEffect, useState } from 'react';
import { getError } from '../../common/utils';
import axios from 'axios';
import MudSourceRow from './MudSourceRow';
import ErrorPanel from '../../common/ErrorPanel';
import InfoPanel from '../../common/InfoPanel';
import AddMudSource from './AddMudSource';
import { PlusSvg } from '../../../svg';
import { getCSRFToken } from '../../background/Torrent';

const MudSources = () => {
  const [fetched, setFetched] = useState(false);
  const [sources, setSources] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');
  const [infoMessage, setInfoMessage] = useState('');
  const [page, setPage] = useState('list');

  useEffect(() => {
    fetchMudSources();
  }, [page]);

  const fetchMudSources = () => {
    axios
      .get('/panel/api/mud-sources')
      .then((response) => {
        setSources(response.data);
        setFetched(true);
      })
      .catch((err) => {
        setErrorMessage(getError(err));
        setFetched(true);
      });
  };

  const renderErrorMessage = () => {
    if (errorMessage === '') return;

    return <ErrorPanel>{errorMessage}</ErrorPanel>;
  };

  const renderInfoMessage = () => {
    if (infoMessage === '') return;

    return <InfoPanel>{infoMessage}</InfoPanel>;
  };

  const deleteSource = ({ sourceId }) => {
    if (sourceId === null || sourceId === undefined) {
      console.log(`Source ID ${sourceId} is invalid.`);
      setErrorMessage('Could not delete the source.');
      return;
    }

    axios
      .delete(`/panel/api/mud-source/${sourceId}`, {
        headers: {
          'X-CSRFToken': getCSRFToken(),
        },
      })
      .then((response) => {
        setInfoMessage('The source has been deleted.');
        fetchMudSources();
      })
      .catch((err) => {
        console.log(err);
        setErrorMessage(getError(err));
      });
  };

  const renderBody = () => {
    if (!fetched) return <h2>Loading...</h2>;

    if (page === 'add') return <AddMudSource setPage={setPage} />;

    if (sources.length === 0)
      return (
        <div className="container-fluid">
          <button
            className="btn btn-sm btn-secondary mb-3"
            onClick={() => setPage('add')}>
            <div className="d-flex align-items-center">
              <PlusSvg /> Add a source
            </div>
          </button>
          <h2>There are no sources</h2>
        </div>
      );

    return (
      <div>
        {renderErrorMessage()}
        {renderInfoMessage()}
        <div className="container-fluid">
          <button
            className="btn btn-sm btn-secondary mb-3"
            onClick={() => setPage('add')}>
            <div className="d-flex align-items-center">
              <PlusSvg /> Add a source
            </div>
          </button>
          <h3>Existing sources</h3>
        </div>
        <hr />
        <div className="container-fluid">
          {sources.map((source) => {
            return (
              <MudSourceRow
                key={source.id}
                source={source}
                deleteFunc={deleteSource}
              />
            );
          })}
        </div>
      </div>
    );
  };
  return <div>{renderBody()}</div>;
};

export default MudSources;
