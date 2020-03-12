import React from 'react';
import PropTypes from 'prop-types';
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
        id={props.id}
      >
        <Glyphicon glyph={props.glyph} />
      </Button>
    </OverlayTrigger>
  );
};

TooltipButton.propTypes = {
  id: PropTypes.string.isRequired,
  text: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
  glyph: PropTypes.string.isRequired,
  disabled: PropTypes.bool.isRequired,
  bsStyle: PropTypes.string,
  placement: PropTypes.string,
};

export default TooltipButton;
