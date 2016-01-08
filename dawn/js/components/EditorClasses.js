import React from 'react';
import { OverlayTrigger, Button, Tooltip, Glyphicon } from 'react-bootstrap';

/* Represents a single button in the EditorToolbar, specifies its
 * name, tooltip text, onClick callback, glyphicon, and conditions for
 * being disabled.
 */
export class EditorButton {
  constructor(name, text, callback, glyph, disabled) {
    this.name = name;
    this.text = text;
    this.callback = callback;
    this.glyph = glyph;
    this.disabled = disabled;
  }

  render(key) {
    return (
      <OverlayTrigger
        key={key}
        placement="top"
        overlay={
          <Tooltip id={ this.name.toLowerCase() + '-tooltip' }>
            {this.text}
          </Tooltip>
        }>
        <Button
          onClick={this.callback}
          bsSize="small"
          disabled={this.disabled || false}
          >
          <Glyphicon glyph={this.glyph} />
        </Button>
      </OverlayTrigger>
    );
  }
}
