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
  render: ->
    <Panel header={<h3>Gamepads</h3>} bsStyle='primary'>
      {
        _.map this.state.gamepads, (gamepad, index) ->
          <DebugGamepadItem key={index} index={index} gamepad={gamepad} />
      }
    </Panel>
