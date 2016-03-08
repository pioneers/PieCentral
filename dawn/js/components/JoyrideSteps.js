/*
 * Specifies the list of steps to follow in the joyride
 * (the interactive intro tour). Each object in the list is a step.
 */
export default [
  {
    title: 'Header and Version',
    text: 'This header displays the version of Dawn that you have. We may periodically release updates to Dawn, so always make sure you have the latest version.',
    selector: '#header-title',
    position: 'bottom',
    type: 'hover'
  },{
    title: 'Status Indicator',
    text: 'This displays your connection status with the robot and (when connected) the robot\'s current battery level. Keep an eye on the battery level and charge the battery whenever it is nearly drained. Allowing the battery level to drop too low could damage your battery permanently.',
    selector: '#battery-indicator',
    position: 'bottom',
    type: 'hover'
  },{
    title: 'Editor',
    text: 'This is the code editor. Create and edit your robot\'s code here. The editor has autocompletion. Press CTRL/CMD-SPACEBAR to see autocomplete suggestions.',
    selector: '.ace_editor',
    position: 'bottom-left',
    type: 'hover'
  },{
    title: 'File operations',
    text: 'Use these buttons to create, open, and save code files.',
    selector: '#file-operations-buttons',
    position: 'bottom',
    type: 'hover'
  },{
    title: 'Code execution',
    text: 'Use these buttons to run and stop your code, upload your code (for the competition), toggle the output console, and clear the output console.',
    selector: '#code-execution-buttons',
    position: 'bottom',
    type: 'hover'
  },{
    title: 'Editor Theme',
    text: 'You can choose your editor\'s theme using this dropdown. Your preferences will be saved automatically.',
    selector: '#choose-theme',
    position: 'bottom',
    type: 'hover'
  },{
    title: 'Peripherals',
    text: 'This panel displays info about your robot\'s peripherals, including motors and sensors. You can click on a peripheral name to change it. The name you assign to a peripheral here is the same name you should use to reference the peripheral in your code.',
    selector: '#peripherals-panel',
    position: 'left',
    type: 'hover'
  },{
    title: 'Gamepads',
    text: 'This panel displays all the connected gamepads. Once you have a gamepad connected, press the details buttons to see more gamepad details.',
    selector: '#gamepads-panel',
    position: 'left',
    type: 'hover'
  },{
    title: 'Updates',
    text: 'Occasionally we may release updates to the robot\'s software. When this happens, you will download two files, an update package and its signature, and click on this button to upload those updates to the robot.',
    selector: '#update-software-button',
    position: 'left',
    type: 'hover'
  },{
    title: 'Robot IP',
    text: 'This sets the IP address Dawn will use when trying to connect to the robot.',
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
