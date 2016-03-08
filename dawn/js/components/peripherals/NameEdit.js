import React from 'react';
import {RIEInput} from 'riek';
import Ansible from '../../utils/Ansible';
import AlertActions from '../../actions/AlertActions';
import RobotPeripheralStore from '../../stores/RobotPeripheralStore';

var NameEdit = React.createClass({
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
  validatePeripheralName(name) {
    let re = new RegExp("^[A-Za-z][A-Za-z0-9]+$");
    let isValid = re.test(name);
    let allCurrentPeripherals = RobotPeripheralStore.getPeripherals();
    let isDuplicate = _.some(allCurrentPeripherals, (peripheral) => {return peripheral.name === name});
    return isValid && !isDuplicate;
  },
  render() {
    return (
      <div>
	<RIEInput
	  className="static"
	  classEditing="editing"
	  classInvalid="invalid"
	  validate={this.validatePeripheralName}
	  value={this.props.name}
	  change={this.dataChange}
	  propName="name"
	/>
      </div>
    );
  }
});

export default NameEdit;
