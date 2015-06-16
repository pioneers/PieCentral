React = require('react')
Panel = require('react-bootstrap').Panel
_ = require('lodash')
GamepadStore = require('../stores/GamepadStore')

DebugGamepadItem = React.createClass
  render: ->
    <div>{this.props.gamepad.axes[0]}</div>

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
  renderGamepadItems: ->
    _.map this.state.gamepads, (gamepad, index) ->
      if gamepad? and gamepad.axes?
        <DebugGamepadItem key={index} gamepad={gamepad} />
      else
        <div key={index}> No gamepad in this slot </div>
  render: ->
    <Panel header='Gamepads'>
      {this.renderGamepadItems()}
    </Panel>
