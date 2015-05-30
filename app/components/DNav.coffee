React = require('react')
ReactBootstrap = require('react-bootstrap')
Navbar = ReactBootstrap.Navbar
Nav = ReactBootstrap.Nav
NavItem = ReactBootstrap.NavItem

module.exports = React.createClass
  displayName: 'DNav'
  render: ->
    <Navbar brand="Daemon" toggleNavKey={0}>
      <Nav right eventKey={0}>
        <NavItem eventKey={1} href='/dashboard'>Dashboard</NavItem>
        <NavItem eventKey={2} href='/edit'>Edit</NavItem>
        <NavItem eventKey={3} href='/debug'>Debug</NavItem>
      </Nav>
    </Navbar>
