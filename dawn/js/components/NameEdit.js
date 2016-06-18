import React from 'react';
import { RIEInput } from 'riek';
import Ansible from '../utils/Ansible';
import AlertActions from '../actions/AlertActions';
import { connect } from 'react-redux';
import _ from 'lodash';

let NameEdit = React.createClass({
  propTypes: {
    name: React.PropTypes.string,
    id: React.PropTypes.string
  },
  shouldComponentUpdate(nextProps) {
    // By default, the component is constantly being updated which makes
    // the RIEInput unusable. This prevents unnecessary updating.
    return nextProps.name !== this.props.name;
  },
  dataChange(data) {
    Ansible.sendMessage('custom_names', {
      id: this.props.id,
      name: data.name
    });
  },
  componentDidMount() {
    // MAJOR HAXORS! The default RIEInput component trims spaces from the
    // end of strings before passing to validation. But we need
    // to check for those spaces. So here I am modifying the RIEInput
    // component's textChanged function to not trim before validation.
    this.nameEdit.textChanged = (event)=>{
      this.nameEdit.doValidations(event.target.value);
    };
  },
  validatePeripheralName(name) {
    let re = new RegExp("^[A-Za-z][A-Za-z0-9]+$");
    let isValid = re.test(name);
    let allCurrentPeripherals = _.toArray(this.props.peripherals);
    let isDuplicate = _.some(allCurrentPeripherals, (peripheral) => {
      return peripheral.get("name") === name && peripheral.get("id") !== this.props.id;
    });
    return isValid && !isDuplicate;
  },
  render() {
    return (
      <div>
      	<RIEInput
      	  ref={(ref) => this.nameEdit = ref}
      	  className="static"
      	  classEditing="editing"
      	  classInvalid="invalid"
      	  validate={this.validatePeripheralName}
      	  value={this.props.name}
      	  change={this.dataChange}
      	  propName="name" />
      </div>
    );
  }
});

const mapStateToProps = (state) => {
  return {
    peripherals: state.peripherals
  };
};

NameEdit = connect(mapStateToProps)(NameEdit);

export default NameEdit;
