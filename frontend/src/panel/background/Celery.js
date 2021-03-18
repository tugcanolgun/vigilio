import React from 'react';
import { useEffect, useState } from 'react';
import axios from 'axios';
import { getCSRFToken } from './Torrent';
import ErrorPanel from '../common/ErrorPanel';
import InfoPanel from '../common/InfoPanel';
import Modal from '../../stream/index/Modal';
import { getError } from '../common/utils';
import { ArrowRepeatSvg, TrashSvg } from '../../svg';

const Celery = () => {
  const [active, setActive] = useState([]);
  const [reserved, setReserved] = useState([]);
  const [scheduled, setScheduled] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');
  const [infoMessage, setInfoMessage] = useState('');
  const [fetched, setFetched] = useState(false);
  const [onMouseOver, setOnMouseOver] = useState(false);

  const resetStates = () => {
    if (active.length !== 0) setActive([]);
    if (reserved.length !== 0) setReserved([]);
    if (scheduled.length !== 0) setScheduled([]);
    if (fetched !== false) setFetched(false);
  };

  const getCeleryTasks = () => {
    resetStates();
    axios
      .get('/panel/api/celery')
      .then((response) => {
        setActive(response.data.active);
        setReserved(response.data.reserved);
        setScheduled(response.data.scheduled);
        setFetched(true);
      })
      .catch((err) => {
        console.log(err);
        setErrorMessage(getError(err));
        setFetched(true);
      });
  };

  useEffect(() => {
    getCeleryTasks();
  }, []);

  const renderInfoMessage = () => {
    if (infoMessage === '') return;

    return <InfoPanel>{infoMessage}</InfoPanel>;
  };

  const unixToDate = (unix) => {
    const dateObject = new Date(unix * 1000);
    return dateObject.toISOString().slice(0, -5);
  };

  const renderErrorMessage = () => {
    if (errorMessage === '') return;

    return (
      <ErrorPanel style={{ fontSize: 'x-large' }}>{errorMessage}</ErrorPanel>
    );
  };

  const cancelProcess = (processId) => {
    axios
      .post(
        '/panel/api/celery',
        {
          processId,
        },
        {
          headers: {
            'X-CSRFToken': getCSRFToken(),
          },
        }
      )
      .then((response) => {
        getCeleryTasks();
        setInfoMessage(`${processId} process id has been cancelled.`);
      })
      .catch((err) => {
        console.error(err);
        setErrorMessage(getError(err));
      });
  };

  const renderRow = (result) => {
    return (
      <tr key={result.id}>
        <th scope="col">{result.name}</th>
        <th scope="col">{result.args}</th>
        <th scope="col">{result.eta}</th>
        <th scope="col">
          <Modal
            title="Delete the process"
            body="Cancelling background process may affect the whole process."
            buttonText="Delete"
            refFunc={cancelProcess}
            refFuncArgs={result.id}>
            <button className={'btn btn-secondary btn-sm'}>
              <TrashSvg width={20} height={20} />
            </button>
          </Modal>
        </th>
      </tr>
    );
  };

  const renderActive = () => {
    if (active.length === 0) return;

    return (
      <table className="table table-dark">
        <tbody>
          {active.map((act) => {
            act.eta = 'Running';
            return renderRow(act);
          })}
        </tbody>
      </table>
    );
  };

  const renderReserved = () => {
    if (reserved.length === 0) return;

    return (
      <table className="table table-dark">
        <tbody>
          {reserved.map((res) => {
            if (res.request === undefined) return;
            res.request.eta = 'Running...';
            return renderRow(res.request);
          })}
        </tbody>
      </table>
    );
  };

  const renderScheduled = () => {
    if (scheduled.length === 0) return;

    return (
      <table className="table table-dark">
        <tbody>
          {scheduled.map((sch) => {
            sch.request.eta = sch.eta;
            return renderRow(sch.request);
          })}
        </tbody>
      </table>
    );
  };

  const renderEmptyOrLoading = () => {
    if (
      fetched === true &&
      errorMessage !== '' &&
      active.length === 0 &&
      scheduled.length === 0 &&
      reserved.length === 0
    )
      return;

    if (
      fetched === true &&
      active.length === 0 &&
      scheduled.length === 0 &&
      reserved.length === 0
    )
      return <h2>There are no ongoing processes</h2>;

    if (
      fetched === false &&
      active.length === 0 &&
      scheduled.length === 0 &&
      reserved.length === 0
    )
      return <h3>Loading...</h3>;
  };

  return (
    <div>
      <h1>
        Background Processes{' '}
        <a
          onClick={() => getCeleryTasks()}
          onMouseEnter={() => setOnMouseOver(true)}
          onMouseLeave={() => setOnMouseOver(false)}
          title="Reload celery tasks"
          style={{
            color: onMouseOver ? '#FFFFFF' : '#AAAAAA',
          }}>
          <ArrowRepeatSvg width={32} height={32} />
        </a>
      </h1>
      {renderInfoMessage()}
      {renderErrorMessage()}
      {renderEmptyOrLoading()}
      {active.length !== 0 ? <h2>Active</h2> : null}
      {renderActive()}
      {scheduled.length !== 0 ? <h2>Scheduled</h2> : null}
      {renderScheduled()}
      {reserved.length !== 0 ? <h2>Reserved</h2> : null}
      {renderReserved()}
    </div>
  );
};

export default Celery;
