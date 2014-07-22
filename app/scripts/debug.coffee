window.angularGet = (name) -> angular.element(document).injector().get(name)

angular.module('debug', [])

.controller('DebugInfoCtrl', [
  '$scope'
  ($scope) ->
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
])
