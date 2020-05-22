# Shepherd

Shepherd is the team that is in charge of field control. 
Shepherd brings together all the data on the game field into one centralized location, where it keeps track of score, processes game-specific actions, keeps track of time, and informs the scoreboard.

## Architecture

Shepherd is essentially a [Flask](https://palletsprojects.com/p/flask/) web app that communicates with:

Arduino devices on the field over USB serial.
Each robot's [Runtime](https://github.com/pioneers/PieCentral/tree/master/runtime) instance using MessagePack remote procedure calls over TCP.
Each driver station's [Dawn](https://github.com/pioneers/PieCentral/tree/master/dawn) instance.
Each scoreboard client, which is rendered with jQuery. Typically, there is a scoreboard on each side of the field, a projection for spectators, and a fourth for the field control staff.
Each perk selection tablet (specific to Sugar Blast).

## Installing dependencies

### LCM

#### Linux
Run the installlcm script
```
./installlcm
```

#### Mac
1. Set the Java Version to 8
```
export JAVA_HOME=$(/usr/libexec/java_home -v 1.8)
```
2. Run the installlcm script
```
./installlcm
```

## Running Shepherd

### Instructions for 2018-2019, aka Sugar Blast:
This year, we ran Shepherd on Ajax, one of the computers owned by PiE. 
In order to make it easier to run Shepherd on various machines, we added needed dependencies to a Pipfile. 
This allows you to work in a virtual environment with all necessary dependencies 
(except for [LCM](https://lcm-proj.github.io/build_instructions.html), which must be installed beforehand) 
by issuing the following commands in PieCentral/shepherd:
```
pipenv install
pipenv shell
```
Next, open a terminal pane for each of the below (using tmux) and run the following commands in PieCentral/shepherd directory.

1:
```
export FLASK_APP=server.py
flask run
```

2:
```
export FLASK_APP=scoreboard_server.py
flask run
```

3:
```
export FLASK_APP=dawn_server.py
flask run
```

4:
```
python3 Shepherd.py
```

5:
```
python3 Sensors.py
```

6:
```
export FLASK_APP=perks_server.py
flask run
```
