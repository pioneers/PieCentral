import React from 'react';
import { connect } from 'react-redux';
import { Panel, ListGroup } from 'react-bootstrap';
import _ from 'lodash';
import GamepadItem from './GamepadItem';

let Gamepads = React.createClass({
  displayName: 'Gamepads',
  renderInterior() {
    // if there are any gamepads
    if (_.some(this.props.gamepads, (gamepad) => gamepad !== undefined)) {
      // Currently there is a bug on windows where navigator.getGamepads()
      // returns a second, 'ghost' gamepad even when only one is connected.
      // The filter on 'mapping' filters out the ghost gamepad.
      return _.map(_.filter(
        this.props.gamepads, {'mapping': 'standard'}), (gamepad, index) => {
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

const mapStateToProps = (state) => {
  return {
    gamepads: state.gamepads.gamepads
  };
};

Gamepads = connect(mapStateToProps)(Gamepads);

export default Gamepads;
