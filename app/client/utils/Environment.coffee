nodeLike = typeof process isnt 'undefined' and typeof require isnt 'undefined'
hasWindow = window?

module.exports =
  isNode: nodeLike
  isHeadless: nodeLike and not hasWindow
  isBrowser: hasWindow
