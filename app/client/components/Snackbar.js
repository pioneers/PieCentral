import React from 'react';
import Notification from 'react-notification';
import EditorStore from '../stores/EditorStore';

var Snackbar = React.createClass({
  getInitialState() {
    return {
      isActive: false,
      message: '',
      action: 'Dismiss',
    }
  },
  errorNotification(err){
    this.setState({
      ...this.state,
      isActive: true,
      message: err
    });
  },
  handleClick() {
    this.setState({
      ...this.state,
      isActive: false,
      message: ''
    });
  },
  componentDidMount() {
    EditorStore.on('error', this.errorNotification)
  },
  render() {
    return (
      <Notification
        {...this.state}
        dismissAfter={ 6000 }
        onClick={ this.handleClick }
        onDismiss={ this.handleClick }
      />
    )
  }
});

export default Snackbar;
