angular.module("daemon.footer", ["daemon.radio"])
  .controller "FooterCtrl", [
    "$scope"
    "$interval"
    "radio"
    ($scope, $interval, radio) ->
      $scope.radio = radio
      $scope.radioAddr = '0013A20040A580C4'
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
