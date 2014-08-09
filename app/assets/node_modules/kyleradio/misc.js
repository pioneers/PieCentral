//
// This module provides small helper functions.
//

// Combine two objects by (over)writing every field in b into a.
var obj_or = function obj_or ( a, b ) {
  var k;
  for ( k in b ) {
    a[k] = b[k];
    }
  return a;
  };

var print = function print () {
  var a;

  if ( typeof console === 'undefined' ) {
    for ( a in arguments ) {
      dump ( JSON.stringify ( arguments[a], null, '  ' ) );
      }
    }
  else {
    for ( a in arguments ) {
      var util = require ( 'util' );
      //console.log ( JSON.stringify ( arguments[a], null, '  ' ) );
      console.log ( util.inspect ( arguments[a], { colors: true, depth: null } ) );
      }
    }
  };

// This exists because there is no built in assert in JavaScript.
function assert ( thing, reason ) {
  if ( ! thing ) {
    throw 'ERROR: ' + reason;
    }
  }

function shallow_copy ( obj ) {
  if ( ! obj || typeof obj !== 'object' ) {
    return obj;
    }
  var copy = obj.constructor ( );
  for ( var a in obj ) {
    if ( obj.hasOwnProperty ( a ) ) {
      copy [ a ] = obj [ a ];
      }
    }
  return copy;
  }


function determine_environment ( ) {
  // TODO(rqou): This is a stupid-ass hack to detect XULrunner. Try to find a
  // better way.

  if ( typeof process === 'object' ) {
    return 'node';
    }

  if ( typeof window === 'undefined' ) {
    return 'xulrunner';
    }

  return 'browser';
  }

var environment = determine_environment ( );

function to_filename ( path ) {
  if ( environment === 'node' ) {
    return path;
    }
  else if ( environment === 'xulrunner' ) {
    var url = require ( 'sdk/url' );
    if ( url.isValidURI ( path ) ) {
      // url.isValidURI returns true for Windows paths.
      // Hopefully, this will be fixed at some point.
      // For the time being, we catch the exception from trying to convert that 
      // path to a filename.
      try {
        return url.toFilename ( path );
        }
      catch ( _ ) {
        return path;
        }
      }
    else {
      return path;
      }
    }
  else {
    throw 'to_filename not supported on environment ' + environment;
    }
  }

exports.environment = environment;
exports.obj_or = obj_or;
exports.print = print;
exports.assert = assert;
exports.shallow_copy = shallow_copy;
exports.to_filename = to_filename;
