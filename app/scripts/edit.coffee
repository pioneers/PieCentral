DEFAULT_VALUE = '''
function addto(x)
  -- Return a new function that adds x to the argument
  return function(y)
    --[[ When we refer to the variable x, which is outside of the current
         scope and whose lifetime would be shorter than that of this anonymous
         function, Lua creates a closure.]]
    return x + y
  end
end
fourplus = addto(4)
print(fourplus(3))  -- Prints 7
 
--This can also be achieved by calling the function in the following way:
print(addto(4)(3))
--[[ This is because we are calling the returned function from `addto(4)' with the argument `3' directly.
     This also helps to reduce data cost and up performance if being called iteratively.
]]
'''

angular.module("daemon.edit", ["ui.ace"])
.controller "EditCtrl", [
  "$scope"
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
      #value = localStorage.edit__autosave_value || DEFAULT_VALUE
      #line = localStorage.edit__autosave_line || 0
      #column = localStorage.edit__autosave_column || 0
      
    doLocalSave = ->
      storage = DataStore.create 'simple'
      editor = promised.editor
      value = editor.getValue()
      position = editor.getCursorPosition()
      line = position.row + 1
      column = position.column
      editor_state = {}
      editor_state.value = value
      editor_state.line = line
      editor_state.column = column
      storage.set('student_code', editor_state)
      #localStorage.edit__autosave_value = value
      #localStorage.edit__autosave_line = line
      #localStorage.edit__autosave_column = column
      console.log 'Autosaved'

    setupAce = ->
      editor = promised.editor
      editor.setShowPrintMargin(false)
      loadLocalSave()
      editor.focus()


    aceChanged = ->
      doLocalSave()

    AUTOSAVE_DELAY = 100
    aceChangedDebounced = _.debounce(aceChanged, AUTOSAVE_DELAY, false)

    aceLoaded = (editor) ->
      promised.editor = editor
      setupAce()
      console.log 'Ace editor loaded!'

      editor.getSelection().on('changeCursor', aceChangedDebounced)

    # Quick fix to prevent aceLoaded from being fired twice in quick succession.
    # Eventually we should figure out what's causing it to be fired in quick
    # succession in the first place.
    aceLoadedDebounced = _.debounce(aceLoaded, 100, true)

    $scope.aceChanged = -> aceChangedDebounced()
    $scope.aceLoaded = (args...) -> aceLoadedDebounced(args...)
    $scope.sendEditorData = ->
      editor = promised.editor
      value = editor.getValue()
      # radio.sendCode(value)

]
