React = require('react')
RouteHandler = require('react-router').RouteHandler
Grid = require('react-bootstrap').Grid
Row = require('react-bootstrap').Row
Col = require('react-bootstrap').Col
MotorTester = require('./MotorList/MotorTester')
MotorList = require('./MotorList')

module.exports = Dashboard = React.createClass
  displayName: 'Dashboard'
  render: ->
    <div className="container-fluid">
      <Grid>
        <Row>
          <Col sm={6}>
            <MotorTester />
          </Col>
          <Col sm={6}>
            <MotorList />
          </Col>
        </Row>
      </Grid>
    </div>
