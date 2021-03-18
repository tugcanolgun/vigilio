import { render } from 'react-dom';
import React from 'react';
import Torrent from './Torrent';
import Celery from './Celery';

const Index = () => {
  return (
    <div className={'mb-4'}>
      <Torrent />
      <hr />
      <Celery />
    </div>
  );
};

render(<Index />, document.getElementById('root'));
