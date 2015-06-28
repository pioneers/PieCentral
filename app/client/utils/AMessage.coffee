# Format data to be sent to griff
class AMessage
  constructor : (msg_type, content) ->
    @msg_type = msg_type
    @content = content

  toJSON : ->
    msg = {}
    msg.header = msg_type: @msg_type
    msg.content = @content
    return msg

module.exports = AMessage
