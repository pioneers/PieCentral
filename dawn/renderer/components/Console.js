import React from 'react';
import { connect } from 'react-redux';
import { Collapse, Menu, MenuItem, Pre } from '@blueprintjs/core';
import { IconNames } from '@blueprintjs/icons';

import { toggle, copy, clear } from '../actions/console';

const Console = connect(state => state.console)((props) =>
  <Collapse isOpen={props.isOpen}>
      <Pre className="console-area">
        {props.records.map((record, index) => (
          <span key={index}>
            {record.event}
            <br />
          </span>
        ))}
      </Pre>
  </Collapse>
);

const ConsoleMenu = connect(state => state.console, { toggle, copy, clear })((props) => {
  let icon, label;
  if (props.isOpen) {
    icon = IconNames.MENU_CLOSED;
    label = 'Close';
  } else {
    icon = IconNames.MENU_OPEN;
    label = 'Open';
  }
  return (
    <Menu>
      <MenuItem text={label} icon={icon} onClick={props.toggle} />
      <MenuItem text="Copy" icon={IconNames.DUPLICATE}></MenuItem>
      <MenuItem text="Clear" icon={IconNames.CLEAN} onClick={props.clear} />
    </Menu>
  );
});

export { Console, ConsoleMenu };
