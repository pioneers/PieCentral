angular.module('daemon.configure', ['daemon.radio'])
  .controller "ConfigureCtrl", [
    "$scope"
    "$interval"
    "radio"
    ($scope, $interval, radio) ->
      #0013A2004086336B
      storeR = DataStore.create('simple')
      $scope.radio = radio
      $scope.radioAddr = storeR.get('xbeeAddr')
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