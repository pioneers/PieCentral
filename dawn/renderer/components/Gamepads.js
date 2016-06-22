import React from 'react';
import { connect } from 'react-redux';
import { Panel, ListGroup } from 'react-bootstrap';
import _ from 'lodash';
import GamepadItem from './GamepadItem';

class GamepadsComponent extends React.Component {
  renderInterior() {
    // if there are any gamepads
    if (_.some(this.props.gamepads, (gamepad) => gamepad !== undefined)) {
      // Currently there is a bug on windows where navigator.getGamepads()
      // returns a second, 'ghost' gamepad even when only one is connected.
      // The filter on 'mapping' filters out the ghost gamepad.
      return _.map(_.filter(
        this.props.gamepads, { mapping: 'standard' }), (gamepad, index) => (
          <GamepadItem key={index} index={index} gamepad={gamepad} />
        )
      );
    }
    return (
      <p>
        There don't seem to be any gamepads connected.
        Connect a gamepad and press any button on it.
      </p>
    );
  }

  render() {
    return (
      <Panel
        header="Gamepads"
        bsStyle="primary"
        id="gamepads-panel"
        defaultExpanded
      >
        <ListGroup fill style={{ marginBottom: '5px' }}>
          {this.renderInterior()}
        </ListGroup>
      </Panel>
    );
  }
}

GamepadsComponent.propTypes = {
  gamepads: React.PropTypes.object,
};

const mapStateToProps = (state) => ({
  gamepads: state.gamepads.gamepads,
});

const Gamepads = connect(mapStateToProps)(GamepadsComponent);

export default Gamepads;
