
// This file was (hastily) ported from lua-ubjson.
// The code structure there will make probably make more sense.
// Multiple return values there have been manually transformed into arrays
// here, and generally make the code harder to understand.
// There are also a few lingering Lua-isms, like keeping track of stack depth
// for error handling, excessive use of nil / null, variable names suggesting
// string and buffers are the same thing, and ambiguity about what's an array
// and what's an object.
// The comments also have not been updated. Comments that look like they've
// been mangled by a regex probably have.

// Global dependencies here.

var buffer_module = require('buffer');

var abs = Math.abs;
var floor = Math.floor;
var dumpint = function (val, size, endian) {
  var b = buffer_module.Buffer(size);

  if (endian !== 'b') {
    throw 'Expected only big endian encoding.';
  }

  if (size === 1) {
    endian = '';
  } else {
    endian = 'BE';
  }

  if (val > pow2(8 * size)) {
    // twos-complement encode too-large values.
    val = val - pow2(8 * size);
  }

  b['writeInt' + (8 * size) + endian].apply(b, [val, 0]);
  return b;
};

var dumpfloat = function (val, type, endian) {
  var b;

  if (endian !== 'b') {
    throw 'Expected only big endian encoding.';
  } else {
    endian = 'BE';
  }

  if (type === 'f') {
    b = buffer_module.Buffer(4);
    b['writeFloat' + endian].apply(b, [val, 0]);
  } else if (type === 'd') {
    b = buffer_module.Buffer(8);
    b['writeDouble' + endian].apply(b, [val, 0]);
  } else {
    throw 'Unexpected float type ' + type + '.';
  }
  return b;
};

var undumpint = function(buf, offset, size, endian) {
  if (endian !== 'b') {
    throw 'Expected only big endian encoding.';
  }

  if (size === 1) {
    endian = '';
  } else {
    endian = 'BE';
  }
  return buf['readInt' + (8 * size) + endian].apply(buf, [offset]);
};

var undumpfloat = function(buf, offset, type, endian) {
  if (endian !== 'b') {
    throw 'Expected only big endian encoding.';
  } else {
    endian = 'BE';
  }

  if (type === 'f') {
    return buf['readFloat' + endian].apply(buff, [offset]);
  } else if (type === 'd') {
    return buf['readDouble' + endian].apply(buff, [offset]);
  } else {
    throw 'Unexpected float type ' + type + '.';
  }
};

var toBuffer = function (str) {
  return buffer_module.Buffer(str);
};

var type = function (val) {
  return typeof val;
};
var error = function (msg) {
  throw "js-ubjson: " + msg;
};

var insert = function(array, val) {
  array.push(buffer_module.Buffer(val));
};

var bufStr = function(buf, start, end) {
  return buf.slice(start, end + 1).toString();
};

// Calculate 2 ^ v
var pow2 = function(v) {
  var out = 1;
  for (var i = 0; i < v; i++) {
    // Use floats, since this may end up very large.
    out = out * 2.0;
  }
  return out;
};

// Mapping from maximum value -> ubjson tag
var int_maxes = [
  pow2( 7),
  pow2(15),
  pow2(31),
  pow2(63),
];

var int_tags = [
  'i',
  'I',
  'l',
  'L',
];

// ubjson tag -> size in bytes
var int_tag_size = {
  U : 1,
  i : 1,
  I : 2,
  l : 4,
  L : 8,
};

// Use doubles to serialize Lua numbers.
var use_double = false;

// Get the smallest tag and size to hold a value.
function int_tag(val) {
  if ( val >= 0 && val < 256 ) {
    return ['U', 1];
  }
  var last_key = 'i';
  var size = 1;
  // Calculate the absolute value.
  if ( val < 0 ) {
    val = -val;
    // Because twos-complement can hold slightly larger negatives than
    // positives.
    if ( val !== 0 ) {
      val = val - 1;
    }
  }
  for (var idx in int_maxes) {
    var max = int_maxes[idx];
    if ( val > max ) {
      return [last_key, size];
    } else {
      last_key = int_tags[idx];
      size = size * 2;
    }
  }
  return [last_key, size / 2];
}

