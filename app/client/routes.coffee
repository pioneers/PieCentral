React = require('react')
Router = require('react-router')
DefaultRoute = Router.DefaultRoute
Route = Router.Route

App = require('./components/App')
Dashboard = require('./components/Dashboard')

module.exports = routes =
  <Route handler={App} path='/'>
    <DefaultRoute handler={Dashboard}/>
    <Route handler={Dashboard} name='dashboard'/>
  </Route>
