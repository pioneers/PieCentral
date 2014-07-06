'use strict'

# Declare app level module which depends on filters, and services
App = angular.module('daemon', [
  'ngCookies'
  'ngResource'
  'ngRoute'
  'daemon.controllers'
  'daemon.directives'
  'daemon.filters'
  'daemon.services'
  'partials'
])

App.config([
  '$routeProvider'
  '$locationProvider'

($routeProvider, $locationProvider, config) ->

  $routeProvider

    .when('/todo', {templateUrl: '/partials/todo.html'})
    .when('/view1', {templateUrl: '/partials/partial1.html'})
    .when('/view2', {templateUrl: '/partials/partial2.html'})

    # Catch all
    .otherwise({redirectTo: '/todo'})

  # Without server side support html5 must be disabled.
  $locationProvider.html5Mode(false)
])
