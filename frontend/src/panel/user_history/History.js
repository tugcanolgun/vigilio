import React from 'react';
import { useEffect, useState } from 'react';
import axios from 'axios';
import { XCircleSvg } from '../../svg';
import { getCSRFToken } from '../background/Torrent';
import ErrorPanel from '../common/ErrorPanel';
import { getError } from '../common/utils';

const History = () => {
  const [history, setHistory] = useState([]);
  const [fetched, setFetched] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = () => {
    axios
      .get('/api/continue-movie-list')
      .then((response) => {
        setHistory(response.data.continue);
        setFetched(true);
      })
      .catch((err) => {
        console.error(err);
        setFetched(true);
      });
  };

  const removeEntry = (id) => {
    console.log(`Remove continue movie id ${id}`);

    axios
      .post(
        `/panel/api/movie-management`,
        {
          movieId: id,
          command: 'deleteContinue',
        },
        {
          headers: {
            'X-CSRFToken': getCSRFToken(),
          },
        }
      )
      .then((response) => {
        console.log(response.data);
        fetchHistory();
      })
      .catch((err) => {
        console.error(err);
        fetchHistory();
        setErrorMessage(getError(err));
      });
  };

  const renderHistory = () => {
    if (!fetched) return <b>Loading</b>;

    if (history.length === 0) return <b>There is no streaming history.</b>;

    return (
      <>
        {history.map((his) => (
          <div key={his.movie.id}>
            <div className={'row'}>
              <div className={'col-4 px-4'}>{his.updated_at.slice(0, 10)}</div>
              <div className={'col'}>{his.movie.title}</div>
              <div className={'col-2 text-end px-5'}>
                <a
                  title={`Remove ${his.movie.title} from continue movie list`}
                  onClick={() => removeEntry(his.movie.id)}>
                  <XCircleSvg />
                </a>
              </div>
            </div>
            <hr />
          </div>
        ))}
      </>
    );
  };

  const renderErrorMessage = () => {
    if (errorMessage === '') return;

    return (
      <ErrorPanel style={{ fontSize: 'x-large' }}>{errorMessage}</ErrorPanel>
    );
  };

  return (
    <div>
      {renderErrorMessage()}
      <hr />
      {renderHistory()}
    </div>
  );
};

export default History;
