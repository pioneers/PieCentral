angular.module('edit', ['ui.ace', 'ansible'])
.controller 'EditCtrl', [
  'ansible'
  'AMessage'
  '$scope'
  (ansible, AMessage, $scope) ->

    # editor is initially undefined
    editor = undefined

    # Does several things, including defining the editor
    setup = (ed) ->
      editor = ed
      editor.setShowPrintMargin(false)
      loadState()
      editor.focus()

      editor.getSelection().on('changeCursor', saveStateDebounced)

    # Loads the saved state data.
    loadState = ->
      storage = DataStore.create 'simple'
      editor_state = storage.get 'editor_state'
      if editor_state?
        editor.setValue editor_state.value || DEFAULT_VALUE
        editor.gotoLine (editor_state.line || 0), (editor_state.column || 0)
      else
        editor.setValue "# what will you create?"
        editor.gotoLine 0, 0

    # Saves the state data.
    saveState = ->
      storage = DataStore.create 'simple'
      value = editor.getValue()
      position = editor.getCursorPosition()
      line = position.row + 1
      column = position.column
      editor_state = {
        value: value
        line: line
        column: column
      }
      storage.set('editor_state', editor_state)

    AUTOSAVE_DELAY = 100
    saveStateDebounced = _.debounce(saveState, AUTOSAVE_DELAY, false)

    # Quick fix to prevent setup from being fired twice in quick succession.
    # Eventually we should figure out what's causing it to be fired in quick
    # succession in the first place.
    setupDebounced = _.debounce(setup, 100, true)

    $scope.aceChanged = -> saveStateDebounced()
    $scope.aceLoaded = (args...) -> setupDebounced(args...)
    $scope.sendEditorData = ->
      value = editor.getValue()
      # send this to Ansible
      message = new AMessage('code_python', code: value)
      ansible.send(message)

]
