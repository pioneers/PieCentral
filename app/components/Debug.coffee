React = require('react')
RouteHandler = require('react-router').RouteHandler
DebugGamepads = require('./DebugGamepads')

module.exports = Debug = React.createClass
  displayName: 'Debug'
  render: ->
    <div className="container">
      <DebugGamepads />
    </div>
