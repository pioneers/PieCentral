angular.module('daemon.context', [])

.controller('CanvasContextCtrl', [
  '$scope'
  ($scope) ->

    $scope.menuItems = [
      class: 'dropdown-header'
      label: 'Visualize'
    ,
      class: 'divider'
    ]
  ])

.directive('canvascontext', [
  ->
    return {
      restrict: 'E'
      templateUrl: '/partials/canvascontext.html'
      link: (scope, elem, attrs) ->
        $('#widget-container').contextmenu({
          before: (e, element, target) ->
            if $(e.target).is('#widget-container')
              return true
            return false
        })
    }
  ])
