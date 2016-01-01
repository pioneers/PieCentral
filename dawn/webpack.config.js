var webpack = require('webpack');
module.exports = {
  entry: {
    app: ['webpack/hot/dev-server', './js/index.js'],
  },
  output: {
    path: './public/built',
    filename: 'bundle.js',
    publicPath: 'http://localhost:8080/built/'
  },
  devServer: {
    contentBase: './public',
    publicPath: 'http://localhost:8080/built/'
  },
  module: {
   loaders: [
     {
       test: /\.js$/,
       loader: 'babel-loader',
       query: {
         presets: ['es2015', 'react']
       },
       exclude: /node_modules/
     },
   ]
  },
  plugins: [
   new webpack.HotModuleReplacementPlugin()
 ]
}
