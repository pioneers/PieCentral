React = require('react')
ReactBootstrap = require('react-bootstrap')
Navbar = ReactBootstrap.Navbar
Nav = ReactBootstrap.Nav
ReactRouterBootstrap = require('react-router-bootstrap')
NavItemLink = ReactRouterBootstrap.NavItemLink

module.exports = React.createClass
  displayName: 'DNav'
  render: ->
    <Navbar brand="Daemon" toggleNavKey={0} fixedTop>
      <Nav right eventKey={0}>
        <NavItemLink eventKey={1} to='dashboard'>Dashboard</NavItemLink>
        <NavItemLink eventKey={2} to='edit'>Edit</NavItemLink>
        <NavItemLink eventKey={3} to='debug'>Debug</NavItemLink>
      </Nav>
    </Navbar>
