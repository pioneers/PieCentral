# the websocket slave for fieldcontrol
angular.module('daemon.fieldcontrol', ['daemon.radio'])

.service('fieldcontrol', [
  'radio',
  (radio) ->
    fieldcontrol = {}
    l = undefined
    sub = undefined
    state =
      auton: true
      enabled: true

    updateState = (msg) ->
      newState =
        auton: msg.auton
        enabled: msg.enabled
      if state.auton != newState.auton \
      or state.enabled != newState.enabled
        # state has been updated
        state = newState
        if state.enabled
          if state.auton
            radio.setAutonomous()
          else
            radio.setTeleoperated()
        else
          radio.emergencyStop()

    fieldcontrol.init = (url = "ws://localhost:8000") ->
      l = new LCM(url)
      l.on_ready ->
        sub = l.subscribe "piemos0/cmd", "piemos_cmd", (msg) ->
          updateState(msg)
    fieldcontrol.close = ->
      l.unsubscribe(sub)

    return fieldcontrol
])
