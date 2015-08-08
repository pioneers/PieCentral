React = require('react')
RouteHandler = require('react-router').RouteHandler
Environment = require('../utils/Environment')
if Environment.isBrowser
  Editor = require('./Editor')

module.exports = Edit = React.createClass
  displayName: 'Edit'
  render: ->
    content = 'Loading...'
    if Editor?
      content = <Editor/>
    <div className="container">
      { content }
    </div>

