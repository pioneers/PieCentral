React = require('react')
RouteHandler = require('react-router').RouteHandler
Grid = require('react-bootstrap').Grid
Row = require('react-bootstrap').Row
Col = require('react-bootstrap').Col
MotorList = require('./MotorList')
PeripheralList = require('./PeripheralList')
FinalCompPeripheralList = require('./FinalCompPeripheralList')
Peripheral = require('./Peripheral')
Controls = require('./Controls')
Environment = require('../../utils/Environment')
if Environment.isBrowser
  RobotActions = require('../actions/RobotActions')

module.exports = Dashboard = React.createClass
  displayName: 'Dashboard'
  render: ->
    return (
      <Grid fluid>
        <Row>
          <Col sm={8}>
            <Controls />
          </Col>
          <Col sm={4}>
            <FinalCompPeripheralList/>
          </Col>
        </Row>
      </Grid>
    )