// If val can be represented by a fixed size value type, return the tag for
// that type, otherwise return the Lua type string.
function val_tag(val) {
  var t = type(val);
  if ( t === 'number' ) {
    t = int_tag(val)[0];
  } else if ( t === 'boolean' ) {
    if ( t ) {
      return 'T';
    } else {
      return 'F';
    }
  } else if ( t === 'null' ) {
    return 'Z';
  }
  return t;
}

// Pre-declare encode_inner
var encode_inner;

// Determines whether an table should become an array or a table.
// Also determines length, and whether the optimized container optimization can
// be applied.
// returns [use_obj, length, max_index, shared_tag, write_val]
// where
// use_obj is true iff the table should become a ubjson object (not an array).
// length is the number of entries in the array or table.
// max_index is the largest integer index.
// shared_tag is a ubjson type tag if ( the optimized container format can be
//     applied, otherwise is the string 'mixed'
// write_val is a function which writes a value for the object or array.
// write_val has the same type as encode_inner
//   (value, buffer, memo, depth) -> ()
//   where value is the value to be serialized
//         buffer is a table of strings which will be concatenated together to
//             produce the output
//         memo is a table mapping currently entered tables to true
//         depth is the recursion depth from the user's call
function array_helper(val) {
  // TODO(kzentner): Handle integer tags more intelligently.
  // Currently, this function only handles integers well when every integer is
  // expected to have the same tag. In theory, this could produce an array for
  // any integer type tag, but in practice probably will almost always only
  // produce 'U'.
  // Basically, this function expects val_tag to return the same tag for every
  // value if the fixed-type container optimization can be applied. This is
  // definitely not true. For example, [0, -1, 2] produces the tags ['U', 'i',
  // 'U'], but all the entries can be represented by one signed byte.
  // 
  var t = null;
  var length = 0;
  var max = 0;

  for (var k in val) {
    var v = val[k];
    if ( k > max ) {
      max = k;
    }
    if ( t === null ) {
      t = val_tag(v);
    }
    if ( t !== val_tag(v) ) {
      t = 'mixed';
    }
    length = length + 1;
  }

  var write_val = encode_inner;

  if ( t !== null && t.length === 1 ) {
    var size = int_tag_size[t];
    if ( size ) {
      write_val = function(val, buffer, memo) {
        insert(buffer, dumpint(val, size, 'b'));
      };
    } else if ( t === 'f' ) {
      write_val = function(val, buffer, memo) {
        insert(buffer, dumpfloat(val, 'f', 'b'));
      };
    } else if ( t === 'd' ) {
      write_val = function(val, buffer, memo) {
        insert(buffer, dumpfloat(val, 'd', 'b'));
      };
    } else {
      // Tag should be 'T', 'F', 'Z'
      write_val = function(val, buffer, memo) {
      };
    }
  }

  // TODO(kzentner): Handle array-likes like Uint8Array's, etc. better.
  // Note that isArray(new Uint8Array) == false
  return [!Array.isArray(val), length, max, t, write_val];
}

function encode_int(val, buffer) {
  var ts = int_tag(val);
  var tag = ts[0];
  var size = ts[1];
  insert(buffer, tag);
  insert(buffer, dumpint(val, size, 'b'));

  // TODO(kzentner): Huge int support?
}

