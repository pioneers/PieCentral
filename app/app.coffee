'use strict'

# Declare app level module which depends on filters, and services
App = angular.module('daemon', [
  'ngCookies'
  'ngResource'
  'ngRoute'
  'ngSanitize'
  'partials'
  'ui.bootstrap'
  'daemon.nav'
  'daemon.edit'
  'daemon.robot'
  'daemon.configure'
  'daemon.menubar'
  'daemon.sensors'
  'debug'
])

App.config([
  '$routeProvider'
  '$locationProvider'

($routeProvider, $locationProvider, config) ->

  $routeProvider

    .when('/dashboard', {templateUrl: '/partials/dashboard.html'})
    .when('/edit', {templateUrl: '/partials/edit.html'})
    .when('/debug', {templateUrl: '/partials/debug.html'})
    .when('/configure', {templateUrl: '/partials/configure.html'})

    # Catch all
    .otherwise({redirectTo: '/dashboard'})

  # Without server side support html5 must be disabled.
  $locationProvider.html5Mode(false)
])
