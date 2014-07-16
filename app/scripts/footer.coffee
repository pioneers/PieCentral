angular.module("daemon.footer", ["daemon.radio"])
  .controller "FooterCtrl", [
    "$scope"
    "radio"
    ($scope, radio) ->
      $scope.radio = radio
  ]