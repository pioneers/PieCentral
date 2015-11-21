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
    values = this.roundedValues()
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
                  <table>
                      <tbody class="table">
                          <tr>
                              <td>Button 0: {values.buttons[0]}</td>
                          </tr>
                          <tr>
                              <td>Button 1: {values.buttons[1]}</td>
                          </tr>
                          <tr>
                              <td>Button 2: {values.buttons[2]}</td>
                          </tr>
                          <tr>
                              <td>Button 3: {values.buttons[3]}</td>
                          </tr>
                          <tr>
                              <td>Button 4: {values.buttons[4]}</td>
                          </tr>
                          <tr>
                              <td>Button 5: {values.buttons[5]}</td>
                          </tr>
                          <tr>
                              <td>Button 6: {values.buttons[6]}</td>
                          </tr>
                          <tr>
                              <td>Button 7: {values.buttons[7]}</td>
                          </tr>
                          <tr>
                              <td>Button 8: {values.buttons[8]}</td>
                          </tr>
                          <tr>
                              <td>Button 9: {values.buttons[9]}</td>
                          </tr>
                          <tr>
                              <td>Button 10: {values.buttons[10]}</td>
                          </tr>
                          <tr>
                              <td>Button 11: {values.buttons[11]}</td>
                          </tr>
                          <tr>
                              <td>Button 12: {values.buttons[12]}</td>
                          </tr>
                          <tr>
                              <td>Button 13: {values.buttons[13]}</td>
                          </tr>
                          <tr>
                              <td>Button 14: {values.buttons[14]}</td>
                          </tr>
                          <tr>
                              <td>Button 15: {values.buttons[15]}</td>
                          </tr>
                          <tr>
                              <td>Button 16: {values.buttons[16]}</td>
                          </tr>
                           <tr>
                              <td>Axis 0: {values.axes[0]}</td>
                          </tr>
                          <tr>
                              <td>Axis 1: {values.axes[1]}</td>
                          </tr>
                          <tr>
                              <td>Axis 2: {values.axes[2]}</td>
                          </tr>
                          <tr>
                              <td>Axis 3: {values.axes[3]}</td>
                          </tr>
                      </tbody>
                  </table>
              </Col>
            </Row>
          </Grid>
        </Modal.Body>
      </Modal>
    </ListGroupItem>



