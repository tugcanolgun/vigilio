import React, { useEffect, useState } from 'react';
import { XCircleSvg } from '../../svg';

const InfoPanel = ({ children, title = 'Info', style = {} }) => {
  const [close, setClose] = useState(false);

  useEffect(() => {
    setClose(false);
  }, [children]);

  if (close) return <></>;

  return (
    <div
      className={'my-1 border border-secondary rounded'}
      style={{ position: 'relative' }}>
      <div className={'info-panel-title'}>
        <span>{title}</span>
      </div>
      <div
        className={'info-panel-body'}
        style={{ whiteSpace: 'pre-wrap', ...style }}>
        {children}
      </div>
      <div style={{ position: 'absolute', right: 5, top: 5 }}>
        <button
          title={'Close the information message'}
          className={
            'btn p-0 border-0 btn-sm btn-outline-secondary rounded-pill'
          }
          onClick={() => setClose(true)}>
          <XCircleSvg style={{ color: '#AAAAAA' }} />
        </button>
      </div>
    </div>
  );
};

export default InfoPanel;
