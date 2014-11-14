'use strict'

### Graphing Widgets ###

angular.module('daemon.widget', ['daemon.context', 'daemon.robot', 'nvd3', 'daemon.sensors'])

.controller('WidgetCtrl', [
  '$scope'
  'Widget'
  'Linechart'
  'robot'
  'SensorGraphData'
  '$rootScope'

  ($scope, Widget, Linechart, robot, SensorGraphData, $rootScope) ->
    $scope.widgets = []
    $scope.activeWidget = {}

    $scope.setRecentWidget = (widget) ->
      $scope.activeWidget = widget

    $scope.addWidget = (type, properties) ->
      switch type
        when 'linechart'
          widget = new Linechart(properties)
        else
          widget = new Widget('default')
      $scope.widgets.push widget
      widget.update()

    $scope.convertToDataObject = (data, key) ->
      return [{values:data, key: key}]

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

    $rootScope.$on 'widget_update', () ->
      DataStore.create('simple').set 'widgets', $scope.widgets

    saved_data = DataStore.create('simple').get 'widgets'
    if saved_data? and saved_data.length > 0
      for widget in saved_data
        if widget.type == 'linechart'
          properties = { did: widget.did, position: widget.position}
          $scope.addWidget 'linechart', properties


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
        start: null
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
        start: null
        stop: (event, ui) ->
          widget.position = ui.position
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

  (type) ->
    return {
      id: guid()
      data: null
      url: defaultURL.replace('type', String(type))
      position: null
      type: type
      update: () -> return null
      options: {}
    }
  )

.factory('Linechart', ['Widget', 'SensorGraphData', '$rootScope'
  (Widget, SensorGraphData, $rootScope) ->
    (properties) ->
      linechart = new Widget('linechart')
      linechart.did = properties.did
      linechart.position = properties.position
      linechart.update = () ->
        linechart.data = [{values: SensorGraphData.GetGraphData linechart.did}]
        $rootScope.$emit 'widget_update'
      linechart.options.chart = {
        type: 'lineChart'
        height: 180
        margin : {
          top: 20
          right: 20
          bottom: 40
          left: 50
        }
        x: (d) -> d.x
        y: (d) -> d.y
        useInteractiveGuideline: true
        transitionDuration: 1
        yAxis: {
          tickFormat: (d) -> d3.format('.01f')(d)
        }
        #yDomain: [0, 1]
        tooltips: false
        interpolate: 'basis'
      }
      return linechart
    ]
)
