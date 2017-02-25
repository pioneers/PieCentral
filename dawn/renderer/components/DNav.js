import React from 'react';
import {
  Navbar,
  Nav,
  ButtonToolbar,
  ButtonGroup,
  Tooltip,
  OverlayTrigger,
  Button,
  Glyphicon}  from 'react-bootstrap';
import StatusLabel from './StatusLabel';

export default React.createClass({
  displayName: 'DNav',
  getInitialState() {
    return { showUpdateModal: false };
  },
  IPvalidate(address) {
    return /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/.test(address);
  },
  saveAddress(currentAddress) {
    let prompt = smalltalk.prompt(
      'Enter the IP address of the robot:',
      'Examples: 192.168.13.100, 127.0.0.1',
      currentAddress
    );
    prompt.then((value) => {
      if (/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/.test(value)) {
        storage.set('runtimeAddress', {
          address: value
        }, (err)=>{
          if (err) throw err;
          Ansible.reload();
        });
      } else if (value != null) {
        console.log("Bad IP: " + value);
      }
    }, ()=>console.log('Canceled'));
  },
  updateAddress() {
    storage.has('runtimeAddress').then((hasKey)=>{
      if (hasKey) {
        storage.get('runtimeAddress').then((data)=>{
          this.saveAddress(data.address);
        });
      } else {
        this.saveAddress('192.168.13.100');
      }
    });
  },
  getDawnVersion() {
    return VERSION;
  },
  toggleUpdateModal() {
    this.setState({ showUpdateModal: !this.state.showUpdateModal });
  },
  render() {
    return (
      <Navbar fixedTop fluid>
        <UpdateBox
          isRunningCode={this.props.isRunningCode}
          connectionStatus={this.props.connection}
          runtimeStatus={this.props.runtimeStatus}
          shouldShow={this.state.showUpdateModal}
          hide={this.toggleUpdateModal} />
        <Navbar.Header>
          <Navbar.Brand id="header-title">
            {"Dawn v" + this.getDawnVersion()}
          </Navbar.Brand>
          <Navbar.Toggle />
        </Navbar.Header>
        <Navbar.Collapse>
  	      <Navbar.Text>
      	    <StatusLabel
      	      connectionStatus={this.props.connection}
      	      runtimeStatus={this.props.runtimeStatus}
      	      battery={this.props.battery}
            />
  	      </Navbar.Text>
          <Navbar.Form
            pullRight={true}
          >
          </Navbar.Form>
        </Navbar.Collapse>
      </Navbar>
    );
  }
});
