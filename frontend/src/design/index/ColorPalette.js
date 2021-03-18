import React from 'react';
import Copy from './Copy';

function invertColor(hex) {
  if (hex.indexOf('#') === 0) {
    hex = hex.slice(1);
  }
  // convert 3-digit hex to 6-digits.
  if (hex.length === 3) {
    hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
  }
  if (hex.length !== 6) {
    throw new Error('Invalid HEX color.');
  }
  // invert color components
  var r = (255 - parseInt(hex.slice(0, 2), 16)).toString(16),
    g = (255 - parseInt(hex.slice(2, 4), 16)).toString(16),
    b = (255 - parseInt(hex.slice(4, 6), 16)).toString(16);
  // pad each with zeros and return
  return '#' + padZero(r) + padZero(g) + padZero(b);
}

function padZero(str, len) {
  len = len || 2;
  var zeros = new Array(len).join('0');
  return (zeros + str).slice(-len);
}

const ColorPalette = () => {
  const colors = [
    '#000000',
    '#232323',
    '#1E1E1E',
    '#828282',
    '#AAAAAA',
    '#FFFFFF',
    '#0D0AFD',
    '#81EF81',
    '#FFFF00',
    '#9C1616',
    '#BB1B1B',
    '#D21E1E',
  ];
  return (
    <div className={'row my-4'}>
      {colors.map((color) => {
        return (
          <div
            key={color}
            className={'col-sm-auto col-md-auto col-lg-auto my-3'}
            style={{ width: 140 }}>
            <Copy text={color}>
              <div className={'p-4'} style={{ backgroundColor: color }}>
                <span style={{ color: invertColor(color), fontSize: 'large' }}>
                  {color}
                </span>
              </div>
            </Copy>
          </div>
        );
      })}
    </div>
  );
};

export default ColorPalette;
