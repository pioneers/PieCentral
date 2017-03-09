import { connect } from 'react-redux';
import PeripheralList from './PeripheralList';

const mapStateToProps = state => ({
  peripherals: state.peripherals,
});

const PeripheralListContainer = connect(mapStateToProps)(PeripheralList);

export default PeripheralListContainer;
