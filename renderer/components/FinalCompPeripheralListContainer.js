import { connect } from 'react-redux';
import FinalCompPeripheralList from './FinalCompPeripheralList';

const mapStateToProps = (state) => ({
  peripherals: state.peripherals,
});

const FinalCompPeripheralListContainer = connect(mapStateToProps)(FinalCompPeripheralList);

export default FinalCompPeripheralListContainer;
