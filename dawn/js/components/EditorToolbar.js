import React from 'react';
import EditorActionCreators from '../actions/EditorActionCreators';
import {
  Button,
  ButtonGroup,
  ButtonToolbar,
  Panel,
  DropdownButton,
  MenuItem,
  Modal,
  Input,
  ListGroup,
  ListGroupItem,
  Glyphicon,
  OverlayTrigger,
  Tooltip
} from 'react-bootstrap';
import _ from 'lodash';

export default React.createClass({
  propTypes: {
    currentFilePath: React.PropTypes.string,
    buttons: React.PropTypes.array.isRequired
  },
  renderToolbar() {
    return (
      _.map(this.props.buttons, (group, groupIndex) => {
        return (
          <ButtonGroup key={String(groupIndex)}>
            {_.map(group, (button, buttonIndex) => {
              return (
                <OverlayTrigger
                  key={String(buttonIndex)}
                  placement="top"
                  overlay={<Tooltip id="{button.name.toLowerCase()}-tooltip">
                    {button.name}
                  </Tooltip>}>
                  <Button onClick={button.onClick} bsSize="small">
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
            { this.props.currentFilePath || "[ New File ]" }
          </ButtonGroup>
          { this.renderToolbar() }
        </ButtonToolbar>
      </div>
    );
  }
});
