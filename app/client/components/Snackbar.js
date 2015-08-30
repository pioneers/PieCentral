import React from 'react';
import Notification from 'react-notification';
import EditorStore from '../stores/EditorStore';

var Snackbar = React.createClass({
  getInitialState() {
    return {
      isActive: false,
      message: '',
      action: 'Dismiss',
      dismissAfter: 4000
    }
  },
  loadError(){
    this.setState({
      ...this.state,
      isActive: true,
      message: 'Failed to load file from robot.',
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
    EditorStore.on('loadError', this.loadError)
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
