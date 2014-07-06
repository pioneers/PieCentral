'use strict'

### Directives ###

# register the module with Angular
angular.module('daemon.directives', [
  # require the 'daemon.service' module
  'daemon.services'
])

.directive('appVersion', [
  'version'

(version) ->

  (scope, elm, attrs) ->
    elm.text(version)
])
