React = require('react')
Router = require('react-router')
RouteHandler = Router.RouteHandler

DNav = require('./DNav')

module.exports = Dawn = React.createClass
  displayName: 'Dawn'

  render: ->
    <div>
      <DNav {...this.props}/>
      <div style={height: '60px', marginBottom: '21px'}/>
      <RouteHandler {...this.props}/>
    </div>
