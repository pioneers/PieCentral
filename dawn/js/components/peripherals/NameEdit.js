import React from 'react';
import InlineEdit from 'react-edit-inline';
import Ansible from '../../utils/Ansible';
import smalltalk from 'smalltalk';

var NameEdit = React.createClass({
  propTypes: {
    name: React.PropTypes.string,
    id: React.PropTypes.string
  },
  dataChange(data) {
    var x = new RegExp("^[A-Za-z][A-Za-z0-9]+$");
    if (x.test(data.name)) {
      Ansible.sendMessage('custom_names', {
        id: this.props.id,
        name: data.name
      });
    } else {
      smalltalk.alert(
        'Invalid Peripheral Name',
        'Names must be alphanumeric, and cannot contain spaces or start with a number.'
      ).then(()=>console.log('Ok.'), ()=>console.log('Cancel.'));
    }
  },
  render() {
    return (
      <div>
        <InlineEdit
          className="static"
          activeClassName="editing"
          text={this.props.name}
          change={this.dataChange}
          paramName="name"
          style = {{
            backgroundColor: 'white',
            minWidth: 150,
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
