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
    <Grid fluid={true}>
      <Row>
        <Col sm={8}>
          <MotorTester />
        </Col>
        <Col sm={4}>
          <PeripheralList>
            <Peripheral peripheralType='MOTOR_SCALAR' id='testmotor' value={50}/>
            <Peripheral peripheralType='SENSOR_BOOLEAN' />
          </PeripheralList>
          <MotorList />
        </Col>
      </Row>
    </Grid>
