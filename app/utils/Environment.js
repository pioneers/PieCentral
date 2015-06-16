var isNode = (typeof process !== "undefined" && typeof require !== "undefined");
var hasWindow = typeof window !== "undefined" && window !== null

module.exports = {
  isNode: isNode && !hasWindow
}
