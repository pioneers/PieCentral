/*
 * Specifies the list of steps to follow in the joyride
 * (the interactive intro tour). Each object in the list is a step.
 */
export default [
  {
    title: 'Battery Indicator',
    text: 'This displays your robot\'s current battery level. Keep an eye on the battery level and charge the battery whenever it is nearly drained.',
    selector: '#battery-indicator',
    position: 'bottom',
    type: 'hover'
  },{
    title: 'Editor',
    text: 'This is the code editor. Create and edit your robot\'s code here.',
    selector: '.ace_editor',
    position: 'bottom-left',
    type: 'hover'
  },{
    title: 'File operations',
    text: 'Use these buttons to open, save, create, and delete files.',
    selector: '#file-operations-buttons',
    position: 'bottom',
    type: 'hover'
  },{
    title: 'Code execution',
    text: 'Use these buttons to run and stop your code, toggle the output console, and clear the output console.',
    selector: '#code-execution-buttons',
    position: 'bottom',
    type: 'hover'
  },{
    title: 'Peripherals',
    text: 'This panel displays info about your robot\'s peripherals, including motors and sensors. You can click on a peripheral name to change it.',
    selector: '#peripherals-panel',
    position: 'left',
    type: 'hover'
  },{
    title: 'Gamepads',
    text: 'This panel displays all the connected gamepads.',
    selector: '#gamepads-panel',
    position: 'left',
    type: 'hover'
  },{
    title: 'Robot IP',
    text: 'Click this button to edit the IP address of the robot.',
    selector: '#update-address-button',
    position: 'left',
    type: 'hover'
  },{
    title: 'That\'s it!',
    text: 'If you would like to see this tour again, simply click this button.',
    selector: '#tour-button',
    position: 'left',
    type: 'hover'
  }
];
