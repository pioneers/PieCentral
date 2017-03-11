import React from 'react';
import {
  Button,
  Glyphicon,
  OverlayTrigger,
  Tooltip,
} from 'react-bootstrap';

const TooltipButton = (props) => {
  const tooltip = (
    <Tooltip id={`tooltip-editor-button-${props.id}`}>{props.text}</Tooltip>
  );
  return (
    <OverlayTrigger placement={props.placement || 'top'} overlay={tooltip}>
      <Button
        type="button"
        bsStyle={props.bsStyle || 'default'}
        bsSize="small"
        onClick={props.onClick}
        disabled={props.disabled}
        active={props.active}
        id={props.id}
      >
        <Glyphicon glyph={props.glyph} />
      </Button>
    </OverlayTrigger>
  );
};

TooltipButton.propTypes = {
  id: React.PropTypes.string.isRequired,
  text: React.PropTypes.string.isRequired,
  onClick: React.PropTypes.func.isRequired,
  glyph: React.PropTypes.string.isRequired,
  disabled: React.PropTypes.bool,
  bsStyle: React.PropTypes.string,
  active: React.PropTypes.bool,
  placement: React.PropTypes.string,
};

export default TooltipButton;
