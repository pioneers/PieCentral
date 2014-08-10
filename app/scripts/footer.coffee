angular.module("daemon.footer", ["daemon.radio"])
  .controller "FooterCtrl", [
    "$scope"
    "radio"
    ($scope, radio) ->
      $scope.radio = radio
      $scope.radioAddr = '0013A20040A580C4'
      $scope.portPath = '/dev/ttyUSB0'
  ]