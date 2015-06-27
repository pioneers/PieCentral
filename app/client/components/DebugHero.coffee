React = require('react')
Jumbotron = require('react-bootstrap').Jumbotron
Label = require('react-bootstrap').Label
Constants = require('../constants/Constants')

module.exports = DebugHero = React.createClass
  displayName: 'DebugHero'
  render: ->
    <Jumbotron>
      <h1>Daemon</h1>
      <h2>It's the future.</h2>
      <p>Version <Label bsStyle='primary'>{Constants.VERSION}</Label><p>
    </Jumbotron>
