import { connect } from 'react-redux';
import Gamepads from './Gamepads';

const mapStateToProps = (state) => ({
  gamepads: state.gamepads.gamepads,
});

const GamepadsContainer = connect(mapStateToProps)(Gamepads);

export default GamepadsContainer;
