'use strict'

### Graphing Widgets ###

angular.module('daemon.widget', ['daemon.context', 'daemon.robot', 'nvd3'])

.controller('widgetCtrl', [
  '$scope'
  '$interval'
  'widgetFactory'
  'robot'

($scope, $interval, widgetFactory, robot) ->
  $scope.widgets = []
  $scope.mostRecentWidget = {}

  $scope.setRecentWidget = (widget) ->
    $scope.mostRecentWidget = widget

  $scope.addWidget = (peripheralFilter = {id: -1}) ->
    $scope.widgets.push new widgetFactory(robot.peripheral(peripheralFilter), 'linechart')

  $scope.removeWidget = (widget) ->
    id = widget.id
    for i in [0...$scope.widgets.length]
      if $scope.widgets[i].id == id
        $scope.widgets.splice i, 1
        return

  $scope.removeRecentWidget = ->
    $scope.removeWidget($scope.mostRecentWidget)

  $scope.removeAllWidgets = ->
    $scope.widgets = []

  # update widgets
  $interval(
    ->
      widget.update() for widget in $scope.widgets when widget.render
    , 300
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
      start: (event, ui) ->
        widget.render = false
        for series in widget.data
          series.values = series.values.slice()
      stop: (event, ui) ->
        widget.position = ui.position
        widget.render = true
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
        widget.render = false
        for series in widget.data
          series.values = series.values.slice()
      stop: (event, ui) ->
        widget.render = true
    })
)

.factory('widgetFactory',
->
  defaultURL = '/partials/type.html'
  # guid generator code
  guid = ->
    s4 = ->
      return Math.floor((1 + Math.random() * 0x10000)).toString(16).substring(1)
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
      render: true
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
