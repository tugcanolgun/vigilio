import React, { useEffect, useState } from 'react';
import { XCircleSvg } from '../../svg';

const ErrorPanel = ({ children, title = 'Error', style = {} }) => {
  const [close, setClose] = useState(false);

  useEffect(() => {
    setClose(false);
  }, [children]);

  if (close) return <></>;

  return (
    <div
      className={'my-1 border border-danger rounded'}
      style={{ position: 'relative' }}>
      <div className={'error-panel-title'}>
        <span>{title}</span>
      </div>
      <div
        className={'error-panel-body'}
        style={{ whiteSpace: 'pre-wrap', ...style }}>
        {children}
      </div>
      <div style={{ position: 'absolute', right: 5, top: 5 }}>
        <button
          title={'Close the error message'}
          className={
            'btn p-0 border-0 btn-sm btn-outline-secondary rounded-pill'
          }
          onClick={() => setClose(true)}>
          <XCircleSvg />
        </button>
      </div>
    </div>
  );
};

export default ErrorPanel;
