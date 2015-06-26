express = require('express')
router = express.Router()
jsx = require('node-jsx').install()
React = require('react')
Router = require('react-router')
routes = require('../routes')

# Delegate most things to the appropriate namespace
router.use '/api', require('./api/api')

# Delegate all other routes to react-router
router.use (req, res, next) ->

  rootProps = {}

  router = Router.create location: req.url, routes: routes
  router.run (Handler, state) ->
    if state.routes.length == 0
      return next() # we've gotten to an illegal path
    markup = React.renderToString(<Handler {...rootProps}/>)
    res.render 'home',
      markup: markup
      rootProps: JSON.stringify rootProps

module.exports = router
