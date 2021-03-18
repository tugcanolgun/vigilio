import React from 'react';
import { useEffect, useRef } from 'react';

const Modal = ({
  children,
  title = '',
  body = 'Are you sure?',
  buttonText = 'Ok',
  refFunc,
  refFuncArgs,
}) => {
  const modalRef = useRef(null);
  const backdropRef = useRef(null);

  useEffect(() => {
    window.onclick = function (event) {
      if (event.target === modalRef.current) {
        closeModal();
      }
    };
  }, []);

  function openModal() {
    if (modalRef.current === null) return;
    modalRef.current.classList.add('show');
    modalRef.current.style.display = 'block';
    backdropRef.current.style.display = 'block';
  }

  function closeModal() {
    if (modalRef.current === null) return;
    modalRef.current.classList.remove('show');
    modalRef.current.style.display = 'none';
    backdropRef.current.style.display = 'none';
  }

  const renderModal = () => {
    return (
      <div
        ref={modalRef}
        className={'modal fade'}
        style={{ display: 'none' }}
        id="exampleModal"
        tabIndex="-1"
        aria-labelledby="exampleModalLabel"
        aria-modal="true"
        role="dialog">
        <div className="modal-dialog modal-dialog-centered" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title text-dark" id="exampleModalLabel">
                {title}
              </h5>
            </div>
            <div className="modal-body text-dark">{body}</div>
            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => closeModal()}>
                Close
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => {
                  refFunc(refFuncArgs);
                  closeModal();
                }}>
                {buttonText}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <>
      <div style={{ display: 'inline' }} onClick={() => openModal()}>
        {children}
      </div>
      {renderModal()}
      <div
        ref={backdropRef}
        style={{ display: 'none' }}
        className="modal-backdrop fade show"
        id="backdrop">
        &nbsp;
      </div>
    </>
  );
};

export default Modal;
