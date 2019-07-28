const path = require('path');
const UglifyJSPlugin = require('uglify-js-plugin');

module.exports = (env, argv) => {
  let production = argv.mode === 'production';
  minimizer = production ? [new UglifyJSPlugin()] : [];
  return {
    entry: './client/app.js',
    module: {
      rules: [{
        test: /\.(js|jsx)$/i,
        exclude: /node_modules/,
        use: ['babel-loader', 'eslint-loader'],
      }, {
        test: /\.scss$/i,
        exclude: /node_modules/,
        use: ['style-loader', 'css-loader', 'sass-loader'],
      }, {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        use: ['file-loader'],
      }],
    },
    output: {
      path: path.join(__dirname, '/dist'),
      publicPath: '/',
      filename: 'bundle.js',
    },
    devServer: {
      contentBase: './dist',
    },
    optimization: { minimizer }
  };
};
