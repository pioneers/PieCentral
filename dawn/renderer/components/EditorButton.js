import React from 'react';
import {
  Button,
  Glyphicon,
  OverlayTrigger,
  Tooltip,
} from 'react-bootstrap';

const EditorButton = (props) => {
  const tooltip = (
    <Tooltip id={`tooltip-editor-button-${props.id}`}>{props.text}</Tooltip>
  );
  return (
    <OverlayTrigger placement="top" overlay={tooltip}>
      <Button
        type="button"
        bsStyle="default"
        bsSize="small"
        onClick={props.onClick}
        disabled={props.disabled}
      >
        <Glyphicon glyph={props.glyph} />
      </Button>
    </OverlayTrigger>
  );
};

EditorButton.propTypes = {
  id: React.PropTypes.string.isRequired,
  text: React.PropTypes.string.isRequired,
  onClick: React.PropTypes.func.isRequired,
  glyph: React.PropTypes.string.isRequired,
  disabled: React.PropTypes.bool,
};

export default EditorButton;
