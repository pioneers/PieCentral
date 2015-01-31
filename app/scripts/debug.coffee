window.angularGet = (name) -> angular.element(document).injector().get(name)

angular.module('debug', [])

.controller('DebugInfoCtrl', [
  '$scope'
  ($scope) ->
    $scope.debugProperties = [
        name: 'Platform'
        value: process.platform
      ,
        name: 'Architecture'
        value: process.arch
      ]
])
