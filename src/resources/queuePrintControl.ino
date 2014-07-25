//Outputs
const int pumpForward   =  3;
const int pumpReverse   =  4;
const int belt          =  6;
const int dripShort     =  5;
const int speaker       =  7;

//Inputs
const int pumpInterupted    =  8;
const int tankEmpty         =  9;
const int tankFull          = 10;
const int bottomRoller      = 11;
const int topRoller         = 12;
const int testButton        = 13;

const int initializeButton  = 2;

// Serial Communication Constants
const int helloCommand = 68; // D
const int dripOnCommand = 69; // E
const int dripOffCommand = 70; // F
const int layerStartCommand = 83; // S
const int layerEndCommand = 84; // T
const int printCompleteCommand = 90;//Z


int incommingByte = 0;
bool testInProgress = false;
bool pumpState = true;

void setup() {
  pinMode(pumpForward, OUTPUT);      
  pinMode(pumpReverse, OUTPUT);
  pinMode(belt, OUTPUT);
  pinMode(dripShort, OUTPUT);
  pinMode(speaker, OUTPUT);

  pinMode(pumpInterupted, INPUT);
  pinMode(tankEmpty, INPUT);
  pinMode(tankFull, INPUT);
  pinMode(bottomRoller, INPUT);
  pinMode(topRoller, INPUT);
  pinMode(testButton, INPUT);
  pinMode(initializeButton, INPUT);

  Serial.begin(9600);
}

void happytone() {
  tone(speaker, 440, 250);
  delay(250);
  tone(speaker, 880, 250);
  delay(250);
}

void alarmtone() {
  for (int i = 440; i < 880; i += 10){
    tone(speaker, i, 25);
    delay(25);
  }
}

void pumpFill() {
  digitalWrite(pumpReverse, LOW);
  digitalWrite(pumpForward, HIGH);
}

void pumpStop() {
  digitalWrite(pumpReverse, HIGH);
  digitalWrite(pumpForward, HIGH);
}

void pumpEmpty() {
  digitalWrite(pumpForward, LOW);
  digitalWrite(pumpReverse, HIGH);
}

void emulateDrip() {
  digitalWrite(dripShort, HIGH);
  delay(10);
  digitalWrite(dripShort, LOW);
}

void converyerAdvance() {
  digitalWrite(belt, HIGH);
}

void converyerStop() {
  digitalWrite(belt, LOW);
}

void aTest() {
  Serial.println("Testing:Alarm");
  alarmtone();
  Serial.println("Testing:Tone");
  happytone();
  Serial.println("Testing:Pump Fill");
  pumpFill();
  delay(1000);
  Serial.println("Testing:Pump Empty");
  pumpEmpty();
  delay(1000);
  Serial.println("Testing:Pump Stop");
  pumpStop();
  Serial.println("Testing:Drip Emulation");
  emulateDrip();
  Serial.println("Testing: Converyer Advance");
  converyerAdvance();
  delay(1000);
  Serial.println("Testing: Converyer Stop");
  converyerStop();
  complete();
}

void initializeBelt(){
  while(digitalRead(bottomRoller) == LOW)
    converyerAdvance();
  converyerStop();
}

void advanceBelt(int turns) {
  bool inTurn = true;
  converyerAdvance();
  while (turns > 0) {
    if (digitalRead(bottomRoller) == LOW)
      inTurn = false;
    if (digitalRead(bottomRoller) == HIGH && inTurn == false) {
      inTurn = true;
      turns--;
    }
  }
  converyerStop();
}

void complete(){
  advanceBelt(4);
  while(digitalRead(tankEmpty) == LOW)
    pumpEmpty();
  pumpStop();
  happytone();
}

void checkPump() {
   if (digitalRead(pumpInterupted) == HIGH){
      if (pumpState != true) {
        pumpState = true;
        Serial.println("Pumped");
      }
    }
  if (digitalRead(pumpInterupted) == LOW) {
    if (pumpState != false) {
        pumpState = false;
        Serial.println("UnPumped");
      }
    }
}

void checkFull() {
  if (digitalRead(tankFull) == HIGH){
    Serial.println("TankFull");
    alarmtone();
  }
}

void checkTestMode(){
  if (digitalRead(testButton) == HIGH){
    if (!testInProgress) {
      testInProgress = true;
      Serial.println("Testing");
      aTest();
    }
  }
  if (digitalRead(testButton) == LOW){
      testInProgress = false;
    }
}

void checkSerial(){
if (Serial.available() > 0) {
    incommingByte = Serial.read();
  }
  
  if (incommingByte == dripOnCommand) {
    pumpFill();
  } else if (incommingByte == dripOffCommand) {
    pumpStop();
  } else if (incommingByte == layerStartCommand) {
    // Do nothing
  } else if (incommingByte == layerEndCommand) {
    // Do nothing
  } else if (incommingByte == helloCommand) {
    Serial.write("OK\n");
    incommingByte = 0;
  }else if (incommingByte == printCompleteCommand) {
    complete();
    incommingByte = 0;
  }
}


void loop()
{ 
  if (!testInProgress) {
    checkPump();
    checkFull();
    checkTestMode();

  }

  if (digitalRead(initializeButton) == HIGH){
      Serial.println("Initializing Belt");
      initializeBelt();
    }

}