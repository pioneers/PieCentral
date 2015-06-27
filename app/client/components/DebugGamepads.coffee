React = require('react')
Panel = require('react-bootstrap').Panel
_ = require('lodash')
GamepadStore = require('../stores/GamepadStore')
DebugGamepadItem = require('./DebugGamepadItem')

module.exports = DebugGamepads = React.createClass
  displayName: 'DebugGamepads'

  getInitialState: ->
    gamepads: GamepadStore.getGamepads()

  onChange: ->
    gamepads = GamepadStore.getGamepads()
    this.setState
      gamepads: gamepads

  componentDidMount: ->
    GamepadStore.on('change', this.onChange)
  componentWillUnmount: ->
    GamepadStore.removeListener('change', this.onChange)
  renderInterior: ->
    # if there are any gamepads
    if _.any(this.state.gamepads, (gamepad) -> gamepad?)
      return _.map this.state.gamepads, (gamepad, index) ->
        <DebugGamepadItem key={index} index={index} gamepad={gamepad} />
    else # assume they haven't connected any
      <p>
        There don't seem to be any gamepads connected.
        Connect a gamepad and press any button on it.
      </p>
  render: ->
    <Panel header={<h3>Gamepads</h3>} bsStyle='primary'>
      {this.renderInterior()}
    </Panel>
