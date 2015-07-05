React = require('react')
RouteHandler = require('react-router').RouteHandler
Col = require('react-bootstrap').Col
MotorTester = require('./MotorTester')
MotorList = require('./MotorList')

module.exports = Dashboard = React.createClass
  displayName: 'Dashboard'
  render: ->
    <div className="container">
      <Col md={6}>
        <MotorTester />
      </Col>
      <Col md={6}>
        <MotorList />
      </Col>
    </div>
