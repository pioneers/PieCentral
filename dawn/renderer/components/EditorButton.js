import React from 'react';
import {
  Button,
  Glyphicon,
  OverlayTrigger,
  Tooltip,
} from 'react-bootstrap';

const EditorButton = (props) => {
  const tooltip = (
    <Tooltip id="tooltip">{props.text}</Tooltip>
  );
  return (
    <OverlayTrigger placement="top" overlay={tooltip}>
      <Button
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
  text: React.PropTypes.string,
  onClick: React.PropTypes.func,
  glyph: React.PropTypes.string,
  disabled: React.PropTypes.bool,
};

export default EditorButton;
