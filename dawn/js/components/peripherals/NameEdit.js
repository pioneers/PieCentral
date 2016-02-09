import React from 'react';
import InlineEdit from 'react-edit-inline';
import Ansible from '../../utils/Ansible';

var NameEdit = React.createClass({
  propTypes: {
    name: React.PropTypes.string,
    id: React.PropTypes.string
  },
  styles: {
    editing: {
      border: '5px solid red'
    }
  },
  dataChange(data) {
    Ansible.sendMessage('custom_names', {
      id: this.props.id,
      name: data.name
    });
  },
  render() {
    return (
      <div>
        <InlineEdit
          className="editing"
          text={this.props.name}
          change={this.dataChange}
          paramName="name"
          style = {this.styles.editing}
        />
      </div>
    );
  }
});

NameEdit.styles = {
  editing: {
    border: '5px solid redasda'
  }
}

export default NameEdit;
