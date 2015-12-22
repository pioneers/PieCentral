React = require('react')
Router = require('react-router')

DNav = require('./DNav')
Dashboard = require('./Dashboard')

module.exports = Dawn = React.createClass
  displayName: 'Dawn'

  render: ->
    <div>
      <DNav {...this.props}/>
      <div style={height: '60px', marginBottom: '21px'}/>
      {this.props.children}
    </div>
