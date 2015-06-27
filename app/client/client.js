var React = require('react');
var Router = require('react-router');

var routes = require('./routes');

var rootProps = JSON.parse(document.getElementById('root-props').innerHTML)

Router.run(routes, Router.HistoryLocation, function (Handler, state) {
  React.render(
    <Handler {...rootProps} />,
    document.getElementById('react-app')
  );
});
