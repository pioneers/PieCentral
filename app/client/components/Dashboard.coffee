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
DebugGamepads = require('./DebugGamepads')
if Environment.isBrowser
  Editor = require('./Editor')
  RobotActions = require('../actions/RobotActions')

module.exports = Dashboard = React.createClass
  displayName: 'Dashboard'
  render: ->
    editor = 'Loading...'
    if Editor?
      editor = <Editor/>
    return (
      <Grid fluid>
        <Row>
          <Col smPush={8} sm={4}>
            <FinalCompPeripheralList/>
            <DebugGamepads/>
          </Col>
          <Col smPull={4} sm={8}>
            { editor }
          </Col>
        </Row>
      </Grid>
    )
