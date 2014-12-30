//PIN Defines
const short STEPPER_DIRECTION_PIN = 8;
const short STEPPER_STEP_PIN = 9;
const short RX_LED_PIN = 11;
const short DRIP_PIN = 4;
const short FORCE_REVERSE_PIN = 3;
const short EMERGENCY_STOP_PIN = 2;
const short REWIND_AFTER_PRINT_SELECTOR = 7;


//Serial Commands
const int dripOnCommand = 49;
const int dripOffCommand = 48;
const int layerStartCommand = 83;
const int layerEndCommand = 69;
const int printCompleteCommand = 77;

//Constants -- THESE CAN BE CHANGED
const int minStepperMicroSeconds = 2000;
const int maxForwardDripSpeed = 1;
const int maxReverseDripSpeed = 1;
const bool emulateDripsInReverse = false;
const int stepperSteps = 200;
const int berrings = 3;
const int stepsPerDrip = 200;
const int dripTimems = 5;

// Enviroment
long steps = 0;
int incommingByte = 0;
bool dripper_on = false;
bool dripper_reverse = false;
long lastCommand = 0;
bool stopped = false;
int inDripTime = 0;


void setup() {
  pinMode(STEPPER_DIRECTION_PIN, OUTPUT);
  digitalWrite(STEPPER_DIRECTION_PIN,LOW);
  pinMode(STEPPER_STEP_PIN, OUTPUT);
  digitalWrite(STEPPER_STEP_PIN,LOW);
  pinMode(RX_LED_PIN, OUTPUT);
  digitalWrite(RX_LED_PIN,LOW);
  pinMode(DRIP_PIN, OUTPUT);
  digitalWrite(DRIP_PIN,HIGH);

  pinMode(FORCE_REVERSE_PIN, INPUT);
  pinMode(EMERGENCY_STOP_PIN, INPUT);
  pinMode(REWIND_AFTER_PRINT_SELECTOR, INPUT);

  attachInterrupt(0, emergencyStop, LOW);
  
  Serial.begin(115200);
}

void drip_forward(){
  digitalWrite(STEPPER_DIRECTION_PIN, HIGH);
  digitalWrite(STEPPER_STEP_PIN, HIGH);
  delayMicroseconds(minStepperMicroSeconds);
  digitalWrite(STEPPER_STEP_PIN, LOW);
  delayMicroseconds(minStepperMicroSeconds);
  steps++;
}

void drip_reverse(){
  digitalWrite(STEPPER_DIRECTION_PIN, LOW);
  digitalWrite(STEPPER_STEP_PIN, HIGH);
  delayMicroseconds(minStepperMicroSeconds);
  digitalWrite(STEPPER_STEP_PIN, LOW);
  delayMicroseconds(minStepperMicroSeconds);
  steps--;
}

void drip() {
  if (steps % stepsPerDrip == 0){
     digitalWrite(DRIP_PIN, LOW);
     delay(dripTimems);
     digitalWrite(DRIP_PIN, HIGH);
     delay(dripTimems);
  }
}

void emergencyStop(){
  if (stopped){
    Serial.println("EMERGENCY STOP -- RESUMED");
    stopped = false;
  } else {
    Serial.println("EMERGENCY STOP");
    stopped = true;
  }
}

void processSerial(){
  if (Serial.available() > 0) {
    incommingByte = Serial.read();
    digitalWrite(RX_LED_PIN, HIGH);
  } else {
    incommingByte = ' ';
    digitalWrite(RX_LED_PIN, LOW);
  }
  if (incommingByte == dripOnCommand) {
    Serial.println("DRIPPING");
    dripper_reverse = false;
    dripper_on = true;
  } else if (incommingByte == dripOffCommand) {
    Serial.println("STOPPED DRIPPING");
    dripper_on = false;
  } else if (incommingByte == 'D') {
    Serial.println("OK");
  }
}

void loop() {
  processSerial();
  if (digitalRead(FORCE_REVERSE_PIN) == LOW){
    dripper_on = false;
    dripper_reverse = true;
  }

  if (dripper_on && !stopped){
      drip_forward();
  } else if (dripper_reverse && !stopped) {
    if (steps > 0){
      drip_reverse();
    }
  }

  drip();
}
