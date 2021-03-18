import { render } from 'react-dom';
import React from 'react';
import SvgList from './SvgList';
import ColorPalette from './ColorPalette';

const Index = () => {
  return (
    <div className={'my-4'}>
      <ColorPalette />
      <hr />
      <SvgList />
    </div>
  );
};

render(<Index />, document.getElementById('root'));
