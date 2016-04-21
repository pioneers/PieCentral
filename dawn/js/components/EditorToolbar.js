import React from 'react';
import EditorActionCreators from '../actions/EditorActionCreators';
import {
  Button,
  DropdownButton,
  MenuItem,
  ButtonGroup,
  ButtonToolbar,
  Glyphicon,
  OverlayTrigger,
  Tooltip
} from 'react-bootstrap';
import Ansible from '../utils/Ansible';
import _ from 'lodash';

export default React.createClass({
  propTypes: {
    buttons: React.PropTypes.array.isRequired,
    unsavedChanges: React.PropTypes.bool.isRequired
  },
  getInitialState() {
    return {gameMode: -1};
  },
  renderToolbar() {
    return (
      _.map(this.props.buttons, (group, groupIndex) => {
        return (
          <ButtonGroup key={String(groupIndex)} id={group.groupId}>
            {_.map(group.buttons, (button, buttonIndex) => {
              return button.render(String(groupIndex) + String(buttonIndex));
            })}
          </ButtonGroup>
        );
      })
    );
  },
  changeGameMode(mode) {
    // Possible gamemodes that can be sent to runtime.
    let gameModes = [
      {enabled: true, autonomous: true}, // autonomous mode
      {enabled: false, autonomous: true}, // disabled mode
      {enabled: true, autonomous: false} // teleop mode
    ];
    Ansible.sendMessage('game', gameModes[mode]);
    this.setState({gameMode: mode});
  },
  render() {
    return (
      <div>
        <ButtonToolbar id="editor-toolbar">
          { this.renderToolbar() }
          <DropdownButton
            disabled={!this.props.runtimeStatus}
            title="Mode"
            bsSize="small"
            id="choose-mode">
            <MenuItem
              active={this.state.gameMode == 0}
              onClick={()=>this.changeGameMode(0)}
              key={0}>Autonomous</MenuItem>
            <MenuItem
              active={this.state.gameMode == 1}
              onClick={()=>this.changeGameMode(1)}
              key={1}>Disable</MenuItem>
            <MenuItem
              active={this.state.gameMode == 2}
              onClick={()=>this.changeGameMode(2)}
              key={2}>TeleOp</MenuItem>
          </DropdownButton>
          <DropdownButton
            title="Theme"
            bsSize="small"
            id="choose-theme">
            { _.map(this.props.themes, (theme, index) => {
              return (
                <MenuItem
                  active={theme == this.props.editorTheme}
                  onClick={_.partial(this.props.changeTheme, theme)}
                  key={index}>
                  {theme}
                </MenuItem>
              );
            }) }
          </DropdownButton>
        </ButtonToolbar>
      </div>
    );
  }
});
