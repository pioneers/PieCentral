angular.module('daemon.configure', [])
  .controller "ConfigureCtrl", [
    "$scope"
    "$interval"
    "$modalInstance"
    ($scope, $interval, $modalInstance) ->
      #0013A2004086336B
      storeR = DataStore.create('simple')

      $scope.cancelClick = () ->
        $modalInstance.close()

      $scope.saveClick = (form) ->
        if form.$valid
          $modalInstance.dismiss 'save'
        

  ]
