import React from 'react';
import { connect } from 'react-redux';
import {
  Alignment,
  Button,
  ButtonGroup,
  Navbar,
  Menu,
  MenuItem,
  Popover,
  PopoverInteractionKind,
  Tooltip,
} from '@blueprintjs/core';
import { IconNames } from '@blueprintjs/icons';
import { VERSION, ConnectionStatus } from '../constants/Constants';

import { ConsoleMenu } from './Console';
import Preferences from './Preferences';
import Status from './Status';

const DebugMenu = () => (
  <Menu>
    <MenuItem text="Lint" icon={IconNames.CODE} />
    <MenuItem text="Restart Runtime" icon={IconNames.RESET} />
    <MenuItem text="Motor check" icon={IconNames.COG} />
    <MenuItem text="Statistics" icon={IconNames.TIMELINE_LINE_CHART} />
  </Menu>
);

class Toolbar extends React.Component {
  render() {
    return (
      <Navbar>
        <Navbar.Group>
          <Navbar.Heading>
            Dawn v
            { VERSION }
          </Navbar.Heading>
          <Navbar.Divider />
          <ButtonGroup>
            <Button icon={IconNames.UPLOAD} disabled={this.props.disconnected}>
              Upload
            </Button>
            <Button icon={IconNames.DOWNLOAD} disabled={this.props.disconnected}>
              Download
            </Button>
          </ButtonGroup>
          <Navbar.Divider />
          <ButtonGroup>
            <Button icon={IconNames.PLAY} disabled={this.props.disconnected}>Start</Button>
            <Button icon={IconNames.STOP} disabled={this.props.disconnected}>Stop</Button>
            <Button icon={IconNames.FLAME} disabled={this.props.disconnected}>Emergency</Button>
          </ButtonGroup>
          <Navbar.Divider />
          <ButtonGroup>
            <Popover
                content={<ConsoleMenu />}
                interactionKind={PopoverInteractionKind.HOVER}
                hoverOpenDelay={0}
                hoverCloseDelay={200}>
              <Button icon={IconNames.CONSOLE}>Console</Button>
            </Popover>
            <Popover
                content={<DebugMenu />}
                interactionKind={PopoverInteractionKind.HOVER}
                hoverOpenDelay={0}
                hoverCloseDelay={200}>
              <Button icon={IconNames.DASHBOARD}>Debug</Button>
            </Popover>
            <Preferences />
          </ButtonGroup>
        </Navbar.Group>
        <Navbar.Group align={Alignment.RIGHT}>
          <Navbar.Heading>
            <Status />
          </Navbar.Heading>
        </Navbar.Group>
      </Navbar>
    );
  }
}

export default connect(state => ({
  disconnected: state.connection.status === ConnectionStatus.DISCONNECTED,
}))(Toolbar);
