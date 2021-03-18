import React from 'react';

const NoMovies = () => {
  return (
    <div>
      <h3>There are no movies</h3>
      <a href={'/panel/add-movie/'} style={{ fontSize: 'large' }}>
        Add a movie
      </a>
    </div>
  );
};

export default NoMovies;
