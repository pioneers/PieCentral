//var socket = io('http://192.31.105.220:5500');

const BLUE = 1;
const GOLD = 0;
const NONE = 2;

const DONE = 0;
const AUTO = 1;
const TELEOP = 2;

const stageTimerID = "stage-timer";
const matchNumberID = "match-number";
const timerIDs = [["recipe-timer-G1", "recipe-timer-G2", "recipe-timer-G3", "recipe-timer-G4"], ["recipe-timer-B1", "recipe-timer-B2", "recipe-timer-B3", "recipe-timer-B4"]];
const nameIDs = ["recipe-name-1", "recipe-name-2", "recipe-name-3", "recipe-name-4"];
const scoreIDs = ["gold-score", "blue-score"];
const ratIDs = ["number-rats-gold", "number-rats-blue"];
const crownIDs = ["gold-crown", "blue-crown"];
const healthIDs = ["gold-health-inspector", "blue-health-inspector"];
const penaltyIDs = ["gold-penalty", "blue-penalty"];
const teamNameIDs = [["gold-name-1", "gold-name-2"], ["blue-name-1", "blue-name-2"]];
const teamNumberIDs = [["gold-number-1", "gold-number-2"], ["blue-number-1", "blue-number-2"]];
const PENALTY_LENGTH = 5;
const GAME_OVER_TIME = 90;
const WARNING_INTERVAL = 10;

var teamNames = [["", ""], ["", ""]];
var teamNumbers = [[1, 2], [3, 4]];

var autoTime = 30;
var autoOffset = 0;
var times = [[0, 0, 0, 0], [0, 0, 0, 0]]; // gold timers, then blue timers, in seconds
var displayTimes = [["0:00", "0:00", "0:00", "0:00"], ["0:00", "0:00", "0:00", "0:00"]];
var recipeNames = ["", "", "", ""];
var offset = [[0, 0, 0, 0], [0, 0, 0, 0]];
var finished = [[false, false, false, false], [false, false, false, false]];

var matchStarted = DONE;
var current = [0, 0];
var haveSpawned = 0;

var regularRats = [3, 3]; // doesn't include king rat
var rats = [3, 3]; // includes king rat
var kingRat = NONE;
var showHealth = [false, false];

var penalties = [0, 0];
var penaltyTimes = ["0:00", "0:00"];

const DONE_COLOR = 'gray';
const RUN_COLOR = 'black';
const WARNING_COLOR = 'rgb(238, 118, 0)';
const STOP_COLOR = 'red';

// socket
/*
socket.on('connect', function(data) {
  socket.emit('join', 'scoreboard');
  console.log('connected');
});

socket.on('teams', function(match_info) {
  setTeamName(JSON.parse(match_info).g1name, GOLD, 0);
  setTeamNumber(JSON.parse(match_info).g1num, GOLD, 0);
  setTeamName(JSON.parse(match_info).g2name, GOLD, 1);
  setTeamNumber(JSON.parse(match_info).g2num, GOLD, 1);
  setTeamName(JSON.parse(match_info).b1name, BLUE, 0);
  setTeamNumber(JSON.parse(match_info).b1num, BLUE, 0);
  setTeamName(JSON.parse(match_info).b2name, BLUE, 1);
  setTeamNumber(JSON.parse(match_info).b2num, BLUE, 1);
  matchNumber(JSON.parse(match_info).match_number);
})

socket.on('reset_match', function() {
  resetMatch();
})

socket.on('start_match', function() {
  console.log('starting');
  startAuto();
})

socket.on('start_teleop', function(recipeName) {
  startTeleop(JSON.parse(recipeName).name);
})

socket.on('spawn', function(recipeName) {
  spawn(JSON.parse(recipeName).name);
})

socket.on('finish_recipe', function(color) {
  finishRecipe(JSON.parse(color).color);
})

socket.on('move_rat', function(color) {
  moveRat(JSON.parse(color).color);
})

socket.on('move_king_rat', function(color) {
  moveKingRat(JSON.parse(color).color);
})

socket.on('health', function() {
  startHealth();
})

socket.on('penalty', function(color) {
  addPenalty(JSON.parse(color).color);
})
*/
// pre-match

// get rid of the next two

function teamName(color, team) {
  setTeamName(document.getElementById("textField").value, color, team);
}

function teamNumber(color, team) {
  setTeamNumber(document.getElementById("textField").value, color, team);
}

function setTeamName(name, color, team) { // team is 0 or 1
  teamNames[color][team] = name;
  document.getElementById(teamNameIDs[color][team]).innerHTML = name;
}

function setTeamNumber(number, color, team) {
  teamNumbers[color][team] = number;
  var n = number < 10 ? ("0" + number.toString()) : number.toString();
  document.getElementById(teamNumberIDs[color][team]).innerHTML = n;
}

function matchNumber(number) {
  document.getElementById(matchNumberID).innerHTML = "MATCH " + number.toString();
}

// need penalty counter

