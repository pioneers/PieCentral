#include "Arduino.h" //to get digital write, etc.

#include "ui.h"
#include "motor.h"
#include "pid.h"
#include "encoder.h"
#include "current_limit.h"
//Code here that helps deal with the human-readable UI.
//Will contain code that will do the following:

//Let the user set State: Disabled, Enabled (open loop), Enabled (PID velocity), Enabled (PID position).
//Let the user set the setpoint.
//Let the user set the current limit stuff?
//Let the user enable/disable printing of various outputs (Position, current, etc)

//This code will be called by void loop in Integrated.  It will NOT use timers or interrupts.
unsigned long manualHeartbeatLimit = 30000;

void manual_ui()
{


  if (heartbeat > manualHeartbeatLimit) {
    disable();
    Serial.println("We ded");
  }
  if (continualPrint) {
    Serial.print("PWM: ");
    Serial.print(pwmPID,5);
    Serial.print("  |  Encoder Pos: ");
    Serial.print(readPos());
    Serial.print("  |  Encoder Vel: ");
    Serial.println(readVel());
  }
  while (Serial.available()) {
    char c = Serial.read();  //gets one byte from serial buffer
    if ( (c == 10) || (c == 13)) //if c is \n or \r
    {
      //do nothing.
    }
    else if (c == 's') 
    {
      pwmInput = Serial.parseFloat();
      Serial.print("New Speed: ");
      Serial.println(pwmInput);
    }
    else if (c == 'c') {
      Serial.println("Clearing Fault");
      clearFault();
    }
    else if (c == 'p') {
      Serial.read();
      char val = Serial.read();
      if (val == 'p') {
        driveMode = 2;
        enablePos();
        Serial.println("Turning on PID Position mode");
      } 
      else if (val == 'v') {
        driveMode = 1;
        enableVel();
        Serial.println("Turning on PID Position mode");
      }
    }
    else if (c == 'm') {
      Serial.println("Turning on manual mode");
      disablePID();
      driveMode = 0;
    }
    else if (c == 'e') {
      Serial.println("Enabled");
      enable();
    }
    else if (c == 'd') {
      Serial.println("Disabled");
      disable();
    }
    else if (c == 'r') {
      Serial.print("Encoder Pos: ");
      Serial.println(readPos());
      Serial.print("Encoder Vel: ");
      Serial.println(readVel());
      Serial.print("Current: ");
      Serial.println(readCurrent());
    }
    else if (c == 't') {
      continualPrint = !continualPrint;
      Serial.println("Toggling readout prints");
    }
    else if (c == 'w') {
      Serial.read();
      char val1 = Serial.read();
      char val2 = Serial.read();
      
      if (val1 == 'c') {
        setCurrentThreshold(Serial.parseFloat());
        Serial.print("New current threshold: ");
        Serial.println(current_threshold);
      }
      else if (val1 == 'p') {
        if (val2 == 'p'){
          setPosKP(Serial.parseFloat());
          Serial.print("New PID position KP value: ");
          Serial.println(PIDPosKP);
        }
        else if (val2 == 'i'){
          setPosKI(Serial.parseFloat());
          Serial.print("New PID position KI value: ");
          Serial.println(PIDPosKI);
        }
        else if (val2 == 'd'){
          setPosKD(Serial.parseFloat());
          Serial.print("New PID position KD value: ");
          Serial.println(PIDPosKD);
        }
        else {
          setPosSetpoint(Serial.parseFloat());
          Serial.print("New PID position: ");
          Serial.println(PIDPos);
        }
        updatePosPID();

    }
    else if (val1 == 'v') {
      if (val2 == 'p') {
        setVelKP(Serial.parseFloat());
        Serial.print("New PID velocity KP value: ");
        Serial.println(PIDVelKP);
      }
      else if (val2 == 'i') {
        setVelKI(Serial.parseFloat());
        Serial.print("New PID velocity KI value: ");
        Serial.println(PIDVelKI);
      }
      else if (val2 == 'd') {
        setVelKD(Serial.parseFloat());
        Serial.print("New PID velocity KD value: ");
        Serial.println(PIDVelKD);
      } 
      else {
        setVelSetpoint(Serial.parseFloat());
        Serial.print("New PID velocity: ");
        Serial.println(PIDVel);
      }
      updateVelPID();
    }
    
    else {
      Serial.println("Cannot write to that");
    }
  }
  else if (c == 'b') {
    Serial.println("Heartbeat");
    heartbeat = 0;
  }
  else if (c == 'h') {
    hibike = true;
    Serial.println("Going to hibike mode");
  }
  else if (c == 'z') {
    hibike = false;
    Serial.println("Turning off hibike");
  }
  else if (c == '?') {
    Serial.println("Manual Controls: \ns <x> - sets pwm to x \nc     - clears faults \np <x> - turns on PID mode, velocity if x = v, position if x = p \nm     - turns on manual input mode \ne     - enables motor \nd     - disables motor \nr     - displays 1 print of all readable values \nt     - toggles continual printing of pos and vel \nb     - send heartbeat \nh     - switch hibike mode \nz     - switch human controls \nw <x> <y> - writes the value y to the variable x");
  }
  else {
    Serial.println("Bad input");
  }
}
delay(10);
}

