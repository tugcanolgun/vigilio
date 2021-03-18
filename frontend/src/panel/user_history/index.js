import { render } from 'react-dom';
import React from 'react';
import History from './History';

const Index = () => {
  return (
    <div>
      <h2>Viewing Activity</h2>
      <div className={'my-4'}>
        <History />
      </div>
    </div>
  );
};

render(<Index />, document.getElementById('root'));
