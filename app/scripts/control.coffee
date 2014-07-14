'use strict'

angular.module('daemon.control', [])

.controller('TodoCtrl', [
  '$scope'

($scope) ->

  $scope.todos = [
    text: "Prepare to build cool things. "
    done: true
  ,
    text: "Build cool things. "
    done: false
  ,
    text: "Change the world. "
    done: false
  ]

  $scope.addTodo = ->
    $scope.todos.push
      text: $scope.todoText
      done: false

    $scope.todoText = ""

  $scope.remaining = ->
    count = 0
    angular.forEach $scope.todos, (todo) ->
      count += (if todo.done then 0 else 1)

    count

  $scope.archive = ->
    oldTodos = $scope.todos
    $scope.todos = []
    angular.forEach oldTodos, (todo) ->
      $scope.todos.push todo  unless todo.done

])

