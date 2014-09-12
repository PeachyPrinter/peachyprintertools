//Outputs
const int pumpIn        =  3;
const int pumpOut       =  4;
const int belt          =  6;
const int dripShort     =  5;
const int speaker       =  7;
const int shutter       =  14;
const int emptyVoltagePin   = 10;

//Inputs
const int pumpInterupted    =  8;
const int emptyCheckPin     =  9;
const int topRoller         = 11;
const int printDisk1Click   = 12;
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
int shutterOn=0;

void setup() {
  pinMode(shutter, OUTPUT);
  pinMode(pumpOut, OUTPUT);
  pinMode(pumpIn, OUTPUT);
  pinMode(belt, OUTPUT);
  pinMode(dripShort, OUTPUT);
  pinMode(speaker, OUTPUT);
  pinMode(emptyVoltagePin, OUTPUT);  
  pinMode(emptyVoltagePin, OUTPUT);  
  digitalWrite(emptyVoltagePin,LOW);

  pinMode(pumpInterupted, INPUT);
  pinMode(printDisk1Click, INPUT);    
  pinMode(emptyCheckPin, INPUT); 
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
  digitalWrite(pumpOut, LOW);
  digitalWrite(pumpIn, HIGH);
}

void pumpStop() {
  digitalWrite(pumpOut, LOW);
  digitalWrite(pumpIn, LOW);
}

void pumpEmpty() {
  digitalWrite(pumpIn, LOW);
  digitalWrite(pumpOut, HIGH);
}

void emulateDrip() {
  digitalWrite(dripShort, HIGH);
  delay(10);
  digitalWrite(dripShort, LOW);
}

void conveyerAdvance() {
  digitalWrite(belt, HIGH);
}

void conveyerStop() {
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
  Serial.println("Testing: Conveyer Advance");
  conveyerAdvance();
  delay(1000);
  Serial.println("Testing: Conveyer Stop");
  conveyerStop();
  
  
  PrintSetup();
}

void advanceBelt(int clicks){
  Serial.println("advancing");
  digitalWrite(belt,HIGH);
  while(clicks>0){
    while(digitalRead(printDisk1Click)==HIGH){delay(10);}
    while(digitalRead(printDisk1Click)==LOW){delay(10);}
    while(digitalRead(printDisk1Click)==HIGH){delay(10);}
    clicks--;
    Serial.println("clicks left: ");
    Serial.println(clicks);
  }
  Serial.println("advanced");
  digitalWrite(belt,LOW);
}

void PrintSetup(){
  Serial.println("Setting up for next print");
  Serial.println("Emptying Tank");
  emptyTank(3000);
  Serial.println("Advancing Belt");
  advanceBelt(1);

  Serial.println("Ready to Print");
  happytone();

}

void emptyTank(int CheckInterval){
  boolean empty = false;
  while(empty==false){  
    digitalWrite(emptyVoltagePin,HIGH);
    if (digitalRead(emptyCheckPin)==HIGH){
      Serial.println("not empty");  
      digitalWrite(pumpOut,HIGH);
    }
    else{
      Serial.println("empty");
      empty=true;
      digitalWrite(pumpOut,LOW);
    }
    digitalWrite(emptyVoltagePin,LOW);
    delay(CheckInterval);
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
    shutterStart();
  } else if (incommingByte == layerEndCommand) {
    shutterClose();

  } else if (incommingByte == helloCommand) {
    Serial.write("OK\n");
  }else if (incommingByte == printCompleteCommand) {
    Serial.println("Communication: Recieved Print Complete");
    PrintSetup();
  }
  incommingByte = 0;
}

void shutterStart(){
  if (shutterOn==0){
    digitalWrite(shutter,HIGH);
    shutterOn=2;
  }
  else if (shutterOn<0){
    shutterOn++;
  }
}

int shutterClose(){
  if (shutterOn>1){
    shutterOn--;
  }
  else if (shutterOn==1){
    digitalWrite(shutter,LOW);
    shutterOn = -3;
  }
}

void loop()
{ 
  if (!testInProgress) {
    checkTestMode();
    checkSerial();
  }

  if (digitalRead(initializeButton) == HIGH){
      PrintSetup();
    }
}