function render() {
  document.getElementById
  document.getElementById(stageTimerID).innerHTML = intToTime(autoTime);
  setDisplayTimes();
  var fin = [0, 0];
  for (j = 0; j < times[0].length; j++) {
    for (i = 0; i < times.length; i++) {
      // by team/recipe
      document.getElementById(timerIDs[i][j]).innerHTML = displayTimes[i][j];
      var color = RUN_COLOR;
      if (finished[i][j]) {
        color = DONE_COLOR;
      } else if(times[i][j] >= GAME_OVER_TIME) {
        color = STOP_COLOR;
      } else if(times[i][j] >= GAME_OVER_TIME - WARNING_INTERVAL) {
        color = WARNING_COLOR;
      }
      document.getElementById(timerIDs[i][j]).style.color = color;
      document.getElementById(timerIDs[i][j]).style.visibility = j < haveSpawned ? "visible" : "hidden";
      if (finished[i][j]) {
        fin[i] += 1;
      }
    }
    // by recipe
    document.getElementById(nameIDs[j]).style.color = (finished[GOLD][j] && finished[BLUE][j]) ? DONE_COLOR : RUN_COLOR;
    document.getElementById(nameIDs[j]).style.visibility = j < haveSpawned ? "visible" : "hidden";
    document.getElementById(nameIDs[j]).innerHTML = recipeNames[j];
  }

  rats = [regularRats[GOLD], regularRats[BLUE]];
  if (kingRat != NONE) {
    rats[kingRat] += 2;
  }

  for (i = 0; i < times.length; i++) {
    // by team
    document.getElementById(scoreIDs[i]).innerHTML = fin[i];
    document.getElementById(ratIDs[i]).innerHTML = rats[i];
    document.getElementById(crownIDs[i]).style.visibility = kingRat == i ? "visible" : "hidden";
    document.getElementById(healthIDs[i]).style.visibility = showHealth[i] ? "visible" : "hidden";
    document.getElementById(penaltyIDs[i]).innerHTML = penaltyTimes[i];
  }

  document.getElementById("stage").innerHTML = matchStarted == DONE ? "NOT STARTED" : (matchStarted == AUTO ? "AUTONOMOUS" : "TELEOP");
}

// timers/game flow

// set all times
function setDisplayTimes() {
  for (i = 0; i < times.length; i++) {
    for (j = 0; j < times[0].length; j++) {
      displayTimes[i][j] = intToTime(times[i][j]);
    }
    penaltyTimes[i] = intToTime(penalties[i] * 5);
  }
}

function intToTime(i) {
  var m = Math.floor(i / 60);
  var s = i % 60;
  var sString = s < 10 ? ("0" + s.toString()) : s.toString();
  return m.toString() + ":" + sString;
}

function resetMatch() {
  autoTime = 30;
  times = [[0, 0, 0, 0], [0, 0, 0, 0]]; // gold timers, then blue timers, in seconds
  displayTimes = [["0:00", "0:00", "0:00", "0:00"], ["0:00", "0:00", "0:00", "0:00"]];
  recipeNames = ["", "", "", ""];
  offset = [[0, 0, 0, 0], [0, 0, 0, 0]];
  finished = [[false, false, false, false], [false, false, false, false]];

  matchStarted = DONE;
  current = [0, 0];
  haveSpawned = 0;

  regularRats = [3, 3]; // doesn't include king rat
  rats = [3, 3]; // includes king rat
  kingRat = NONE;
  showHealth = [false, false];

  penalties = [0, 0];
  penaltyTimes = ["0:00", "0:00"];

  render();
}

function reset(color, number) { // blue is 0, gold is 1
  times[color][number] = 0;
  render();
}

function start(color, number) {
  offset[color][number] = Date.now();
}

function beginRecipe() {
  start(GOLD, haveSpawned - 1);
  start(BLUE, haveSpawned - 1);
}

function finishRecipe(color) {
  if (!finished[color][current[color]]) {
    finished[color][current[color]] = true;
  }
}

function update() {
  if (matchStarted == AUTO) {
    autoTime = 30 - Math.floor((Date.now() - autoOffset) / 1000);
    if (autoTime < 0 && matchStarted == AUTO) {
      autoTime = 0;
    }
  } else if (matchStarted == TELEOP) {
    for (i = 0; i < times.length; i++) {
      if (finished[i][current[i]] && (haveSpawned - 1 > current[i])) {
        current[i] += 1;
      }
      for (j = 0; j < times[0].length; j++) {
        if (!finished[i][j] && (j < haveSpawned)) {
          times[i][j] = Math.floor((Date.now() - offset[i][j]) / 1000);
          if (times[i][j] >= GAME_OVER_TIME) {
            matchStarted = DONE;
          }
        }
      }
    }
  }
  render();
  if (matchStarted != DONE) {
    t = setTimeout(update, 20);
  }
}

// todo: delete this

function sp() {
  spawn(document.getElementById("textField").value);
}

function spawn(recipeName) {
  haveSpawned += 1;
  recipeNames[haveSpawned - 1] = recipeName;
  beginRecipe();
}

function startAuto() {
  matchStarted = AUTO;
  autoOffset = Date.now();
  update();
}

function startTeleop(recipeName) {
  if (matchStarted == AUTO) {
    spawn(recipeName);
    matchStarted = TELEOP;
  }
}

function stopMatch() {
  matchStarted = DONE;
}

function startHealth() {
  setTimeout(function(){ return stopHealth(GOLD); }, rats[GOLD] * 1000);
  showHealth[GOLD] = true;
  setTimeout(function(){ return stopHealth(BLUE); }, rats[BLUE] * 1000);
  showHealth[BLUE] = true;
}

function stopHealth(color) {
  showHealth[color] = false;
}

// penalty

function addPenalty(color) {
  penalties[color] += 1;
}

// rats

function moveRat(toTeam) {
  if (regularRats[(toTeam + 1) % 2] > 0) {
    regularRats[toTeam] += 1;
    regularRats[(toTeam + 1) % 2] -= 1;
  }
}

function moveKingRat(toTeam) {
  kingRat = toTeam;
}
