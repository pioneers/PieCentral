#include <SevenSeg.h>
SevenSeg disp(13, 12, 11, 10, 9, 8, 7);
const int numOfDigits = 4;
const int numOfButtons = 5;
//const int numGoals = 5;

int digitPins[numOfDigits] = {6, 5, 4, 3};
//char bidGoals[numGoals] = {'a', 'b', 'c', 'd', 'e'}; //for gold side
//char bidGoals[numGoals] = {'e', 'd', 'c', 'b', 'a'}; //for blue side

//int switchIn = 2;
//int prevSwitchVal = 0;
//int switchVal = 0;
boolean buttonWasPressed[numOfButtons] = {false, false, false, false, false};

int buttonPins[numOfButtons] = {22, 23, 24, 25, 26};
const int blueRatPin = 22;
const int blueKingPin = 23;
const int goldKingPin = 25;
const int goldRatPin = 26;

//int submitButton = 27;

int redPins[numOfButtons] = {51, 50, 44, 38, 32};
int greenPins[numOfButtons] = {53, 48, 42, 36, 30};
int bluePins[numOfButtons] = {52, 46, 40, 34, 28};
int blueRatLED[3] = {51, 53, 52};
int blueKingLED[3] = {50, 48, 46};
int goldKingLED[3] = {38, 36, 34};
int goldRatLED[3] = {32, 30, 28};
int blueLED[3] = {0, 0, 255};
int goldLED[3] = {212, 175, 55};
//blue rgb: 0, 0, 255
//gold RGB: 212, 175, 55

//each side starts with 3 rats, king starts in the middle
int blueRats = 3;
int goldRats = 3;
typedef enum {
  GOLD, //0
  MID,  //1
  BLUE, //2
} kingRat;

kingRat kRPos = MID;

//int goalOwner[numGoals] = {'n', 'n', 'n', 'n', 'n'};
//int biddingPrice[numGoals] = {0, 0, 0, 0, 0};
// ' ' = no owner, 'b' = blue, 'g' = goal
//int myScore = 0; 
//char myTeam = 'b'; //change this var for opposite team
//char myEnemy = 'g';

char pyInpStr[1023];
int inpStrIndex = 0;
char blank = ' ';
boolean pyInpComplete = false;
char *pyInpBuffer = NULL;

int heartCount = 0;

void setup() {
  Serial.begin(9600);
  disp.setDigitPins(numOfDigits, digitPins);

  //pinMode(submitButton, INPUT);
  for (int ii = 0; ii < numOfButtons; ii++) {
    pinMode(buttonPins[ii], INPUT);
    pinMode(redPins[ii], OUTPUT);
    pinMode(bluePins[ii], OUTPUT);
    pinMode(greenPins[ii], OUTPUT);
  }
  writeLED(blueRatLED, blueLED);
  writeLED(blueKingLED, blueLED);
  writeLED(goldRatLED, goldLED);
  writeLED(goldKingLED, goldLED);
}

//TODO: fix led colors (low priority)
//TODO: Enable box reset through Shepherd (high priority)
void loop() {
  heartCount += 1;
  if (heartCount % 100 == 0){
    Serial.println("rb;hb"); //ratbox
    //Serial.println("bsb;hb"); //identifier for blue side
    // Serial.println("bsg;hb"); //identifier for gold side
  }
  
  //reset stuff
  if (pyInpComplete) {    
    pyInpBuffer = strtok(pyInpStr, ";");
    
    if (pyInpBuffer != NULL){
      if (strcmp(pyInpBuffer, "rst") == 0) {
        //reset display and counters
        blueRats = 3;
        goldRats = 3;
        kRPos = MID;
      }
      /* if(strcmp(pyInpBuffer, "bp") == 0){
        // Serial.println("received bidding price info");
        int index = 0; 
        pyInpBuffer = strtok(NULL, ";");
        while(pyInpBuffer != NULL and index < numGoals){
          biddingPrice[index] = atoi(pyInpBuffer);          
          pyInpBuffer = strtok(NULL, ";");
          index++;          
        }
      } else if (strcmp(pyInpBuffer, "go") == 0){
        // Serial.println("received goal owner info");
        int index = 0; 
        pyInpBuffer = strtok(NULL, ";");
        while(pyInpBuffer != NULL and index < numGoals){        
          goalOwner[index] = *pyInpBuffer;          
          pyInpBuffer = strtok(NULL, ";");
          index++;
        }
      } else if (strcmp(pyInpBuffer, "ts") == 0){
//        Serial.println("received team score info");
        pyInpBuffer = strtok(NULL, ";");
             
        if (pyInpBuffer == NULL){
          // Serial.println("received null for team score, error");
        } else {
          myScore = atoi(pyInpBuffer);        
        }
      } else if (strcmp(pyInpBuffer, "cstatus") == 0){
        // Serial.println("received code + goal status");
        pyInpBuffer = strtok(NULL, ";");
        if (pyInpBuffer == NULL){
          // Serial.println("null for code + goal status");
        } else {
          cstatus = atoi(pyInpBuffer);
        }
      } */
    }
    pyInpStr[0] = '\0';
    pyInpComplete = false;
  }
  
  for (int i = 0; i < numOfButtons; i++) {
    if (i == 2) { //unused middle button
      continue;
    }
    int butt = buttonPressed(i);
    switch (butt) {
      case 0: //blue rat
        if (blueRats < 6) {
          blueRats++;
          goldRats--;
        }
        break;
      case 1: //blue king
        kRPos = BLUE;
        break;
      case 3: //gold king
        kRPos = GOLD;
        break;
      case 4: //gold rat
        if (goldRats < 6) {
          blueRats--;
          goldRats++;
        }
        break;
      default:
        break;
    }
  }

  //serial message indicating rat counts for Shepherd
  //rs = rat status
  String rat_status = "rs;" + String(blueRats) + ";" + String(goldRats) + ";" + kRPos + ";";
  Serial.println(rat_status);
  
  //code for 4dig 7seg display here
  //blue rat count
  disp.changeDigit(0);
  disp.writeDigit(blueRats);
  //king rat blue
  disp.changeDigit(1);
  if (kRPos == BLUE) {
    disp.writeDigit('-');
  } else {
    disp.writeDigit(' ');
  }
  //king rat gold
  disp.changeDigit(2);
  if (kRPos == GOLD) {
    disp.writeDigit('-');
  } else {
    disp.writeDigit(' ');
  }
  //gold rat count
  disp.changeDigit(3);
  disp.writeDigit(goldRats);

}

void serialEvent() {
  while (Serial.available()) {
    char inChar[1];
    Serial.readBytes(inChar, 1);
    if (inChar[0] == '\n'){
      pyInpStr[inpStrIndex] = '\0';
      pyInpComplete = true;
      inpStrIndex = 0;      
    } else {
      pyInpStr[inpStrIndex] = inChar[0];
      inpStrIndex++;
    }
    
  }
}

//precondition: led and rbg array is 3 elements long
void writeLED(int led[], int rgb[]) {
  for (int l = 0; l < 3; l++) {
    analogWrite(led[l], rgb[l]);
  }
}

// detect if a button was pressed
// returns number that the button represents.
int buttonPressed(int button) {
  int buttonVal = digitalRead(buttonPins[button]);
  if (!buttonVal && buttonWasPressed[button]) {
    //button released
    buttonWasPressed[button] = false;
    return button;
  } else if (buttonVal && !buttonWasPressed[button]) {
    //button initially pressed down
    buttonWasPressed[button] = true;
  }
  return -1;
}
