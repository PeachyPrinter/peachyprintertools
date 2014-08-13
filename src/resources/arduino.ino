/*
  Peachy Printer Servo Controlled Dripper
  
  Notes:
     Using LOW for on LED
 */
 
#include <Servo.h> 

Servo valveServo; 

int camera_pin = 8;
int onLed = 4;
int offLed = 3;
int servo = 2;
int servoHi = 1;
int servoLo = 2;
int loPot = A0;
int hiPot = A1;
int testSwitch = 5;
int bufferSize = 500;

int dripOnCommand = 49;
int dripOffCommand = 48;
int layerStartCommand = 83;
int layerEndCommand = 69;

int maxPotValue = 1024;
float servoThrow = 180.0;
int incommingByte = 0;
unsigned long cameraStateOnTime = millis() + 100000l;
unsigned long cameraStateOffTime = millis() + 100000l;


void setup() {                
  pinMode(camera_pin, OUTPUT);
  pinMode(onLed, OUTPUT);
  pinMode(offLed, OUTPUT);
  pinMode(servo, OUTPUT);
  pinMode(testSwitch, INPUT);
  valveServo.attach(servo);
  Serial.begin(9600);
}

int getHighValue(){
  return ((analogRead(hiPot) * servoThrow) + 1) / maxPotValue;
}
  
int getLowValue(){
  return ((analogRead(loPot) * servoThrow) + 1) / maxPotValue;
}

void test() {
  Serial.print("LOW:");
  Serial.print(getLowValue());
  Serial.print("\tHigh:");
  Serial.println(getHighValue());
  dripperOn();
  delay(1000);
  dripperOff();
  delay(100);               // wait for a second
}

void dripperOn(){
    digitalWrite(onLed, LOW);
    digitalWrite(offLed, HIGH);
    valveServo.write(getHighValue());
}

void dripperOff(){
  digitalWrite(onLed, HIGH);
  digitalWrite(offLed, LOW);
  valveServo.write(getLowValue());
}

void camera_on(){
  cameraStateOnTime = millis() + bufferSize;
}

void camera_off(){
  cameraStateOffTime = millis() + bufferSize;
}

void camera_state(){
  if (millis() >=  cameraStateOnTime){
      digitalWrite(camera_pin, HIGH);
      cameraStateOnTime = millis() + 1000000l;
      Serial.println("On");
  } 
  if (millis() >=  cameraStateOffTime){
      digitalWrite(camera_pin, LOW);
      cameraStateOffTime = millis() + 1000000l;
      Serial.println("Off");
    }
}

void run() {
  if (Serial.available() > 0) {
    incommingByte = Serial.read();
  } else {
    incommingByte = ' ';
  }
  
  if (incommingByte == dripOnCommand) {
    dripperOn();
  } else if (incommingByte == dripOffCommand) {
    dripperOff();
  } else if (incommingByte == layerStartCommand) {
    camera_on();
  } else if (incommingByte == layerEndCommand) {
    camera_off();
  } else if (incommingByte == 'D') {
    Serial.write("OK\n");
    incommingByte = 0;
  }
  camera_state();
}

void loop() {
  if (digitalRead(testSwitch) == HIGH) {
    test();
  } else {
    run();
  }

}