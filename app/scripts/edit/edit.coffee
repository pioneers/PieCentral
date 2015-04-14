DEFAULT_VALUE = '''
# what will you create?
'''

angular.module('edit', ['ui.ace'])
.controller 'EditCtrl', [
  '$scope'
  ($scope) ->

    promised = {}

    loadLocalSave = ->
      storage = DataStore.create 'simple'
      editor = promised.editor
      editor_state = storage.get 'student_code'
      if editor_state?
        editor.setValue editor_state.value || DEFAULT_VALUE
        editor.gotoLine (editor_state.line || 0), (editor_state.column || 0)
      else
        editor.setValue DEFAULT_VALUE
        editor.gotoLine 0, 0

    doLocalSave = ->
      storage = DataStore.create 'simple'
      editor = promised.editor
      value = editor.getValue()
      position = editor.getCursorPosition()
      line = position.row + 1
      column = position.column
      editor_state = {
        value: value
        line: line
        column: column
      }
      storage.set('student_code', editor_state)

    setupAce = ->

    aceChanged = ->
      doLocalSave()

    AUTOSAVE_DELAY = 100
    aceChangedDebounced = _.debounce(aceChanged, AUTOSAVE_DELAY, false)

    setup = (editor) ->
      promised.editor = editor
      editor.setShowPrintMargin(false)
      loadLocalSave()
      editor.focus()

      editor.getSelection().on('changeCursor', aceChangedDebounced)

    # Quick fix to prevent setup from being fired twice in quick succession.
    # Eventually we should figure out what's causing it to be fired in quick
    # succession in the first place.
    setupDebounced = _.debounce(setup, 100, true)

    $scope.aceChanged = -> aceChangedDebounced()
    $scope.aceLoaded = (args...) -> setupDebounced(args...)
    $scope.sendEditorData = ->
      editor = promised.editor
      value = editor.getValue()

]
