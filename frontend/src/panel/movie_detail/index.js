import { render } from 'react-dom';
import React from 'react';
import Detail from './Detail';
import FileManager from './FileManager';
import MovieManagement from './MovieManagement';

const Index = () => {
  return (
    <div className={'mb-5'}>
      <Detail movieId={document.getElementById('root').getAttribute('mid')} />
      <MovieManagement
        movieId={document.getElementById('root').getAttribute('mid')}
      />
      <FileManager
        movieId={document.getElementById('root').getAttribute('mid')}
      />
    </div>
  );
};

render(<Index />, document.getElementById('root'));
