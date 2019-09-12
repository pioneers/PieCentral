var socket = io('http://127.0.0.1:5000');

socket.on('connect', function(data) {
    socket.emit('join', 'scoreboard');
  });

socket.on('launch_button_timer_start', function(allianceButton) {
    alliance = JSON.parse(allianceButton).alliance
    button = JSON.parse(allianceButton).button
    if (alliance == "blue"){
        if (button == 1) {
            timer1()
        } else {
            timer2()
        }
    } else {
        if (button == 1) {
            timer3()
        } else {
            timer4()
        }
    }
    });

socket.on('stage_timer_start', function(secondsInStage) {
    time = JSON.parse(secondsInStage.time)
    startOverdrive(time)
})