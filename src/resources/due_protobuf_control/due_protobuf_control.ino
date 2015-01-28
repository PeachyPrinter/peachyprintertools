#include <pb_encode.h>
#include <pb_decode.h>
#include "serialio.h"


#include <string>

static const short DATA_PIN = 6;
uint8_t buffer[128];
size_t message_length;
bool status;
int index = 0;


void setup() {
  Serial.begin(115200);
  SerialUSB.begin(2);
  pinMode(DATA_PIN, OUTPUT);
  digitalWrite(DATA_PIN, LOW);
  Serial.println("SETUP");
}

void loop() {
    serialio_feed();
    DripRecorded dr;
    pb_ostream_t stream = pb_ostream_from_buffer(buffer, sizeof(buffer));
    dr.drips = index;
    status = pb_encode(&stream, SimpleMessage_fields, &message);
    message_length = stream.bytes_written;
    if (!status) {
        Serial.println("Encoding failed: %s\n", PB_GET_ERROR(&stream));
        return 1;
    } else {
        
    }

}