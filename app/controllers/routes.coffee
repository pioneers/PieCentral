express = require('express')
router = express.Router()
React = require('react')
Router = require('react-router')
clientRoutes = require('../client/routes')

# Delegate most things to the appropriate namespace
router.use '/api', require('./api/api')

# Delegate all other routes to react-router
router.use (req, res, next) ->

  res.render 'home',
    markup: "<div>Loading...</div>"
    rootProps: "{}"

  return

  rootProps = {}

  router = Router.create location: req.url, routes: clientRoutes
  router.run (Handler, state) ->
    if state.routes.length == 0
      return next() # we've gotten to an illegal path
    markup = React.renderToString(<Handler {...rootProps}/>)
    res.render 'home',
      markup: markup
      rootProps: JSON.stringify rootProps

module.exports = router
