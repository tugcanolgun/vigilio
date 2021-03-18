import React, { useState } from 'react';
import { ClipboardCheckSvg } from '../../svg';

const Copy = ({ text, children }) => {
  const [showCopied, setShowCopied] = useState(false);

  const copyClipboard = () => {
    navigator.clipboard
      .writeText(text)
      .then(() => {
        setShowCopied(true);
        setTimeout(() => {
          setShowCopied(false);
        }, 2000);
      })
      .catch((err) => {
        console.error('Could not copied to the clipboard.');
      });
  };

  return (
    <div
      style={{ display: 'inline', cursor: 'pointer', position: 'relative' }}
      onClick={() => copyClipboard()}>
      {children}
      {showCopied && (
        <div
          className={'mt-1 text-center'}
          style={{ position: 'absolute', width: '100%', zIndex: 10 }}>
          <ClipboardCheckSvg style={{ color: 'green' }} />
        </div>
      )}
    </div>
  );
};

export default Copy;
