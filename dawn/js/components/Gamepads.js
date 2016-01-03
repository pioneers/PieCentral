import React from 'react';
import { Panel, ListGroup } from 'react-bootstrap';
import _ from 'lodash';
import GamepadStore from '../stores/GamepadStore';
import GamepadItem from './GamepadItem';

export default React.createClass({
  displayName: 'Gamepads',
  getInitialState() {
    return { gamepads: GamepadStore.getGamepads() };
  },
  onChange() {
    let gamepads = GamepadStore.getGamepads();
    this.setState({ gamepads: gamepads });
  },
  componentDidMount() {
    GamepadStore.on('change', this.onChange);
  },
  componentWillUnmount() {
    GamepadStore.removeListener('change', this.onChange);
  },
  renderInterior() {
    // if there are any gamepads
    if (_.any(this.state.gamepads, (gamepad) => gamepad !== null)) {
      return _.map(this.state.gamepads, (gamepad, index) => {
        return (<GamepadItem key={index} index={index} gamepad={gamepad}/>);
      });
    } else {
      return (
        <p>
          There don't seem to be any gamepads connected.
          Connect a gamepad and press any button on it.
        </p>
      );
    }
  },
  render() {
    return (
      <Panel
        header="Gamepads"
        bsStyle="primary"
        id="gamepads-panel"
        defaultExpanded>
        <ListGroup fill style={{marginBottom: '5px'}}>
          {this.renderInterior()}
        </ListGroup>
      </Panel>
    );
  }
});
