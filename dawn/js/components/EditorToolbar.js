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
import _ from 'lodash';

export default React.createClass({
  propTypes: {
    buttons: React.PropTypes.array.isRequired,
    unsavedChanges: React.PropTypes.bool.isRequired
  },
  renderToolbar() {
    return (
      _.map(this.props.buttons, (group, groupIndex) => {
        return (
          <ButtonGroup key={String(groupIndex)} id={group.groupId}>
            {_.map(group.buttons, (button, buttonIndex) => {
              return (
                <OverlayTrigger
                  key={String(buttonIndex)}
                  placement="top"
                  overlay={<Tooltip id="{button.name.toLowerCase()}-tooltip">
                    {button.text}
                  </Tooltip>}>
                  <Button
                    onClick={button.onClick}
                    bsSize="small"
                    disabled={button.disabled || false}
                    >
                    <Glyphicon glyph={button.glyph} />
                  </Button>
                </OverlayTrigger>
              );
            })}
          </ButtonGroup>
        );
      })
    );
  },
  render() {
    return (
      <div>
        <ButtonToolbar id="editor-toolbar">
          { this.renderToolbar() }
          <DropdownButton
            title={this.props.editorTheme}
            bsSize="small"
            id="choose-theme">
            { _.map(this.props.themes, (theme, index) => {
              if (theme !== this.props.editorTheme) {
                return (
                  <MenuItem
                    onClick={_.partial(this.props.changeTheme, theme)}
                    key={index}>
                    {theme}
                  </MenuItem>
                );
              }
            }) }
          </DropdownButton>
        </ButtonToolbar>
      </div>
    );
  }
});
