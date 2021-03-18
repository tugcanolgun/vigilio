const path = require('path');

module.exports = {
  entry: {
    Main: './src/stream/index/index.js',
    Search: './src/stream/search/index.js',
    Categories: './src/stream/categories/index.js',
    Background: './src/panel/background/index.js',
    MovieDetail: './src/panel/movie_detail/index.js',
    AddMovieYts: './src/panel/add_movie/index.js',
    UserHistory: './src/panel/user_history/index.js',
    DesignSvg: './src/design/index/index.js',
    Settings: './src/panel/settings/index.js',
    InitialSettings: './src/panel/initial_setup/index.js',
  },
  mode: 'production',
  module: {
    rules: [
      {
        test: /\.(jsx|js)$/,
        include: path.resolve(__dirname, 'src'),
        exclude: /node_modules/,
        use: [{
          loader: 'babel-loader',
          options: {
            presets: [
              ['@babel/preset-env', {
                "targets": "defaults"
              }],
              '@babel/preset-react'
            ]
          }
        }]
      }]
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name]-bundle.js'
  },
  optimization: {
    splitChunks: {
      chunks: 'all',
      name: 'Common'
    }
  }
};
