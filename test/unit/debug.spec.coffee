describe 'DebugInfoCtrl', ->

  # preload all the things
  $controller = undefined
  beforeEach ->
    module 'debug'
    inject (_$controller_) -> $controller = _$controller_

  describe 'debug properties', ->
    it 'defines scope debugProperties', ->
      $scope = {}
      controller = $controller('DebugInfoCtrl', $scope: $scope)
      expect($scope.debugProperties).not.toBeUndefined()
      expect($scope.debugProperties.length).toBeGreaterThan(0)