import React from 'react';
import { Classes, Colors } from '@blueprintjs/core';

export function withTheme(WrappedComponent) {
  return (props) => {
    let className, background;
    if (props.darkTheme) {
      className = Classes.DARK;
      background = Colors.DARK_GRAY1;
    } else {
      className = Classes.LIGHT;
      background = Colors.LIGHT_GRAY1;
    }
    return (
      <div className={`bg-theme ${Classes.TEXT_LARGE} ${className}`} style={{ background }}>
        <WrappedComponent {...props} />
      </div>
    );
  };
};
