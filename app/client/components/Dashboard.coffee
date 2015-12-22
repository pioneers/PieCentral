React = require('react')
RouteHandler = require('react-router').RouteHandler
Grid = require('react-bootstrap').Grid
Row = require('react-bootstrap').Row
Col = require('react-bootstrap').Col
MotorList = require('./MotorList')
PeripheralList = require('./PeripheralList')
FinalCompPeripheralList = require('./FinalCompPeripheralList')
Peripheral = require('./Peripheral')
Environment = require('../utils/Environment')
Gamepads = require('./Gamepads')
ConsoleOutput = require('./ConsoleOutput')
if Environment.isBrowser
  Editor = require('./Editor')
  RobotActions = require('../actions/RobotActions')

module.exports = Dashboard = React.createClass
  displayName: 'Dashboard'

  render: ->
    editor = 'Loading...'
    if Editor?
      editor = <Editor {...this.props} />
    return (
      <Grid fluid>
        <Row>
          <Col smPush={8} sm={4}>
            <FinalCompPeripheralList {...this.props} />
            <Gamepads {...this.props} />
          </Col>
          <Col smPull={4} sm={8}>
            { editor }
          </Col>
        </Row>
        <Row>
          <Col sm={12}>
            <ConsoleOutput {...this.props} />
          </Col>
        </Row>
      </Grid>
    )
