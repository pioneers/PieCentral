'use strict'

### Graphing Widgets ###

angular.module('daemon.widget', ['daemon.context', 'daemon.robot', 'nvd3'])

.controller('WidgetCtrl', [
  '$scope'
  'Widget'
  'robot'

($scope, Widget, robot) ->
  $scope.widgets = []
  $scope.activeWidget = {}

  $scope.setRecentWidget = (widget) ->
    $scope.activeWidget = widget

  $scope.addWidget = (properties = {id: -1}) ->
    $scope.widgets.push new Widget(robot.peripheral(properties), 'linechart')
    $scope.widgets[$scope.widgets.length-1].update()

  $scope.removeWidget = (widget) ->
    id = widget.id
    for i in [0...$scope.widgets.length]
      if $scope.widgets[i].id == id
        $scope.widgets.splice i, 1
        return

  $scope.removeRecentWidget = ->
    $scope.removeWidget($scope.activeWidget)

  $scope.removeAllWidgets = ->
    $scope.widgets = []
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
      start: (event, ui) ->
        for series in widget.data
          series.values = series.values.slice()
      stop: (event, ui) ->
        widget.position = ui.position
        widget.update()
      })
)

.directive('resizable',
->
  restrict: 'A',
  link: (scope, elm, attr) ->
    widget = scope.widgets[scope.$index]
    jQelm = $(elm[0])
    $(jQelm).resizable({
      start: (event, ui) ->
        for series in widget.data
          series.values = series.values.slice()
      stop: (event, ui) ->
        widget.update()
    })
)

.factory('Widget',
->
  defaultURL = '/partials/type.html'
  # guid generator code
  guid = ->
    s4 = ->
      return Math.floor(1 + Math.random() * 0x10000).toString(16).substring(1)
    return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
             s4() + '-' + s4() + s4() + s4()

  (periph, type) ->
    _data = [{
      "key": periph.name
      "values": []
      "peripheral": periph
    }]

    return {
      id: guid()
      data: _data
      update: -> _.each(_data, (element, index, list) ->
        element.values =  element.peripheral.historyPairs())
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
          x: (d) -> d.time - periph.lastUpdate().time
          y: (d) -> d.value
          useInteractiveGuideline: true
          transitionDuration: 1
          yAxis: {
            tickFormat: (d) -> d3.format('.01f')(d)
          }
          yDomain: [0, 1]
          tooltips: false
          interpolate: 'basis'
        }
      }
    }
)
