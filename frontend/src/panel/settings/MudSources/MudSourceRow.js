import React from 'react';
import { TrashSvg } from '../../../svg';
import Modal from '../../../stream/index/Modal';

const MudSourceRow = ({ source, deleteFunc }) => {
  return (
    <>
      <div className="row mb-3">
        <div className="col">{source.name}</div>
        <div className="col-1">
          <Modal
            title="Delete the source?"
            body="Are you sure you want to delete this source?"
            buttonText="Delete"
            refFunc={deleteFunc}
            refFuncArgs={{ sourceId: source.id }}>
            <button className={'btn btn-secondary btn-sm'} onClick={() => null}>
              <TrashSvg width={16} height={16} />
            </button>
          </Modal>
        </div>
      </div>
      <div className="row">
        <hr />
      </div>
    </>
  );
};

export default MudSourceRow;
