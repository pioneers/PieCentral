angular.module('daemon.configure', ['daemon.fieldcontrol', 'daemon.radio'])
  .controller "ConfigureCtrl", [
    "$scope"
    "$interval"
    "radio"
    "fieldcontrol"
    ($scope, $interval, radio, fieldcontrol) ->
      $scope.radio = radio
      $scope.fieldcontrol = fieldcontrol
      $scope.radioAddr = '0013A2004086336B'
      $scope.portPath = ''

      $scope.portPathList = []

      $scope.assignPortPath = (path) ->
        $scope.portPath = path

      $scope.updatePortPathList = ->
        serialPort = requireNode('serialport')
        if serialPort
          serialPort.list( (err, ports) ->
            $scope.portPathList = _.map(ports, (p) -> p.comName)
            $scope.$apply()
            )
      $scope.updatePortPathList()
      $interval($scope.updatePortPathList, 500)
  ]