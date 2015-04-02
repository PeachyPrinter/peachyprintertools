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

short BYTE_PIN_X0 = 38;
short BYTE_PIN_X1 = 40;
short BYTE_PIN_X2 = 42;
short BYTE_PIN_X3 = 44;
short BYTE_PIN_X4 = 46;
short BYTE_PIN_X5 = 48;
short BYTE_PIN_X6 = 50;
short BYTE_PIN_X7 = 52;

short BYTE_PIN_Y0 = 39;
short BYTE_PIN_Y1 = 41;
short BYTE_PIN_Y2 = 43;
short BYTE_PIN_Y3 = 45;
short BYTE_PIN_Y4 = 47;
short BYTE_PIN_Y5 = 49;
short BYTE_PIN_Y6 = 51;
short BYTE_PIN_Y7 = 53;

short xbits[] = { BYTE_PIN_X0, BYTE_PIN_X1, BYTE_PIN_X2, BYTE_PIN_X3, BYTE_PIN_X4, BYTE_PIN_X5, BYTE_PIN_X6, BYTE_PIN_X7 };
short ybits[] = { BYTE_PIN_Y0, BYTE_PIN_Y1, BYTE_PIN_Y2, BYTE_PIN_Y3, BYTE_PIN_Y4, BYTE_PIN_Y5, BYTE_PIN_Y6, BYTE_PIN_Y7 };

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
  for(int idx = 0 ; idx < 8; idx++){
    pinMode(xbits[idx], OUTPUT);
    pinMode(ybits[idx], OUTPUT);
    digitalWrite(xbits[idx], HIGH);
    digitalWrite(ybits[idx], HIGH);
  }


  Serial.println("SETUP");
}

void show_index(){
  for(int idx = 0 ; idx < 8; idx++){
    bool xbit = (g_xout >> idx) & 1;
    bool ybit = (g_yout >> idx) & 1;
    if (xbit)
      digitalWrite(xbits[idx], HIGH);
    else
      digitalWrite(xbits[idx], LOW);
    if (ybit)
      digitalWrite(xbits[idx], HIGH);
    else
      digitalWrite(xbits[idx], LOW);
  }
}

void loop() {
    serialio_feed();
    DripRecorded dr;
    pb_ostream_t stream = pb_ostream_from_buffer(buffer, sizeof(buffer));
    dr.drips = (unsigned int)millis() / 100;
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
    show_index();
}
