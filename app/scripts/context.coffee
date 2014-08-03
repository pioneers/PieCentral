angular.module('daemon.context', ['daemon.radio'])

.controller('CanvasContextCtrl', [
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
      label: 'Visualize'
    ,
      label: 'Mock Peripheral'
      ngClick: $scope.addWidget
    ,
      class: 'divider'
    ,
      class: 'dropdown-header'
      label: 'Radio'
    ,
      label: 'Toggle Radio'
      ngClick: toggleRadio
    ,
      class: 'divider'
    ,
      label: 'Close All Widgets'
      ngClick: $scope.removeAllWidgets
    ]
  ])

.directive('canvascontext', [
  ->
    return {
      restrict: 'E'
      templateUrl: '/partials/canvascontext.html'
      link: (scope, elem, attrs) ->
        $('#widgetContainer').contextmenu({
          before: (e, element, target) ->
            if $(e.target).is('#widgetContainer')
              return true
            return false
        })
    }
  ])

.directive('widgetcontext', [
  ->
    return {
      restrict: 'E'
      templateUrl: '/partials/widgetcontext.html'
      link: (scope, elem, attrs) ->
        $(elem[0])
    }
  ])

.directive('widgetcontextcaller', [
  ->
    return {
      restrict: 'A'
      link: (scope, elem, attrs) ->
        $(elem[0]).contextmenu(
            target: '#widget-context-menu'
            before: (e, context) ->
              scope.setRecentWidget(scope.widget)
          )
    }
  ])