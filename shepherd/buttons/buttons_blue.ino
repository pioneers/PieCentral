// buttons for blue side

// constants won't change. They're used here to set pin numbers:
const int buttonPin1 = 10;     // the number of the pushbutton pin
const int buttonPin2 = 9;
const int ledPin =  13;      // the number of the LED pin

// variables will change:
int buttonState1 = 0;         // variable for reading the pushbutton status
int buttonState2 = 0;

bool button1Pressed = false;
bool button2Pressed = false;

void setup() {
  // initialize the LED pin as an output:
  // pinMode(ledPin, OUTPUT);
  // initialize the pushbutton pin as an input:
  pinMode(buttonPin1, INPUT);
  pinMode(buttonPin2, INPUT);
  Serial.begin(9600);
}

void loop() {
  // read the state of the pushbutton value:
  buttonState1 = analogRead(buttonPin1);
  buttonState2 = analogRead(buttonPin2);
  if (buttonState1 >= 1023 && button1Pressed == false) {
    Serial.println("b,1");
    button1Pressed = true;
  }
  if (buttonState2 >= 1023 && button2Pressed == false){
    Serial.println("b,2");
    button2Pressed = true;
  }

  if(button1Pressed && buttonState1 == 0){
    button1Pressed = false;
  }

  if(button2Pressed && buttonState2 == 0){
    button2Pressed = false;
  }

}
