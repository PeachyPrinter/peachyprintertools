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

//Constants
const int minStepperMicroSeconds = 75;
const int maxForwardDripSpeed = 1;
const int maxReverseDripSpeed = 1;
const bool emulateDripsInReverse = false;
const int stepperSteps = 200;
const int berrings = 3;
const int steps_per_drip = 3;

// Enviroment
int drips = 0;
int incommingByte = 0;
bool dripper_on = false;
long lastCommand = 0;


void setup() {
  
  pinMode(STEPPER_DIRECTION_PIN, OUTPUT);
  pinMode(STEPPER_STEP_PIN, OUTPUT);
  pinMode(RX_LED_PIN, OUTPUT);
  pinMode(DRIP_PIN, OUTPUT);

  pinMode(FORCE_REVERSE_PIN, INPUT);
  pinMode(EMERGENCY_STOP_PIN, INPUT);
  pinMode(REWIND_AFTER_PRINT_SELECTOR, INPUT);

  //attachInterrupt(0, emergencyStop, RISING);
  
  Serial.begin(115200);
}

void drip_forward(){
  digitalWrite(STEPPER_DIRECTION_PIN, HIGH);
  digitalWrite(STEPPER_STEP_PIN, HIGH);
  delayMicroseconds(minStepperMicroSeconds);
  digitalWrite(STEPPER_STEP_PIN, LOW);
  delayMicroseconds(minStepperMicroSeconds);
  drips++;
}

void drip_reverse(){
  digitalWrite(STEPPER_DIRECTION_PIN, LOW);
  digitalWrite(STEPPER_STEP_PIN, HIGH);
  delayMicroseconds(minStepperMicroSeconds);
  digitalWrite(STEPPER_STEP_PIN, LOW);
  delayMicroseconds(minStepperMicroSeconds);
  drips--;
}

void emergencyStop(){
  Serial.write("EMERGENCY STOP\n");
  while (true){
    delay(1000);
  }
}


void loop() {
  if (Serial.available() > 0) {
    incommingByte = Serial.read();


  } else {
    incommingByte = ' ';
  }
  
  if (incommingByte == dripOnCommand) {
    Serial.write("DRIPPING\n");
    dripper_on = true;
  } else if (incommingByte == dripOffCommand) {
    Serial.write("STOPPED DRIPPING\n");
    dripper_on = false;
  } else if (incommingByte == 'D') {
    Serial.write("OK\n");
  }

  if (dripper_on){
    drip_forward();
  }

}
