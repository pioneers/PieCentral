'use strict'

### Graphing Widgets ###

angular.module('daemon.widget', ['daemon.robot', 'nvd3'])

.controller('widgetCtrl', [
  '$scope'
  '$interval'
  'widgetFactory'
  'robot'

($scope, $interval, widgetFactory, robot) ->
  $scope.widgets = []

  $scope.addWidget = ->
    $scope.widgets.push((new widgetFactory(robot.peripherals()[0], 'linechart')))

  $interval(
    ->
      for widget in $scope.widgets
        widget.update()
    , 100
    )
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
    _data = [{
      "key": periph.name
      "values": []
    }]

    return {
      data: _data
      update: -> _data[0].values = periph.historyPairs()
      url: defaultURL.replace('type', String(type))
      position: null
      options: {
        chart: {
          type: 'lineChart'
          height: 180
          margin : {
            top: 20
            right: 20
            bottom: 40
            left: 50
          }
          x: (d) -> d[0]
          y: (d) -> d[1]
          useInteractiveGuideline: true
          transitionDuration: 1
          yAxis: {
            tickFormat: (d) -> d3.format('.01f')(d)
          }
          yDomain: [0, 1]
        }
      }
    }
)
