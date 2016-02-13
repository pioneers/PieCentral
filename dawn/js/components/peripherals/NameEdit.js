import React from 'react';
import InlineEdit from 'react-edit-inline';
import Ansible from '../../utils/Ansible';
import AlertActions from '../../actions/AlertActions';

var NameEdit = React.createClass({
  propTypes: {
    name: React.PropTypes.string,
    id: React.PropTypes.string
  },
  dataChange(data) {
    Ansible.sendMessage('custom_names', {
      id: this.props.id,
      name: data.name
    });
  },
  validatePeripheralName(name) {
    let re = new RegExp("^[A-Za-z][A-Za-z0-9]+$");
    let valid = re.test(name);
    return valid;
  },
  render() {
    return (
      <div>
        <InlineEdit
          className="static"
          validate={this.validatePeripheralName}
          activeClassName="editing"
          text={this.props.name}
          change={this.dataChange}
          paramName="name"
          style = {{
            minWidth: 150,
            borderRadius: '7px',
            display: 'inline-block',
            margin: 0,
            padding: 0,
            fontSize:15
          }}
        />
      </div>
    );
  }
});

export default NameEdit;
