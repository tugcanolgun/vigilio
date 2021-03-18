import * as React from 'react';
import { useEffect, useState } from 'react';
import axios from 'axios';
import ErrorPanel from '../common/ErrorPanel';
import InfoPanel from '../common/InfoPanel';
import { getError } from '../common/utils';
import TorrentRow from './TorrentRow';

const getCSRFToken = () => {
  return document.querySelector('[name=csrfmiddlewaretoken]').value;
};

const Torrent = () => {
  const [torrents, setTorrents] = useState([]);
  const [fetched, setFetched] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [infoMessage, setInfoMessage] = useState('');
  let refresh = null;
  let refreshInterval = 5000;
  let errorCount = 0;

  useEffect(() => {
    getTorrents();
    refresh = setInterval(function () {
      getTorrents();
    }, refreshInterval);
  }, []);

  const getTorrents = () => {
    axios
      .get('/panel/api/t_status')
      .then((response) => {
        response.data &&
          response.data.torrents &&
          setTorrents(response.data.torrents);
        if (response.data === undefined || response.data.torrents === undefined)
          setErrorMessage('There was a problem getting the list');
        else setErrorMessage('');
        setFetched(true);
      })
      .catch((err) => {
        errorCount++;
        console.log(err);
        setErrorMessage(getError(err));
        setFetched(true);
        if (errorCount > 2) clearInterval(refresh);
      });
  };

  const renderTorrents = () => {
    if (errorMessage !== '') return;

    if (!fetched && torrents.length === 0) {
      return (
        <tr>
          <td scope="col">Loading...</td>
          <td scope="col">Loading...</td>
          <td scope="col">Loading...</td>
          <td scope="col">Loading...</td>
        </tr>
      );
    }

    if (fetched && torrents.length === 0) {
      return (
        <tr>
          <td scope="col">No results</td>
          <td scope="col">No results</td>
          <td scope="col">No results</td>
          <td scope="col">No results</td>
        </tr>
      );
    }

    const torrentOperation = ({ infoHashes, command }) => {
      axios
        .post(
          '/panel/api/t_status',
          {
            infoHashes: Array.isArray(infoHashes) ? infoHashes : [infoHashes],
            command: command,
          },
          {
            headers: {
              'X-CSRFToken': getCSRFToken(),
            },
          }
        )
        .then((response) => {
          setInfoMessage(`${command} operation is successful.`);
        })
        .catch((err) => {
          console.error(err);
          setErrorMessage(getError(err));
        });
    };

    return torrents.map((torrent) => (
      <TorrentRow
        key={torrent.hash}
        torrent={torrent}
        torrentOperation={torrentOperation}
      />
    ));
  };

  const renderInfoMessage = () => {
    if (infoMessage === '') return;

    return <InfoPanel>{infoMessage}</InfoPanel>;
  };

  const renderErrorMessage = () => {
    if (errorMessage === '') return;

    return (
      <ErrorPanel style={{ fontSize: 'x-large' }}>{errorMessage}</ErrorPanel>
    );
  };

  return (
    <div>
      <h1>Torrent status</h1>
      {renderInfoMessage()}
      {renderErrorMessage()}
      <div className={'d-flex justify-content-end'}>
        Table refreshes every {refreshInterval / 1000} seconds.
      </div>
      <table className="table table-dark">
        <thead>
          <tr>
            <td scope="col">Name</td>
            <td scope="col">Status</td>
            <td scope="col">Percentage</td>
            <td scope="col justify-content-end">Manage</td>
          </tr>
        </thead>
        <tbody>{renderTorrents()}</tbody>
      </table>
    </div>
  );
};

export default Torrent;
export { getCSRFToken };