function encode_inner(val, buffer, memo, depth) {
  var k;
  // if val in memo. Some things, Javascript makes really weird.
  if ( ~memo.indexOf(val) ) {
    error('Cannot serialize circular data structure.', depth);
  }
  if ( depth === undefined ) {
    error('Depth missing.');
  }

  var t = type(val);
  if ( t === 'number' ) {
    if ( floor(val) === val ) {
      encode_int(val, buffer);
    } else {
      if ( use_double ) {
        insert(buffer, 'D');
        insert(buffer, dumpfloat(val, 'd', 'b'));
      } else {
        insert(buffer, 'd');
        insert(buffer, dumpfloat(val, 'f', 'b'));
      }
    }
  } else if ( t === 'null' || t === 'undefined' ) {
    insert(buffer, 'Z');
  } else if ( t === 'boolean' ) {
    if ( val ) {
      insert(buffer, 'T');
    } else {
      insert(buffer, 'F');
    }
  } else if ( t === 'string' ) {
    insert(buffer, 'S');
    encode_int(val.length, buffer);
    insert(buffer, val);
  } else if ( t === 'object' ) {
    memo.push(val);
    var ulmtw = array_helper(val);
    var use_obj = ulmtw[0];
    var length = ulmtw[1];
    var max = ulmtw[2];
    var tag = ulmtw[3];
    var write_val = ulmtw[4];
    if ( use_obj ) {
      insert(buffer, '{');
    } else {
      insert(buffer, '[');
    }

    if ( tag !== null && tag.length === 1 ) {
      insert(buffer, '$');
      insert(buffer, tag);
    }

    insert(buffer, '#');
    encode_int(length, buffer);

    if ( use_obj ) {
      for (k in val) {
        var v = val[k];
        var str = k + '';
        encode_int(str.length, buffer);
        insert(buffer, str);
        write_val(v, buffer, memo, depth + 1);
      }
    } else {
      for (k = 0; k <= max; k++ ) {
        write_val(val[k], buffer, memo, depth + 1);
      }
    }
    // Remove val from memo.
    memo.splice(memo.indexOf(val), 1);
  }
}

function encode(value, state) {
  var buffer = [];
  var memo = [];
  var k;
  encode_inner(value, buffer, memo, 3);
  var total_length = 0;
  for (k in buffer) {
    total_length += buffer[k].length;
  }
  var out = buffer_module.Buffer(total_length);
  var current_offset = 0;
  for (k in buffer) {
    var b = buffer[k];
    b.copy(out, current_offset, 0, b.length);
    current_offset += b.length;
  }
  return out;
}

function decode_int(str, offset, depth, error_context) {
  var c = bufStr(str, offset, offset);
  var int_size = int_tag_size[c];
  if ( int_size === undefined ) {
    error(error_context + ' length did not have an integer tag.', depth);
  }
  var i = undumpint(str, offset + 1, int_size, 'b');
  if ( c === 'U' && i < 0 ) {
    // Undo twos-complement
    i = 256 + i;
  }
  return [i, offset + 1 + int_size];
}

// Returns function with signature
// (str, offset, depth) -> val, new_offset, skip
// where str is the input string
//       offset is the index into str to start reading at
//       depth is the recursion depth from the user's call
//       val is the read value
//       new_offset is the offset after the read element
//       skip is whether the object should be recognized
//           (used to implement noop)
function get_read_func(tag) {
  var int_size = int_tag_size[tag];
  if ( tag === 'C' ) {
    int_size = 1;
  }
  if ( int_size !== undefined ) {
    return function(str, offset, depth) {
      return [undumpint(str, offset, int_size, 'b'), offset + int_size];
    };
  } else if ( tag === 'd' ) {
    return function(str, offset, depth) {
      return [undumpfloat(str, offset, 'f', 'b'), offset + 4];
    };
  } else if ( tag === 'D' ) {
    return function(str, offset, depth) {
      return [undumpfloat(str, offset, 'd', 'b'), offset + 8];
    };
  } else if ( tag === 'T' ) {
    return function(str, offset, depth) {
      return [true, offset];
    };
  } else if ( tag === 'F' ) {
    return function(str, offset, depth) {
      return [false, offset];
    };
  } else if ( tag === 'Z' ) {
    return function(str, offset, depth) {
      return [null, offset];
    };
  } else if ( tag === 'N' ) {
    return function(str, offset, depth) {
      return [null, offset, true];
    };
  } else {
    return null;
  }
}

// Decodes a string. Does ! read the type tag, so that it can be used to
// decode ubjson object keys.
function decode_str(str, offset, depth) {
  var ls = decode_int(str, offset, depth + 1, 'String at offset ' + offset);
  var str_length = ls[0];
  var str_start = ls[1];

  // Since bufStr is inclusive at of the end, -1 is needed.
  return [bufStr(str, str_start, str_start + str_length - 1), str_start + str_length];
}

