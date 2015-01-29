#include <pb_encode.h>
#include <pb_decode.h>
#include "messages.pb.h"
#include "serialio.h"


#include <string>

#define HEADER 0x40
#define FOOTER 0x41
#define ESCAPE_CHAR 0x42

static const short DATA_PIN = 6;
uint8_t buffer[128];
size_t message_length;
bool status;
unsigned int drip_index = 0;

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
    dr.drips = drip_index;
    status = pb_encode(&stream, DripRecorded_fields, &dr);
    message_length = stream.bytes_written;
    if (!status) {
        Serial.print("Encoding failed: ");
        Serial.println(PB_GET_ERROR(&stream));
    } else {
        SerialUSB.write(HEADER);
        SerialUSB.write(3);
        for(int idx=0; idx < message_length; idx++){
          if (buffer[idx] == HEADER or buffer[idx] == FOOTER or buffer[idx] ==  ESCAPE_CHAR){
            SerialUSB.write(ESCAPE_CHAR);
            SerialUSB.write(~buffer[idx]);
          } else {
            SerialUSB.write(buffer[idx]);
          }
        }
        SerialUSB.write(FOOTER);
    }
    delay(100);
    drip_index++;
}