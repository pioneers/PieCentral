window.angularGet = (name) -> angular.element(document).injector().get(name)

angular.module('debug', ['ansible'])

.controller('DebugInfoCtrl', [
  '$scope'
  'ansible'
  'gamepadReporter'
  ($scope, ansible, gamepadReporter) ->
    $scope.debugProperties = [
        name: 'Platform'
        value: process.platform
      ,
        name: 'Architecture'
        value: process.arch
      ]

    $scope.validGamepad = ->
      return _.filter(navigator.getGamepads(), (x) -> x?)

    $scope.lastMessage = 'None'
    ansible.on('message', (msg) ->
      console.log('ansible received messages')
      $scope.lastMessage = msg
      $scope.$apply()
    )
])
