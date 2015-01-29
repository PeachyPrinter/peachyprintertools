#include <pb_encode.h>
#include <pb_decode.h>
#include "messages.pb.h"
#include "serialio.h"


#include <string>

#define HEADER 0x40
#define FOOTER 0x41
#define ESCAPE_CHAR 0x42

static const short DATA_PIN = 6;
static const short SEND_PIN = 5;

short BYTE_PIN_0 = 22;
short BYTE_PIN_1 = 23;
short BYTE_PIN_2 = 24;
short BYTE_PIN_3 = 25;
short BYTE_PIN_4 = 26;
short BYTE_PIN_5 = 27;
short BYTE_PIN_6 = 28;
short BYTE_PIN_7 = 29;
short BYTE_PIN_8 = 30;
short BYTE_PIN_9 = 31;
short BYTE_PIN_A = 32;
short BYTE_PIN_B = 33;
short BYTE_PIN_C = 34;
short BYTE_PIN_D = 35;
short BYTE_PIN_E = 36;
short BYTE_PIN_F = 37;

short bits[] = {BYTE_PIN_0, BYTE_PIN_1, BYTE_PIN_2, BYTE_PIN_3, BYTE_PIN_4, BYTE_PIN_5, BYTE_PIN_6, BYTE_PIN_7, BYTE_PIN_9, BYTE_PIN_9, BYTE_PIN_A, BYTE_PIN_B, BYTE_PIN_C, BYTE_PIN_D, BYTE_PIN_E, BYTE_PIN_F};

uint8_t buffer[128];
size_t message_length;
bool status;
unsigned int drip_index = 0;

void setup() {
  Serial.begin(115200);
  SerialUSB.begin(2);
  pinMode(DATA_PIN, OUTPUT);
  digitalWrite(DATA_PIN, LOW);
  pinMode(SEND_PIN, OUTPUT);
  digitalWrite(SEND_PIN, LOW);
  for(int idx = 0 ; idx < 16; idx++){
    pinMode(bits[idx], OUTPUT);
    digitalWrite(bits[idx], HIGH);
  }


  Serial.println("SETUP");
}

void show_index(){
  for(int idx = 0 ; idx < 16; idx++){
    bool bit = (drip_index >> idx) & 1;
    digitalWrite(bits[idx], !bit);
  }
  Serial.println();
}

void loop() {
    // serialio_feed();
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
    drip_index++;
    show_index();
}
