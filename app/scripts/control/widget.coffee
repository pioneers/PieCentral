'use strict'

### Graphing Widgets ###

angular.module('daemon.widget', ['daemon.context', 'daemon.robot', 'nvd3'])

.controller('WidgetCtrl', [
  '$scope'
  'Widget'
  'robot'
  '$rootScope'

  ($scope, Widget, robot, $rootScope) ->
    $scope.widgets = []
    $scope.activeWidget = {}

    $scope.setRecentWidget = (widget) ->
      $scope.activeWidget = widget

    $scope.addWidget = (type, properties) ->
      switch type
        when "linechart"
          #nothing here yet
          console.log "asdf"
        else
          widget = new Widget('default')
      $scope.widgets.push widget
      widget.update()

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
        $scope.addWidget widget

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
