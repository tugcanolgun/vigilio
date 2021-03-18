import React, { useRef, useState } from 'react';
import {
  FileEarmarkSvg,
  FilePlaySvg,
  FileTextSvg,
  OpenFolderSvg,
} from '../../svg';

const getIcon = (suffix) => {
  let url = '';
  switch (suffix) {
    case '.txt':
      url = <FileTextSvg width={24} height={24} />;
      break;
    case '.mp4':
      url = <FilePlaySvg width={24} height={24} />;
      break;
    case undefined:
      url = <OpenFolderSvg width={24} height={24} />;
      break;
    default:
      url = <FileEarmarkSvg width={24} height={24} />;
      break;
  }

  return url;
};

const Contains = (list, item) => {
  var index = list.indexOf(item);
  return index !== -1;
};

const Row = ({
  file,
  handleClick,
  tab,
  children,
  nonselectable = [],
  paddingLeft = 30,
}) => {
  const [bg, setBg] = useState({});
  const checkbox = useRef(null);
  const selectable = !Contains(nonselectable, file.name);
  const usedClass = file.used === true ? 'used-file' : '';

  const onHover = () => {
    if (checkbox.current)
      setBg(
        checkbox.current.checked
          ? { backgroundImage: 'linear-gradient(#828282, #68747d)' }
          : {}
      );
  };
  const offHover = () => {
    if (checkbox.current)
      setBg(
        checkbox.current.checked
          ? { backgroundImage: 'linear-gradient(#787878, #616c74)' }
          : {}
      );
  };
  const onClick = () => {
    if (selectable) {
      handleClick({ obj: file, isSelected: !checkbox.current.checked });
      checkbox.current.checked = !checkbox.current.checked;
      onHover();
    }
  };

  return (
    <>
      <tr
        onMouseEnter={() => onHover()}
        onMouseLeave={() => offHover()}
        onClick={() => onClick()}
        key={file.full_path}>
        <th className={usedClass} style={{ ...bg }}>
          {selectable ? (
            <input ref={checkbox} type="checkbox" onClick={() => onClick()} />
          ) : null}
        </th>
        <td
          className={usedClass}
          style={{ ...bg, paddingLeft: tab * paddingLeft + paddingLeft / 3 }}
          title={file.name}>
          {getIcon(file.suffix)}&nbsp;{file.name}
        </td>
        <td className={usedClass} style={{ ...bg }}>
          {file.date}
        </td>
        <td className={usedClass} style={{ ...bg }}>
          {getType(file.suffix)}
        </td>
        <td className={usedClass} style={{ ...bg }}>
          {file.size ? parseFloat(file.size / 1048576).toFixed(2) : null}
        </td>
      </tr>
      {children}
    </>
  );
};

const FileBlock = ({ files, handleClick, nonselectable = [], tab = 0 }) => {
  if (files.length === 0) return <></>;

  return (
    <>
      {files.map((f) => {
        if (f.files && f.files.length !== 0)
          return (
            <Row
              nonselectable={nonselectable}
              key={f.full_path}
              file={f}
              tab={tab}
              handleClick={handleClick}>
              <FileBlock
                nonselectable={nonselectable}
                tab={tab + 1}
                files={f.files}
                handleClick={handleClick}
              />
            </Row>
          );
        else
          return (
            <Row
              nonselectable={nonselectable}
              key={f.full_path || 'root'}
              file={f}
              tab={tab}
              handleClick={handleClick}
            />
          );
      })}
    </>
  );
};

const getType = (suffix) => {
  let type = '';
  switch (suffix) {
    case '.srt':
      type = 'Subtitle️';
      break;
    case '.vtt':
      type = 'Subtitle️';
      break;
    case '.mp4':
      type = 'Video';
      break;
    case '.webm':
      type = 'Video';
      break;
    case '.mkv':
      type = 'Raw Video';
      break;
    case undefined:
      type = 'Folder';
      break;
    default:
      type = 'File';
      break;
  }

  return type;
};

export default FileBlock;
