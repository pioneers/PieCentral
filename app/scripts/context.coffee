angular.module('daemon.context', ['ngRoute', 'ng-context-menu', 'daemon.radio'])

.controller('WidgetContextCtrl', [
  '$scope'
  'radio'
  ($scope, radio) ->
    
    toggleRadio = ->
      if radio.initialized()
        radio.close()
      else
        radio.init()

    $scope.menuItems = [
      class: 'dropdown-header'
      label: 'Add Widget'
    ,
      label: 'Distance Sensor'
    ,
      label: 'Light Sensor'
    ,
      class: 'divider'
    ,
      class: 'dropdown-header'
      label: 'Radio'
    ,
      label: 'Toggle Radio'
      ngClick: toggleRadio
    ]

  ])