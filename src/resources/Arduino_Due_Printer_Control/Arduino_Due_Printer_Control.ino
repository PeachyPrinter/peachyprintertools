/*
This is an experimental work in progress. Peachy Printer Assumes no responsibility for its use.
It is not recommened that this is uploaded to a arduino at this time.
*/

#include "JAudio.h"

static const short LASER_PIN = 2;
static const short TEST_PIN = 11;
static const short RUN_PIN = 12;
static const short MAX_VOLUME = 1024;
static const short MAX_SHORT = 32767;
static const float pi = 3.14159265359;
int sample_rate = 22050;
short channels = 2;
short bits = 16; //Audio library downsamples

bool running = false;
const int buffer_size_millis = 100;
// const int buffer_size_samples = channels * sample_rate * buffer_size_millis / 1000 /2;
const int buffer_size_samples = 2048;



void print_settings() {
 Serial.print("Sample Rate:           ");
 Serial.print(sample_rate);
 Serial.print("\nChannels:            ");
 Serial.print(channels);
 Serial.print("\nBuffer Milliseconds: ");
 Serial.print(buffer_size_millis);
 Serial.print("\nBuffer Samples:      ");
 Serial.print(buffer_size_samples);
 Serial.print("\n");
  }

void writeBuffer(short *buffer, int samples){
  Audio.prepare(buffer, samples, MAX_VOLUME);
  Audio.write(buffer, samples);
}

void setup() {
  pinMode(LASER_PIN, OUTPUT);
  pinMode(RUN_PIN, INPUT);
  pinMode(TEST_PIN, INPUT);
  Serial.begin(115200);
  SerialUSB.begin(2);
  Audio.begin(sample_rate * channels, buffer_size_millis);
}

void loop() {
  if (digitalRead(TEST_PIN) == HIGH) {
      print_settings();
      delay(500);
  }
  short buffer[buffer_size_samples]; 
  int buffer_location = 0;
  while (SerialUSB.available() > 6) {
    short left,right;
    left = SerialUSB.read();
    left |= SerialUSB.read() << 8;
    right = SerialUSB.read();
    right |= SerialUSB.read() << 8;

    buffer[buffer_location] = left;
    buffer_location++;
    buffer[buffer_location] = right;
    buffer_location++;

    if (buffer_location >= buffer_size_samples){
      writeBuffer(buffer,buffer_location);
      buffer_location = 0;
    }
  }
  if (buffer_location > 0) {
    writeBuffer(buffer,buffer_location);
  }
}
