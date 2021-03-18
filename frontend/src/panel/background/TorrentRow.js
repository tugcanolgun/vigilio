import * as React from 'react';
import { useState } from 'react';
import Modal from '../../stream/index/Modal';
import {
  ChevronDoubleRightSvg,
  ChevronRightSvg,
  PauseSvg,
  TrashSvg,
} from '../../svg';

const TorrentRow = ({ torrent, torrentOperation }) => {
  const [check, setCheck] = useState(false);

  const renderProgressBar = (progress) => {
    const percent = Math.floor(progress * 100);
    return (
      <div className="progress">
        <div
          className={'progress-bar progress-bar-striped'}
          role={'progressbar'}
          style={{ width: `${percent}%` }}
          aria-valuenow={percent}
          aria-valuemin={0}
          aria-valuemax={100}>
          {percent} %
        </div>
      </div>
    );
  };

  const renderModalBody = () => {
    return (
      <div className="form-check">
        <input
          onChange={(e) => setCheck(e.target.checked)}
          className="form-check-input"
          type="checkbox"
          id="flexCheckDefault"
        />
        <label
          className="form-check-label"
          htmlFor="flexCheckDefault"
          onClick={() => setCheck(!check)}>
          Delete files permanently?
        </label>
      </div>
    );
  };

  return (
    <tr>
      <td scope="col">{torrent.name}</td>
      <td scope="col">{torrent.state}</td>
      <td scope="col">{renderProgressBar(torrent.progress)}</td>
      <td scope="col">
        <button
          className={'btn btn-secondary btn-sm'}
          style={{ marginRight: 2 }}
          onClick={() =>
            torrentOperation({
              infoHashes: torrent.hash,
              command: 'force_start',
            })
          }>
          <ChevronDoubleRightSvg width={16} height={16} />
        </button>
        <button
          className={'btn btn-secondary btn-sm'}
          style={{ marginRight: 2 }}
          onClick={() =>
            torrentOperation({ infoHashes: torrent.hash, command: 'resume' })
          }>
          <ChevronRightSvg width={16} height={16} />
        </button>
        <button
          className={'btn btn-secondary btn-sm'}
          style={{ marginRight: 2 }}
          onClick={() =>
            torrentOperation({ infoHashes: torrent.hash, command: 'pause' })
          }>
          <PauseSvg width={16} height={16} />
        </button>
        <Modal
          title="Delete torrent"
          body={renderModalBody()}
          buttonText="Delete"
          refFunc={torrentOperation}
          refFuncArgs={{
            infoHashes: torrent.hash,
            command: check ? 'delete_permanent' : 'delete',
          }}>
          <button className={'btn btn-secondary btn-sm'}>
            <TrashSvg width={16} height={16} />
          </button>
        </Modal>
      </td>
    </tr>
  );
};

export default TorrentRow;
