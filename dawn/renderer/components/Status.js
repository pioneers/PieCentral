import React from 'react';
import { connect } from 'react-redux';
import {
  Intent,
  Navbar,
  Tag,
  Tooltip,
} from '@blueprintjs/core';
import { IconNames } from '@blueprintjs/icons';

import { ConnectionStatus } from '../constants/Constants';

class Status extends React.Component {
  render() {
    let address = 'team42.local';
    let status = 'Unknown', icon = IconNames.HELP, intent;
    switch (this.props.status) {
      case ConnectionStatus.HEALTHY:
        status = 'Healthy';
        icon = IconNames.TICK_CIRCLE;
        intent = Intent.SUCCESS;
        break;
      case ConnectionStatus.WARNING:
        status = 'Warning';
        icon = IconNames.WARNING_SIGN;
        intent = Intent.WARNING;
        break;
      // case ConnectionStatus.ERROR:
      //   status = 'Error';
      //   icon = IconNames.ERROR;
      //   intent = Intent.DANGER;
      //   break;
      case ConnectionStatus.DISCONNECTED:
        status = 'Disconnected';
        icon = IconNames.SIGNAL_SEARCH;
        break;
    }
    return (
      <Tooltip content="(No information)">
        <Tag icon={icon} intent={intent} large>
          {status} {this.props.status !== ConnectionStatus.DISCONNECTED && <span>
            (<code>{address}</code>)
          </span>}
        </Tag>
      </Tooltip>
    );
  }
}

export default connect(state => state.connection)(Status);
