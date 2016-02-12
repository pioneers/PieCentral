var path = require('path');
var webpack = require('webpack')

module.exports = {
  entry: './js/index.js',
  output: { path: __dirname + '/build/', filename: 'bundle.js' },
  target: 'atom',
  module: {
    loaders: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        loader: "babel-loader",
        query: {
          presets: ['es2015', 'react']
        }
      }
    ]
  }
};
