React = require('react')
RouteHandler = require('react-router').RouteHandler

module.exports = Dashboard = React.createClass
  displayName: 'Dashboard'
  render: ->
    <div className="container">
      <p> This is a dashboard!!! </p>
    </div>
