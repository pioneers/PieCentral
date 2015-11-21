React = require('react')
Panel = require('react-bootstrap').Panel
Modal = require('react-bootstrap').Modal
Button = require('react-bootstrap').Button
ListGroupItem = require('react-bootstrap').ListGroupItem
Table = require('react-bootstrap').Table
Grid = require('react-bootstrap').Grid
Row = require('react-bootstrap').Row
Col = require('react-bootstrap').Col
_ = require('lodash')
numeral = require('numeral')

module.exports = GamepadItem = React.createClass
  displayName: 'GamepadItem'
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
    </div>

  getInitialState: ->
    showModal: false

  closeModal: ->
    this.setState({ showModal: false })

  openModal: ->
    this.setState({ showModal: true })

  render: ->
    if not this.props.gamepad?
      return <div/>
    <ListGroupItem>
      <div style={{overflow: 'auto', width: '100%'}}>
        <span style={{float: 'left'}}>{this.renderHeader()}</span>
        <Button bsSize="small" onClick={this.openModal} style={{float: 'right'}}>Details</Button>
      </div>
      <Modal show={this.state.showModal} onHide={this.closeModal} bsSize="large">
        <Modal.Header closeButton>
          <Modal.Title>{this.renderHeader()}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Grid fluid={true}>
            <Row>
              <Col lg={9} md={12}>
                <img src={'/assets/gamepad.png'} style={{width: '100%'}}/>
              </Col>
              <Col lg={3} md={12}>
                  <p>Axes: {String(this.roundedValues().axes)}</p>
                  <p>Buttons: {String(this.roundedValues().buttons)}</p>
              </Col>
            </Row>
          </Grid>
        </Modal.Body>
      </Modal>
    </ListGroupItem>



