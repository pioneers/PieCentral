React = require('react')
RouteHandler = require('react-router').RouteHandler
Grid = require('react-bootstrap').Grid
Row = require('react-bootstrap').Row
Col = require('react-bootstrap').Col
MotorList = require('./MotorList')
PeripheralList = require('./PeripheralList')
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
            <PeripheralList>
              <Peripheral peripheralType='UNKNOWN_PERIPHERAL' id='idk' />
              <Peripheral peripheralType='MOTOR_SCALAR' id='testmotor' value={50}/>
              <Peripheral peripheralType='SENSOR_SCALAR' id='leftLineScan' value={42}/>
              <Peripheral peripheralType='SENSOR_SCALAR' id='rightLineScan' value={42}/>
            </PeripheralList>
            <MotorList />
          </Col>
        </Row>
      </Grid>
    )
