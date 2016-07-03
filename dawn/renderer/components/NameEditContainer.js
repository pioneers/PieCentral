import { connect } from 'react-redux';
import NameEdit from './NameEdit';

const mapStateToProps = (state) => ({
  peripherals: state.peripherals,
});

const NameEditContainer = connect(mapStateToProps)(NameEdit);

export default NameEditContainer;
