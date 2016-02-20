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
    if (_.some(this.state.gamepads, (gamepad) => gamepad !== undefined)) {
      // Currently there is a bug on windows where navigator.getGamepads()
      // returns a second, 'ghost' gamepad even when only one is connected.
      // The filter on 'mapping' filters out the ghost gamepad.
      return _.map(_.filter(
        this.state.gamepads, {'mapping': 'standard'}), (gamepad, index) => {
          return (<GamepadItem key={index} index={index} gamepad={gamepad}/>);
        }
      );
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
