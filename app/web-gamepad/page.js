var gamepad = angular.module('gamepad', [])

.controller('gamepadController', [
  '$scope', '$http', 
  function($scope) {
    var socket = io.connect();
    $scope.gamepadIndex = 0;
    var typical_button_count = 16;
    var typical_axis_count = 4;
    $scope.ticking = false;
    $scope.prevRawGamepadTypes = [];
    $scope.prevTimestamps = [];

    $scope.sendGamepadData = function(data) {
      socket.emit('gamepad', { data: data },
          function processResponse(response) {
            console.log(response);
          });
    };

    $scope.startSend = function() {
      var gamepads = navigator.getGamepads();
      for(var i = 0; i < gamepads.length; i++) {
        if(gamepads[i] !== undefined) { // takes the first valid gamepad
          $scope.gamepadIndex = i;
          break;
        }
      }
      setInterval(function() { 
        var gamepads = navigator.getGamepads();
        var gamepad = gamepads[$scope.gamepadIndex];
        gamepad.ANALOGUE_BUTTON_THRESHOLD = .5;

        $scope.startPolling = function() {
          if (!gamepadSupport.ticking) {
            gamepadSupport.ticking = true;
            gamepadSupport.tick();
          }
        }

        $scope.stopPolling = function() {
          gamepadSupport.ticking = false;
        }

        $scope.tick = function() {
          gamepadSupport.pollStatus();
          gamepadSupport.scheduleNextTick();
        }

        $scope.scheduleNextTick = function() {
          if (gamepadSupport.ticking) {
            if (window.requestAnimationFrame) {
              window.requestAnimationFrame(gamepadSupport.tick);
            } else if (window.webkitRequestAnimationFrame) {
              window.webkitRequestAnimationFrame(gamepadSupport.tick);
            } else if (window.mozRequestAnimationFrame) {
              window.mozRequestAnimationFrame(gamepadSupport.tick);
            }
          }
        }

        $scope.pollStatus = function() {
          //necessary only on Chrome
          gamepadSupport.pollGamepads();

          for (var i in gamepadSupport) {
            var gamepad = gamepadSupport.gamepads[i];

            if (gamepad.timestamp && (gamepad.timestamp == gamepadSupport.prevTimestamps[i])) {
              continue;
            }
            gamepadSupport.prevTimestamps[i] = gamepad.timestamp;

            gamepadSupport.updateDisplay(i);
          }
        }

        $scope.pollGamepads = function() {
          var rawGamepads = gamepads; //may need to change this

          if (rawGamepads) {
            gamepadSupport.gamepads = [];
            var gamepadsChanged = false;
            for (var i = 0; i < rawGamepads.length; i++) {
              if (typeof rawGamepads[i] != gamepadSupport.prevRawGamepadTypes[i]) {
                gamepadsChanged = true;
                gamepadSupport.prevRawGamepadTypes[i] = typeof rawGamepads[i];
              }

              if (rawGamepads[i]) {
                gamepadSupport.gamepads.push(rawGamepads[i]);
              }
            }

            if (gamepadsChanged) {
              user.updateGamepads(gamepadSupport.gamepads);
            }
          }
        }

        $scope.updateDisplay() = function(gamepadID) {
          var gamepad = gamepadSupport.gamepads[gamepadID];
          user.updateButton(gamepad.button[0], gamepadID, 'button-1');
          user.updateButton(gamepad.button[1], gamepadID, 'button-2');
          user.updateButton(gamepad.button[2], gamepadID, 'button-3');
          user.updateButton(gamepad.button[3], gamepadID, 'button-4');

          user.updateButton(gamepad.button[4], gamepadID, 'button-left-shoulder-top');
          user.updateButton(gamepad.button[6], gamepadID, 'button-left-shoulder-bottom');
          user.updateButton(gamepad.button[5], gamepadID, 'button-right-shoulder-top');
          user.updateButton(gamepad.button[7], gamepadID, 'button-right-shoulder-bottom');

          user.updateButton(gamepad.button[8], gamepadID, 'button-select');
          user.updateButton(gamepad.button[9], gamepadID, 'button-start');

          user.updateButton(gamepad.button[10], gamepadID, 'stick-1');
          user.updateButton(gamepad.button[11], gamepadID, 'stick-2');

          user.updateButton(gamepad.button[12], gamepadID, 'button-dpad-top');
          user.updateButton(gamepad.button[13], gamepadID, 'button-dpad-bottom');
          user.updateButton(gamepad.button[14], gamepadID, 'button-dpad-left');
          user.updateButton(gamepad.button[15], gamepadID, 'button-dpad-right');

          user.updateAxis(gamepad.axes[0], gamepadID, 'stick-1-axis-x', 'stick-1', true);
          user.updateAxis(gamepad.axes[1], gamepadID, 'stick-1-axis-y', 'stick-1', false);
          user.updateAxis(gamepad.axes[2], gamepadID, 'stick-2-axis-x', 'stick-2', true);
          user.updateAxis(gamepad.axes[3], gamepadID, 'stick-2-axis-y', 'stick-2', false);
        }

        gamepad.buttonPressed_ = function(pad, buttonId) {
          return pad.buttons[buttonId] && (pad.buttons[buttonId] > gamepad.ANALOGUE_BUTTON_THRESHOLD);
        };
        $scope.sendGamepadData(JSON.stringify(gamepads[$scope.gamepadIndex]));

      }, 100);
    };

    window.requestAnimFrame = (function(){
      return  window.requestAnimationFrame       ||
      window.webkitRequestAnimationFrame ||
      window.mozRequestAnimationFrame    ||
      window.oRequestAnimationFrame      ||
      window.msRequestAnimationFrame     ||
      function(/* function */ callback, /* DOMElement */ element) {
          window.setTimeout(callback, 1000 / 60);
      };
    })();
  }
]);


