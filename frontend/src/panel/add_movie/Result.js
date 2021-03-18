import React from 'react';
import { useState } from 'react';

const Result = ({ data, downloadFunction }) => {
  const [showDetails, setShowDetails] = useState(false);

  const renderDetails = () => {
    if (!showDetails) return;

    if (
      data.sources === undefined ||
      data.sources === [] ||
      data.sources.constructor !== Array ||
      data.sources.length === 0
    )
      return;

    return (
      <div
        className={
          'row align-items-center justify-content-center result-details-row'
        }>
        <table className="table table-hover table-dark table-sm">
          <thead>
            <tr>
              {data.sources[0].quality !== undefined ? (
                <th scope="col" style={{ paddingLeft: 14 }}>
                  Quality
                </th>
              ) : null}
              {data.sources[0].type !== undefined ? (
                <th scope="col">Type</th>
              ) : null}
              {data.sources[0].seeds !== undefined ? (
                <th scope="col">Seeds</th>
              ) : null}
              {data.sources[0].size !== undefined ? (
                <th scope="col">Size</th>
              ) : null}
              <th scope="col" style={{ paddingRight: 14 }} className={'col-1'}>
                Download
              </th>
            </tr>
          </thead>
          <tbody>
            {data.sources.map((torrent, index) => (
              <tr key={index}>
                {torrent.quality !== undefined ? (
                  <th scope="row" style={{ paddingLeft: 14 }}>
                    {torrent.quality}
                  </th>
                ) : null}
                {torrent.type !== undefined ? <td>{torrent.type}</td> : null}
                {torrent.seeds !== undefined ? <td>{torrent.seeds}</td> : null}
                {torrent.size !== undefined ? <td>{torrent.size}</td> : null}
                <td style={{ paddingRight: 14 }} className={'text-end'}>
                  <button
                    onClick={() => {
                      downloadFunction({
                        imdbId: data.imdbId,
                        source: torrent.source,
                      });
                      window.location.href = '#';
                    }}
                    className={'btn btn-secondary btn-sm p-1'}>
                    Download&Add
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div>
      <div
        style={{ cursor: 'pointer' }}
        onClick={() => setShowDetails(!showDetails)}
        className={
          'row border-top py-1 align-items-center justify-content-center result-row'
        }>
        <div className={'col-1'}>
          <img src={data.image} />
        </div>
        <div className={'col'}>
          <span>
            {data.title ? data.title : data.imdbId}{' '}
            {data.year ? `(${data.year})` : ''}
          </span>
        </div>
        <div className={'col align-center'}>
          {data.sources &&
            data.sources.constructor === Array &&
            data.sources.map((torrent, index) => {
              if (torrent.quality === undefined) return;

              return (
                <span className={'border rounded m-1 p-1'} key={index}>
                  {torrent.quality}
                </span>
              );
            })}
        </div>
      </div>
      {renderDetails()}
    </div>
  );
};

export default Result;
