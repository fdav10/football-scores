const path = require('path');
 
module.exports = {
  context: path.join(__dirname, 'footie_scores', 'webapp', 'react'),
  entry: [
    './main.js',
  ],
  output: {
    path: path.join(__dirname, 'footie_scores', 'webapp', 'static', 'js'),
    filename: 'webpack-bundle.js',
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: [
          'babel-loader',
        ],
      },
    ],
  },
  resolve: {
    modules: [
      path.join(__dirname, 'node_modules'),
    ],
  },
};
