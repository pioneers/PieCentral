angular.module('page', [])

.controller('userController', [
	'$scope', '$http',
	function($scope) {
		var user = {
			$scope.visible_threshold = 0.1;
			$scope.stick_offset = 25;
			$scope.analog_button_threshold = 0.5;

			$scope.init = function() {
				user.updateMode();
				user.updateGamepads();
			}

			//for users who cannot see the gamepad, they can get raw data
			$scope.updateMode = function() {
				if (document.querySelector('#mode-raw').checked) {
					document.querySelector('#gamepads').classList.add('raw');
				} else {
					document.querySelector('#gamepads').classList.remove('raw');
				}
			}

			$scope.updateGamepads = function(gamepads) {
				var els = document.querySelectorAll('#gamepads > :not(.template)');

				for (var i = 0, el; el = els[i]; i++) {
					e1.parentNode.removeChild(e1);
				}

				var padsConnected = false;

				if (gamepads) {
					for (var i in gamepads) {
						var gamepad = gamepads[i];
						if (gamepad) {
							var e1 = document.createElement('li');
						}
					}
				}
			}

			$scope.updateButton = function(value, gamepadID, id) {
				var gamepadEl = document.querySelector('#gamepad-' + gamepadID);

				var value, pressed;
				if (typeof(button) == 'object') {
					value = button.value;
					pressed = button.pressed;
				} else {
					value = button;
					pressed = button > user.analog_button_threshold;
				}

				//update button visually
				var buttonEl = gamepadEl.querySelector('[name="' + id + '"]');
				if (buttonEl) {
					if (pressed) {
						buttonEl.classList.add('pressed');
					} else {
						buttonEl.classList.remove('pressed');
					}
				}

				
			}

			$scope.updateAxis = function(value, gamepadID, labelID, stickID, horizontal) {
				var gamepadEl = document.querySelector('#gamepad-' + gamepadID);

			}
		}		
	}
]);
