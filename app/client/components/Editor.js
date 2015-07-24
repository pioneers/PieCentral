import React from 'react';
import AceEditor from 'react-ace';
import brace from 'brace';
import 'brace/mode/python';
import 'brace/theme/monokai';

var Editor = React.createClass({
  render() {
    return <AceEditor
      mode="python"
      theme="monokai"
      width="100%"
      name="CodeEditor"
    />;
  }
});

export default Editor;
