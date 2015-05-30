React = require('react')
Router = require('react-router')
RouteHandler = Router.RouteHandler

Nav = require('./Nav')

module.exports = Daemon = React.createClass
  displayName: 'Daemon'

  render: ->
    <div>
      <Nav {...this.props}/>
      <RouteHandler {...this.props}/>
    </div>
