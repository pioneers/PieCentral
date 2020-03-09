const path = require('path');

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
    {
      test: /\.css$/i,
      use: ['style-loader', 'css-loader'],
    },
    {
      test: /\.png$/i,
      use: ['file-loader'],
    },
  ],
};

module.exports = [
  {
    entry: './renderer/index.js',
    devtool: 'cheap-module-eval-source-map',
    output: {
      path: path.join(__dirname, 'build'),
      filename: 'bundle.js',
    },
    target: 'electron-renderer',
    module: modules,
    node: {
      __dirname: true,
    },
  },
  {
    entry: './main/main-process.js',
    output: {
      path: path.join(__dirname, 'build'),
      filename: 'main.js',
    },
    target: 'electron-main',
    node: {
      __dirname: true,
      __filename: false,
    },
    module: modules,
  },
];
