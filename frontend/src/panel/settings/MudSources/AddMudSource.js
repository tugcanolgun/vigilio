import React, { useEffect, useState } from 'react';
import { ArrowLeftCircleSvg } from '../../../svg';
import ErrorPanel from '../../common/ErrorPanel';
import InfoPanel from '../../common/InfoPanel';
import { getError } from '../../common/utils';
import { checkMudSchema } from 'mud-parser';
import axios from 'axios';
import { getCSRFToken } from '../../background/Torrent';

const AddMudSource = ({ setPage = null }) => {
  const [name, setName] = useState('');
  const [schema, setSchema] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [infoMessage, setInfoMessage] = useState('');
  const [buttonEnabled, setButtonEnabled] = useState(false);

  useEffect(() => {
    setErrorMessage('');
    if (schema !== '') {
      try {
        checkMudSchema(JSON.parse(schema));
        if (name !== '') {
          setButtonEnabled(true);
        }
      } catch (e) {
        setErrorMessage(getError(e));
        setButtonEnabled(false);
      }
    }
    if (name === '') setButtonEnabled(false);
  }, [schema, name]);

  const saveSource = () => {
    if (name === '' || schema === '') return;

    try {
      checkMudSchema(JSON.parse(schema));
    } catch (e) {
      return;
    }
    axios
      .post(
        '/panel/api/mud-sources',
        {
          name,
          source: schema,
        },
        {
          headers: {
            'X-CSRFToken': getCSRFToken(),
          },
        }
      )
      .then((response) => {
        setPage('list');
      })
      .catch((err) => {
        console.log(err);
        setErrorMessage(getError(err));
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

  return (
    <div>
      <button
        onClick={() => setPage !== null && setPage('list')}
        className="btn btn-sm btn-secondary mb-3">
        <div className="d-flex align-items-center">
          <ArrowLeftCircleSvg />
          &nbsp; Go back to the list
        </div>
      </button>
      <div className="my-1">
        You can find sources at{' '}
        <a href="https://vigiliosources.docaine.com" target="_blank">
          Vigilio sources
        </a>
        . Be cautious of the contents of the sources since they may include
        illegal content.
      </div>
      <div className="my-2">
        {renderErrorMessage()}
        {renderInfoMessage()}
      </div>
      <input
        onChange={(val) => setName(val.target.value)}
        value={name}
        placeholder="*Give a name to this source"
        type="text"
        className="form-control default-input"
        aria-label="Give a name to the source"
        aria-describedby="Give a name to the source"
        autoFocus={true}
      />

      <textarea
        onChange={(val) => setSchema(val.target.value)}
        value={schema}
        className="form-control default-input my-2"
        name="Schema"
        cols="40"
        rows="1"
        placeholder="*Copy the source"
        aria-label="Copy the source"
        aria-describedby="Copy the source"
        style={{
          width: '100%',
        }}
        required
        id="id_schema">
        {' '}
      </textarea>
      <button
        className={'btn btn-light ' + (buttonEnabled ? '' : 'disabled')}
        onClick={() => saveSource()}>
        Save
      </button>
    </div>
  );
};

export default AddMudSource;
