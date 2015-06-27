React = require('react')
RouteHandler = require('react-router').RouteHandler
DebugHero = require('./DebugHero')
DebugGamepads = require('./DebugGamepads')

module.exports = Debug = React.createClass
  displayName: 'Debug'
  render: ->
    <div className="container">
      <DebugHero />
      <DebugGamepads />
    </div>
