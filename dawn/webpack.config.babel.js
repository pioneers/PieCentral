import path from 'path';
import webpack from 'webpack';
import { version } from './package.json';

const target = process.env.NODE_ENV === 'production' ? 'electron' : 'atom';
const module = {
  preLoaders: [
    { test: /\.js$/, loader: 'eslint-loader', exclude: /node_modules/ },
  ],
  loaders: [
    {
      test: /\.js$/,
      exclude: /node_modules/,
      loader: 'babel-loader',
    },
    {
      test: /\.json$/,
      loader: 'json-loader',
    },
  ],
};

const plugins = [
  new webpack.DefinePlugin({
    VERSION: JSON.stringify(version),
  }),
  new webpack.DefinePlugin({
    "global.GENTLY": false,
  })
];

export default [
  {
    entry: [ 'babel-polyfill', './renderer/index.js' ],
    devtool: 'cheap-module-eval-source-map',
    eslint: {
      configFile: './.eslintrc',
    },
    output: { path: __dirname + '/build/', filename: 'bundle.js' },
    target,
    module,
    plugins,
  },
  {
    entry: './main/main-develop.js',
    eslint: {
      configFile: './.eslintrc',
    },
    output: { path: __dirname + '/build/', filename: 'main.js' },
    target,
    node: {
      __dirname: false,
      __filename: false,
    },
    module,
    plugins,
  },
];
