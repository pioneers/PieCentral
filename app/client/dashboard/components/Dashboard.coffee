React = require('react')
RouteHandler = require('react-router').RouteHandler
Grid = require('react-bootstrap').Grid
Row = require('react-bootstrap').Row
Col = require('react-bootstrap').Col
MotorTester = require('./MotorTester')
MotorList = require('./MotorList')
PeripheralList = require('./PeripheralList')
Peripheral = require('./Peripheral')

module.exports = Dashboard = React.createClass
  displayName: 'Dashboard'
  render: ->
    <Grid fluid>
      <Row>
        <Col sm={8}>
          <MotorTester />
        </Col>
        <Col sm={4}>
          <PeripheralList>
            <Peripheral peripheralType='MOTOR_SCALAR' id='testmotor' value={50}/>
            <Peripheral peripheralType='SENSOR_BOOLEAN' id='testsensor' value={1}/>
            <Peripheral peripheralType='SENSOR_BOOLEAN' id='testoff' value={0}/>
            <Peripheral peripheralType='SENSOR_SCALAR' id='scalar' value={42}/>
          </PeripheralList>
          <MotorList />
        </Col>
      </Row>
    </Grid>
