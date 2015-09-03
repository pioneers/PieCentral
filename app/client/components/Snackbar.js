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
  saveSuccessNotification(){
    this.setState({
      ...this.state,
      isActive: true,
      message: 'Save successful!'
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
    EditorStore.on('error', this.errorNotification);
    EditorStore.on('success', this.saveSuccessNotification);
  },
  render() {
    return (
      <Notification
        {...this.state}
        onClick={ this.handleClick }
        onDismiss={ this.handleClick }
      />
    )
  }
});

export default Snackbar;
