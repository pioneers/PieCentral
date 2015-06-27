React = require('react')
Panel = require('react-bootstrap').Panel
Table = require('react-bootstrap').Table
_ = require('lodash')
numeral = require('numeral')

module.exports = DebugGamepadItem = React.createClass
  displayName: 'DebugGamepadItem'
  propTypes:
    gamepad: React.PropTypes.object
    index: React.PropTypes.number

  # Utility function to get the rounded (string) values on the gamepad.
  roundedValues: ->
    axes: _.map this.props.gamepad.axes, (axis) ->
      numeral(axis).format('0.00000')
    buttons: _.map this.props.gamepad.buttons, (button) ->
      numeral(button.value).format('0.00')

  renderHeader: ->
    <div>
      <h4 style={display: 'inline'}> Gamepad {this.props.index} </h4>
      <span style={float: 'right'}> {this.props.gamepad.id}</span>
    </div>

  render: ->
    if not this.props.gamepad?
      return <div/>
    <Panel header={this.renderHeader()}>
      <div>Timestamp: {this.props.gamepad.timestamp}</div>
      <div>Mapping: {this.props.gamepad.mapping}</div>
      <div>Axes: {String(this.roundedValues().axes)}</div>
      <div>Buttons: {String(this.roundedValues().buttons)}</div>
    </Panel>

