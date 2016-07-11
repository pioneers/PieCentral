var path = require('path');
var webpack = require('webpack')

var modules = {
  preLoaders: [
    { test: /\.js$/, loader: 'eslint-loader', exclude: /node_modules/ }
  ],
  loaders: [
    {
      test: /\.js$/,
      exclude: /node_modules/,
      loader: "babel-loader",
      query: {
        presets: [ 'es2015', 'react' ],
        plugins: [ 'transform-object-rest-spread', 'transform-regenerator' ]
      }
    },
    {
      test: /\.json$/,
      loader: 'json-loader'
    }
  ]
};

var plugins = [
  new webpack.DefinePlugin({
    VERSION: JSON.stringify(require('./package.json').version)
  }),
  new webpack.DefinePlugin({
    "global.GENTLY": false
  })
];

module.exports = [{
  entry: './renderer/index.js',
  devtool: 'cheap-module-eval-source-map',
  eslint: {
    configFile: './.eslintrc'
  },
  output: { path: __dirname + '/build/', filename: 'bundle.js' },
  target: 'atom',
  module: modules,
  plugins: plugins
}, {
  entry: './main/main-develop.js',
  eslint: {
    configFile: './.eslintrc'
  },
  output: { path: __dirname + '/build/', filename: 'main.js' },
  target: 'atom',
  node: {
    __dirname: false,
    __filename: false
  },
  module: modules,
  plugins: plugins
}];
