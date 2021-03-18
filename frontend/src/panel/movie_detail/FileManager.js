import React, { useEffect, useState } from 'react';
import axios from 'axios';
import FileBlock from './FileBlock';
import Modal from '../../stream/index/Modal';
import { getCSRFToken } from '../background/Torrent';
import ErrorPanel from '../common/ErrorPanel';
import InfoPanel from '../common/InfoPanel';
import { getError } from '../common/utils';

const FileManager = ({ movieId }) => {
  const [files, setFiles] = useState([]);
  const [fetched, setFetched] = useState(false);
  const [selected, setSelected] = useState([]);
  const [criticalFiles, setCriticalFiles] = useState([]);
  const [missingFiles, setMissingFiles] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');
  const [results, setResults] = useState('');

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = () => {
    axios
      .get(`/panel/api/files?movieId=${movieId}`)
      .then((response) => {
        if (response.data.files.length === 0) {
          setErrorMessage('Files could not be fetched.');
          return;
        }

        setFiles(response.data.files);
        setMissingFiles(response.data.missing_files);
        setCriticalFiles(response.data.used_files);
        setFetched(true);
      })
      .catch((err) => {
        setFetched(true);
        console.error(err);
        setErrorMessage(getError(err));
      });
  };

  const handleClick = ({ obj, isSelected }) => {
    if (isSelected) setSelected(selected.concat(obj));
    else {
      var tempSelected = selected;
      const index = tempSelected.indexOf(obj);
      if (index > -1) {
        tempSelected.splice(index, 1);
      }
      setSelected(tempSelected.slice());
    }
  };

  const renderFiles = () => {
    if (files.length === 0 && !fetched)
      return (
        <tr>
          <td>Loading</td>
          <td>Loading</td>
          <td>Loading</td>
          <td>Loading</td>
          <td>Loading</td>
        </tr>
      );

    if (files.length === 0) return;

    return (
      <FileBlock
        nonselectable={[files[0].name]}
        files={files}
        tab={0}
        handleClick={handleClick}
      />
    );
  };

  const renderErrorMessage = () => {
    if (errorMessage === '') return;

    return (
      <ErrorPanel style={{ fontSize: 'x-large' }}>{errorMessage}</ErrorPanel>
    );
  };

  const fileOperation = () => {
    axios
      .post(
        `/panel/api/files`,
        {
          movieId: movieId,
          command: 'deleteFiles',
          files: selected,
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
        fetchFiles();
        setSelected([]);
      })
      .catch((err) => {
        console.error(err);
        setErrorMessage(getError(err));
      });
  };

  const renderResults = () => {
    if (results === '') return;

    return <InfoPanel>{results}</InfoPanel>;
  };

  const getSelectedUrls = () => {
    var li = [];
    {
      selected.map((file) => li.push(file.full_path));
    }
    return li;
  };

  const renderHeader = () => {
    const modalBody = () => {
      const found = getSelectedUrls().some(
        (r) => criticalFiles.indexOf(r) >= 0
      );
      let critical = <></>;
      if (found)
        critical = (
          <div className={'border border-danger py-2 px-1 my-3'}>
            <b>
              <span style={{ color: 'red' }}>
                You are about to remove a necessary file/folder. This is highly
                discouraged.
              </span>
            </b>
          </div>
        );
      return (
        <>
          <div>Deleting files directly form here is not recommended.</div>
          {critical}
          <div>
            <b>
              Selecting folders will delete the folders and everything blongs to
              those folders.
            </b>
          </div>
        </>
      );
    };
    return (
      <div className={'container border-bottom'}>
        <div
          className={'row py-2'}
          style={{ backgroundColor: 'rgb(32,36,40)' }}>
          <div className={'col px-4'}>
            <h3>File Manager</h3>
          </div>
          <div className={'col'}>
            <div style={{ float: 'right' }}>
              {selected.length} selected &nbsp;
              {selected.length !== 0 ? (
                <Modal
                  title="Delete the files/folders?"
                  body={modalBody()}
                  buttonText="Delete"
                  refFunc={fileOperation}
                  refFuncArgs={{}}>
                  <button className={'btn btn-secondary btn-sm'}>
                    Delete selected
                  </button>
                </Modal>
              ) : (
                <button className={'btn btn-secondary btn-sm disabled'}>
                  Delete selected
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderMissingFiles = () => {
    if (missingFiles.length === 0) return;

    return (
      <ErrorPanel title={'There are missing files!'}>
        <ul className={'mt-2'}>
          {missingFiles.map((file) => (
            <li key={file}>
              <span>{file}</span>
            </li>
          ))}
        </ul>
      </ErrorPanel>
    );
  };

  return (
    <div className={'mt-4'}>
      {renderResults()}
      {renderErrorMessage()}
      {renderMissingFiles()}
      {renderHeader()}
      <table className="table table-hover table-dark table-sm pb-0 mb-0">
        <thead>
          <tr>
            <th scope="col">Select</th>
            <th scope="col">Name</th>
            <th scope="col">Date</th>
            <th scope="col">Type</th>
            <th scope="col">Size (MB)</th>
          </tr>
        </thead>
        <tbody>{renderFiles()}</tbody>
      </table>
      <div
        className={'pt-0 mt-0'}
        style={{ float: 'right', fontSize: 'small' }}>
        <span className={'used-file'}>Critical files</span> -{' '}
        <span>Unused files</span>
      </div>
    </div>
  );
};

export default FileManager;
