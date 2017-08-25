import path from 'path';
import webpack from 'webpack';
import { version } from './package.json';

const target = 'electron';
const modules = {
  rules: [
    {
      test: /\.js$/,
      exclude: /node_modules/,
      enforce: 'pre',
      loader: 'eslint-loader',
    },
    {
      test: /\.js$/,
      exclude: /node_modules/,
      loader: 'babel-loader',
    },
  ],
};

const plugins = [
  new webpack.optimize.ModuleConcatenationPlugin(),
  new webpack.DefinePlugin({
    VERSION: JSON.stringify(version),
  }),
];

export default [
  {
    entry: './renderer/index.js',
    devtool: 'cheap-module-eval-source-map',
    output: {
      path: path.join(__dirname, 'build'),
      filename: 'bundle.js',
    },
    target,
    module: modules,
    plugins,
  },
  {
    entry: './main/main-process.js',
    output: {
      path: path.join(__dirname, 'build'),
      filename: 'main.js',
    },
    target,
    node: {
      __dirname: false,
      __filename: false,
    },
    module: modules,
    plugins,
  },
];
