import React, { useEffect, useState } from 'react';
import languageCodes from './LanguageCodes';
import { XCircleSvg } from '../../svg';
import ErrorPanel from '../common/ErrorPanel';
import InfoPanel from '../common/InfoPanel';
import axios from 'axios';
import { getCSRFToken } from '../background/Torrent';
import { getError } from '../common/utils';

const SubtitleLanguages = ({ fetchSettings, subtitles = '' }) => {
  const [selected, setSelected] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');
  const [infoMessage, setInfoMessage] = useState('');
  const [searchText, setSearchText] = useState('');

  useEffect(() => {
    if (subtitles !== '' || subtitles === undefined)
      setSelected(subtitles.split(','));
  }, [subtitles]);

  const addToSelected = (val) => {
    if (selected.find((i) => i === val)) return;
    if (selected.length > 0 && selected.find((i) => i === '-')) {
      const remDash = selected.filter((i) => i !== '-');
      setSelected([...remDash, val].slice());
    } else {
      setSelected([...selected, val]);
    }
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

  const saveSubtitles = () => {
    setInfoMessage('');
    axios
      .post(
        '/panel/api/global-settings',
        {
          dotenv: {
            SUBTITLE_LANGS: selected.length === 0 ? '-' : selected.toString(),
          },
        },
        {
          headers: {
            'X-CSRFToken': getCSRFToken(),
          },
        }
      )
      .then((response) => {
        setInfoMessage('Subtitle language preferences are saved.');
        setTimeout(() => fetchSettings(), 2000);
      })
      .catch((err) => {
        setErrorMessage(getError(err));
      });
  };

  const renderSelected = () => {
    if (selected.length === 0) {
      return (
        <div className={'container my-4'}>
          <h4>0 Selected</h4>
          <button
            onClick={() => {
              saveSubtitles();
            }}
            className={'btn btn-light mx-2'}>
            Skip
          </button>
        </div>
      );
    }

    return (
      <div className={'container my-4'}>
        <h4>
          {selected.length === 1 && selected[0] === '-' ? 0 : selected.length}{' '}
          Selected
        </h4>
        <div className={'row row-cols-auto py-2'}>
          {selected.map((sel) => {
            if (sel === '-') return;

            return (
              <div
                key={sel}
                className={'col p-3 mx-2 my-1'}
                style={{ backgroundColor: '#232323' }}>
                <a
                  title={`Delete ${sel}`}
                  onClick={() => removeFromSelected(sel)}>
                  {sel}&nbsp;
                  <XCircleSvg width={16} height={16} />
                </a>
              </div>
            );
          })}
        </div>
        <div style={{ marginBottom: 10 }}>&nbsp;</div>
        <button
          onClick={() => saveSubtitles()}
          className={'btn btn-light mx-2'}>
          Save
        </button>
        <div style={{ marginBottom: 10 }}>&nbsp;</div>
      </div>
    );
  };

  const isIn = (val) => {
    return selected.find((i) => i === val) !== undefined;
  };

  const renderLanguageCodes = () => {
    return (
      <>
        {languageCodes()
          .filter((lang) =>
            lang.name.toLowerCase().includes(searchText.toLowerCase())
          )
          .map((code) => {
            return (
              <div
                key={code.iso}
                onClick={() => {
                  if (isIn(code.iso)) removeFromSelected(code.iso);
                  else addToSelected(code.iso);
                }}
                className={
                  'd-flex justify-content-between px-3 py-2 border-bottom'
                }
                style={{
                  backgroundColor: isIn(code.iso) ? '#828282' : '#232323',
                  maxWidth: 700,
                }}>
                <div style={{ display: 'inline' }}>
                  <input
                    type="checkbox"
                    checked={isIn(code.iso)}
                    readOnly={true}
                    onClick={() => null}
                  />
                  &nbsp;<a title={`Add ${code.name}`}>{code.name}</a>
                </div>
                <span>{code.iso}</span>
              </div>
            );
          })}
      </>
    );
  };

  const renderSearchBar = () => {
    return (
      <div style={{ maxWidth: 700, paddingBottom: 10 }}>
        <input
          onChange={(val) => setSearchText(val.target.value)}
          value={searchText}
          placeholder="Search a language"
          type="text"
          className="form-control default-input"
          style={{ fontSize: 'medium', paddingLeft: 10 }}
          aria-label="Search a language"
          aria-describedby="Search a langauge"
          autoFocus={true}
        />
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
      <h2>Choose Subtitle Languages</h2>
      {renderSelected()}
      {renderErrorMessage()}
      {renderInfoMessage()}
      {renderSearchBar()}
      {renderLanguageCodes()}
    </div>
  );
};

export default SubtitleLanguages;