// Recursive function used to decode object.
// (str, offset, depth) -> (val, new_offset, skip)
// where str is the input string
//       offset is the index into str to start reading at
//       depth is the recursion depth from the user's call
//       val is the read value
//       new_offset is the offset after the read element
//       skip is whether the object should be recognized
//           (used to implement noop)
function decode_inner(str, offset, depth) {
  if ( depth === null ) {
    error('Depth missing');
  }

  var c = bufStr(str, offset, offset);
  var int_size = int_tag_size[c];
  if ( int_size !== undefined ) {
    return [undumpint(str, offset + 1, int_size, 'b'), offset + 1 + int_size];
  } else if ( c === 'C' ) {
    return [undumpint(str, offset + 1, 1, 'b'), offset + 2];
  } else if ( c === 'S' || c === 'H' ) {
    // TODO(kzentner): How to handle huge numbers?
    return [decode_str(str, offset + 1, depth + 1)];
  } else if ( c === 'T' ) {
    return [true, offset + 1];
  } else if ( c === 'F' ) {
    return [false, offset + 1];
  } else if ( c === 'Z' ) {
    return [null, offset + 1];
  } else if ( c === 'N' ) {
    return [null, offset + 1, true];
  } else if ( c === '[' || c === '{' ) {
    var start_offset = offset + 1;
    var tag = bufStr(str, start_offset, start_offset);
    var length = null;
    var out;
    var read_val = decode_inner;
    if ( tag === '$' ) {
      start_offset = start_offset + 1;
      var t = bufStr(str, start_offset, start_offset);
      start_offset = start_offset + 1;
      tag = bufStr(str, start_offset, start_offset);
      read_val = get_read_func(t);
      if ( read_val === null ) {
        if ( c === '[' ) {
          error('Type tag for non value type in array at offset ' + offset,
              depth);
        } else {
          error('Type tag for non value type in object at offset ' + offset,
                depth);
        }
      }
    }
    // TODO(kzentner): Do not construct the error message every time.
    if ( tag === '#' ) {
      var msg;
      if ( c === '[' ) {
        msg = 'Array';
      } else {
        msg = 'Object';
      }
      msg = msg + ' length at offset ' + offset;
      var ls = decode_int(str, start_offset + 1, depth + 1, msg);
      length = ls[0];
      start_offset = ls[1];
    } else {
      start_offset = start_offset - 1;
    }

    var elt_offset = start_offset;
    var key, val, skip;
    var ke;
    var ves;
    var i;
    if ( c === '[' ) {
      out = [];
      if ( length !== null ) {
        for (i = 0; i < length; i++) {
          ves = read_val(str, elt_offset, depth + 1);
          val = ves[0];
          elt_offset = ves[1];
          skip = ves[2];
          if ( ! skip ) {
            out.push(val);
          }
        }
      } else {
        while ( bufStr(str, elt_offset, elt_offset) !== ']' ) {
          ves = read_val(str, elt_offset, depth + 1);
          val = ves[0];
          elt_offset = ves[1];
          skip = ves[2];
          if ( ! skip ) {
            out.push(val);
          }
        }
      }
    } else {
      out = {};
      if ( length !== null ) {
        for (i = 0; i < length; i++) {
          ke = decode_str(str, elt_offset, depth + 1);
          key = ke[0];
          elt_offset = ke[1];
          ves = read_val(str, elt_offset, depth + 1);
          val = ves[0];
          elt_offset = ves[1];
          skip = ves[2];
          if ( ! skip ) {
            out[key] = val;
          }
        }
      } else {
        while ( bufStr(str, elt_offset, elt_offset) !== '}' ) {
          ke = decode_str(str, elt_offset, depth + 1);
          key = ke[0];
          elt_offset = ke[1];
          ves = read_val(str, elt_offset, depth + 1);
          val = ves[0];
          elt_offset = ves[1];
          skip = ves[2];
          if ( ! skip ) {
            out[key] = val;
          }
        }
      }
    }
    return [out, elt_offset];
  } else {
    error('Unrecognized type tag ' + c + ' at offset ' + offset + '.', depth);
  }
}

// Get decoded value and the offset after it in the buffer.
function decode_offset(str, offset) {
  if (offset === undefined) {
    offset = 0;
  }
  return decode_inner(str, offset, 1);
}

// Just get the decoded value.
function decode(str, offset) {
  return decode_offset(str, offset)[0];
}

var ubjson = {
  version : 'js-ubjson 0.1',
  encode : encode,
  decode : decode,
  decode_offset: decode_offset
};

module.exports = ubjson;
