import React, { useState } from 'react';
import * as Svg from '../../svg';
import Copy from './Copy';

const SvgList = () => {
  const [size, setSize] = useState(64);
  var li = [];
  for (const key in Svg) {
    li.push(Svg[key]);
  }

  const renderIcons = () => {
    return (
      <div className={'row'}>
        {li.map((s) => {
          let text = `<${s.name} width={${size}} height={${size}} />`;
          return (
            <div
              key={s.name}
              className={'col-sm-auto col-md-auto col-lg-auto my-3'}>
              <Copy text={text}>
                <s.prototype.constructor width={size} height={size} />
              </Copy>
            </div>
          );
        })}
      </div>
    );
  };

  const renderControls = () => {
    return (
      <div className={'row my-2'}>
        <div className={'col'}>
          <div style={{ width: 120 }}>
            <div className="input-group input-group-sm mb-3">
              <span className="input-group-text" id="inputGroup-sizing-sm">
                Size
              </span>
              <input
                value={size}
                type="text"
                className="form-control"
                aria-label="Sizing example input"
                onChange={(event) => setSize(Number(event.target.value))}
                aria-describedby="inputGroup-sizing-sm"
              />
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className={'container'}>
      {renderControls()}
      {renderIcons()}
    </div>
  );
};

export default SvgList;
