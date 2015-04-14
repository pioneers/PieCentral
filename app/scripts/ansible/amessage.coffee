angular.module('ansible')

# An Ansible Message
#
# Require this factory and use it. 'new' is required.
# Automatically serializes into Ansible message format
#
# @example How to use
# am = AMessage('message type', {key1: 'val1', key2: 'val2'})
#
.factory 'AMessage', ->

  class AMessage
    constructor : (msg_type, content) ->
      @msg_type = msg_type
      @content = content

    toJSON : ->
      msg = {}
      msg.header = msg_type: @msg_type
      msg.content = @content
      return msg

  return AMessage
