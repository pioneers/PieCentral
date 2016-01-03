import React from 'react';
import EditorActionCreators from '../actions/EditorActionCreators';
import {
  Button,
  ButtonGroup,
  ButtonToolbar,
  Glyphicon,
  OverlayTrigger,
  Tooltip
} from 'react-bootstrap';
import _ from 'lodash';

export default React.createClass({
  propTypes: {
    currentFilename: React.PropTypes.string.isRequired,
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
          <ButtonGroup>
            { this.props.currentFilename +
              (this.props.unsavedChanges ? '*' : '') }
          </ButtonGroup>
          { this.renderToolbar() }
        </ButtonToolbar>
      </div>
    );
  }
});
