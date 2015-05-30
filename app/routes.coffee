React = require('react')
Router = require('react-router')
DefaultRoute = Router.DefaultRoute
Route = Router.Route

App = require('./components/App')
Edit = require('./components/Edit')
Debug = require('./components/Debug')
Dashboard = require('./components/Dashboard')

module.exports = routes =
  <Route handler={App} path='/'>
    <DefaultRoute handler={Dashboard}/>
    <Route handler={Edit} name='edit'/>
    <Route handler={Debug} name='debug'/>
    <Route handler={Dashboard} name='dashboard'/>
  </Route>
