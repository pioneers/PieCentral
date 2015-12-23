React = require('react')
Environment = require('../utils/Environment')
if Environment.isBrowser
  Joyride = require('react-joyride')
Router = require('react-router')
DNav = require('./DNav')
Dashboard = require('./Dashboard')

module.exports = Dawn = React.createClass
  displayName: 'Dawn'

  getInitialState: ->
    steps: []

  addSteps: (steps) ->
    joyride = this.refs.joyride

    if not Array.isArray(steps)
      steps = [steps]

    if not steps.length
      return false

    this.setState((currentState) ->
      currentState.steps = currentState.steps.concat(joyride.parseSteps(steps))
      return currentState
    )

  addTooltip: (data) ->
    this.refs.joyride.addTooltip(data)

  startTour: ->
    this.refs.joyride.start(false)

  componentDidMount: ->
    this.addSteps([{
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
      title: 'File selector',
      text: 'This dropdown displays a list of your code files, and allows you to switch between them.',
      selector: '#choose-file-button',
      position: 'bottom',
      type: 'hover'
    },{
      title: 'File operations',
      text: 'Use these buttons to save your code, create and delete files, and download and upload code.',
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
      text: 'This panel displays info about your robot\'s peripherals, including motors and sensors.',
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
      title: 'That\'s it!',
      text: 'If you would like to see this tour again, simply click this button.',
      selector: '#tour-button',
      position: 'left',
      type: 'hover'
    }])

  render: ->
    joyride = null
    if Joyride?
      joyride = <Joyride ref="joyride" steps={this.state.steps} />
    return (<div>
      <DNav {...this.props} startTour={this.startTour}/>
      {joyride}
      <div style={height: '60px', marginBottom: '21px'}/>
      {React.cloneElement(this.props.children, {
        addSteps: this.addSteps,
        addTooltip: this.addTooltip
      })}
    </div>)
