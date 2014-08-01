'use strict'

### Graphing Widgets ###

angular.module('daemon.widget', [])

.controller('widgetCtrl', [
  '$scope'
  'widgetFactory'

($scope, widgetFactory) ->
  $scope.widgets = widgetFactory.getWidgets()

  $scope.addWidget = ->
    widgetFactory.addWidget()

  $scope.getWidgets = (index) ->
    widgetFactory.getWidgets(index)

])

.directive('draggable',
->
  restrict: 'A',
  link: (scope, elm, attr) ->
    widget = scope.getWidgets(scope.$index)
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
  widgets = []

  addWidget: ->
    widgets.push {position: null}
  getWidgets: (index) ->
    if index
      widgets[index]
    else
      widgets
)
