import React, { useEffect, useState } from 'react';
import { Check2Svg, DashSvg, PlusSvg } from '../../svg';
import axios from 'axios';
import { getError } from '../../panel/common/utils';
import { getCSRFToken } from '../../panel/background/Torrent';

const AddToListButton = ({
  movieId,
  refreshMyList = undefined,
  myList = null,
}) => {
  const [showSuccess, setShowSuccess] = useState(false);
  const [add, setAdd] = useState(false);

  useEffect(() => {
    setAdd(myList === null);
  }, [myList]);

  const movieListProcess = () => {
    axios
      .post(
        '/api/movies',
        {
          movieId: movieId,
          command: add ? 'addToMyList' : 'removeFromMyList',
        },
        {
          headers: {
            'X-CSRFToken': getCSRFToken(),
          },
        }
      )
      .then((response) => {
        setAdd(!add);
        setShowSuccess(true);
        if (refreshMyList !== undefined) refreshMyList();
        if (add) {
          setTimeout(() => {
            setShowSuccess(false);
          }, 2000);
        } else setShowSuccess(false);
      })
      .catch((err) => {
        console.log(err);
        console.log(getError(err));
      });
  };

  const renderIcon = () => {
    if (showSuccess) return <Check2Svg style={{ color: 'green' }} />;

    if (add) return <PlusSvg style={{ color: '#9affde' }} />;
    else return <DashSvg style={{ color: '#9affde' }} />;
  };

  return (
    <button
      title={add ? 'Add to My List' : 'Remove from My List'}
      onClick={() => movieListProcess()}
      className={'btn btn-sm btn-outline-secondary rounded-pill'}
      style={{ paddingBottom: 4 }}>
      {renderIcon()}
    </button>
  );
};

export default AddToListButton;
