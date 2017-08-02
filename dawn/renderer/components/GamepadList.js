import React from 'react';
import PropTypes from 'prop-types';
import { Panel, ListGroup } from 'react-bootstrap';
import { connect } from 'react-redux';

import _ from 'lodash';
import Gamepad from './Gamepad';

const GamepadListComponent = (props) => {
  let interior;
  if (_.some(props.gamepads, gamepad => gamepad !== undefined)) {
    interior = _.map(
      props.gamepads,
      (gamepad, index) => <Gamepad key={index} index={parseInt(index, 10)} gamepad={gamepad} />,
    );
  } else {
    interior = (
      <p className="panelText">
        There doesn&apos;t seem to be any gamepads connected.
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

GamepadListComponent.propTypes = {
  gamepads: PropTypes.object.isRequired,
};

const mapStateToProps = state => ({
  gamepads: state.gamepads.gamepads,
});

const GamepadList = connect(mapStateToProps)(GamepadListComponent);

export default GamepadList;
