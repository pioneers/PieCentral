import { connect } from 'react-redux';
import NameEdit from './NameEdit';
import { peripheralRename } from '../actions/PeripheralActions';

const mapStateToProps = state => ({
  peripherals: state.peripherals,
});

const mapDispatchToProps = dispatch => ({
  onRename: (uid, name) => {
    dispatch(peripheralRename(uid, name));
  },
});

const NameEditContainer = connect(mapStateToProps, mapDispatchToProps)(NameEdit);

export default NameEditContainer;
