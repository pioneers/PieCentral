'use strict'

### Graphing Widgets ###

angular.module('daemon.widget', ['nvd3ChartDirectives', 'daemon.robot'])

.controller('widgetCtrl', [
  '$scope'
  'widgetFactory'
  'robot'

($scope, widgetFactory, robot) ->
  $scope.widgets = []

  $scope.addWidget = ->
    $scope.widgets.push((new widgetFactory(robot.peripherals()[0], 'linechart')))

])

.directive('draggable',
->
  restrict: 'A',
  link: (scope, elm, attr) ->
    widget = scope.widgets[scope.$index]
    jQelm = $(elm[0])
    if widget.position
      $(jQelm).css('left', widget.position.left)
      $(jQelm).css('top', widget.position.top)
    $(jQelm).draggable({
      containment: 'parent'
      stop: (event, ui) ->
        widget.position = ui.position
      })
)

.directive('resizable',
->
  restrict: 'A',
  link: (scope, elm, attr) ->
    jQelm = $(elm[0])
    $(jQelm).resizable()
)

.factory('widgetFactory',
->
  defaultURL = '/partials/type.html'

  (periph, type) ->
    data:
      [
        "key": periph.name
        "values": periph.historyPairs()
      ]
    url: defaultURL.replace('type', String(type))
    position: null
)
