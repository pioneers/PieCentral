React = require('react')
RouteHandler = require('react-router').RouteHandler

module.exports = Debug = React.createClass
  displayName: 'Debug'
  render: ->
    <div className="container">
      <p> This is debug! </p>
    </div>
