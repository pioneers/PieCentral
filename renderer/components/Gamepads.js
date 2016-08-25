import React from 'react';
import { Panel, ListGroup } from 'react-bootstrap';
import _ from 'lodash';
import GamepadItem from './GamepadItem';

const Gamepads = (props) => {
  let interior;
  // if there are any gamepads
  if (_.some(props.gamepads, (gamepad) => gamepad !== undefined)) {
    interior = _.map(
      props.gamepads,
      (gamepad, index) => <GamepadItem key={index} index={index} gamepad={gamepad} />
    );
  } else {
    interior = (
      <p>
        There don't seem to be any gamepads connected.
        Connect a gamepad and press any button on it.
      </p>
    );
  }
  return (
    <Panel
      header="Gamepads"
      bsStyle="primary"
      id="gamepads-panel"
      defaultExpanded
    >
      <ListGroup fill style={{ marginBottom: '5px' }}>
        {interior}
      </ListGroup>
    </Panel>
  );
};

Gamepads.propTypes = {
  gamepads: React.PropTypes.object,
};

export default Gamepads;
