window.angularGet = (name) -> angular.element(document).injector().get(name)

angular.module('debug', ['daemon.gamepad'])

.controller('DebugInfoCtrl', [
  '$scope'
  'gamepads'
  ($scope, gamepads) ->
    hasSerialport = ->
      try
        serialport = requireNode('serialport')
        if serialport?
          return "Yes"
      catch error
        return "No.\n" + String(error)

    $scope.debugProperties = [
        name: 'Platform'
        value: process.platform
      ,
        name: 'Architecture'
        value: process.arch
      ,
        name: 'Has serialport?'
        value: hasSerialport()
      ]

    $scope.gamepad = gamepads.gamepad
])
