import React from 'react';
import { connect } from 'react-redux';
import { Collapse, Menu, MenuItem, Pre } from '@blueprintjs/core';
import { IconNames } from '@blueprintjs/icons';

class Console extends React.Component {
  render() {
    return (
      <Collapse isOpen={this.props.isOpen}>
          <Pre className="console-area">
            {this.props.lines.map((line, index) => (
              <span key={index}>
                {line}
                <br />
              </span>
            ))}
          </Pre>
      </Collapse>
    );
  }
}

export default connect(
  state => state.console,
)(Console);
