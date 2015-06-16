React = require('react')
Panel = require('react-bootstrap').Panel
_ = require('lodash')

module.exports = DebugGamepadItem = React.createClass
  displayName: 'DebugGamepadItem'
  propTypes:
    gamepad: React.PropTypes.object
    index: React.PropTypes.number

  # Utility function to get the rounded values on the gamepad.
  roundedValues: ->
    axes: _.map this.props.gamepad.axes, (axis) -> Math.round(axis * 100) / 100
    buttons: _.map this.props.gamepad.buttons, (button) -> Math.round(button.value * 100) / 100
  render: ->
    if not this.props.gamepad?
      return <div/>
    <Panel header={<h4> Gamepad {this.props.index} </h4>}>
      <div>Axes: {String(this.roundedValues().axes)}</div>
      <div>Buttons: {String(this.roundedValues().buttons)}</div>
    </Panel>

