import React from 'react';
import InlineEdit from 'react-edit-inline';
import RobotActions from '../../actions/RobotActions';

var NameEdit = React.createClass({
  propTypes: {
    name: React.PropTypes.string,
    id: React.PropTypes.string
  },
  dataChange(data) {
    RobotActions.updatePeripheralName(this.props.id, data.name);
  },
  render() {
    return (
      <div>
        <InlineEdit
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
            fontSize:15,
            outline: 0,
            border: 0
          }}
        />
      </div>
    );
  }
});
  

export default NameEdit;
