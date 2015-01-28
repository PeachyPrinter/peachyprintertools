#include <pb_encode.h>
#include <pb_decode.h>
#include "serialio.h"


#include <string>

static const short DATA_PIN = 6;

void setup() {
  Serial.begin(115200);
  SerialUSB.begin(2);
  pinMode(DATA_PIN, OUTPUT);
  digitalWrite(DATA_PIN, LOW);
  Serial.println("SETUP");
}

void loop() {
    serialio_feed();
}