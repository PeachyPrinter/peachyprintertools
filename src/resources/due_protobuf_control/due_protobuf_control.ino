#include <pb_encode.h>
#include <pb_decode.h>
#include "move.pb.h"
#include "drip.pb.h"

#include <string>

static const short DATA_PIN = 6;

static const char HEADER = 64;
static const char FOOTER = 65;
static const char ESCAPE = 66;

static const int buffer_size = 100;
char buffer[buffer_size];

//PROTO
uint8_t proto_buffer[128];
size_t proto_message_length_recieve;
bool proto_status;
Move proto_move;

void setup() {
  Serial.begin(115200);
  SerialUSB.begin(2);
  pinMode(DATA_PIN, OUTPUT);
  digitalWrite(DATA_PIN, LOW);
  Serial.println("SETUP");
}

int decodeMove(uint8_t* message, int message_length){
    pb_istream_t stream = pb_istream_from_buffer(message, message_length);
    proto_status = pb_decode(&stream, Move_fields, &proto_move);
    if (!proto_status) {
            Serial.print("Decoding failed: ");
            Serial.println(PB_GET_ERROR(&stream));
            return 1;
        }
}

int encodeDrip(DripRecorded drip){
    pb_ostream_t stream = pb_ostream_from_buffer(proto_buffer, sizeof(proto_buffer));
    proto_status = pb_encode(&stream, DripRecorded_fields, &drip);
    proto_message_length_recieve = stream.bytes_written;
    if (!proto_status)
    {
        Serial.print("Encoding failed: ");
        Serial.println(PB_GET_ERROR(&stream));
        return 1;
    }
}

void read_serial_data(){
    Serial.print("PRE_MESSAGE: ");
    int bytesRead = 0;
    while (bytesRead == 0 or buffer[bytesRead -1] == ESCAPE){
        bytesRead = SerialUSB.readBytesUntil(HEADER, buffer, buffer_size);
        if (bytesRead > 0){
            Serial.println(buffer);
        }
    }
    bytesRead = 0;
    int message_bytes = 0;
    char message[buffer_size];
    while (bytesRead == 0 or buffer[bytesRead -1] == ESCAPE){
        bytesRead = SerialUSB.readBytesUntil(FOOTER, buffer, buffer_size);
        Serial.print("Buffer: ");
        Serial.println(buffer);
        memcpy(message, buffer, bytesRead - 1);
        message_bytes = message_bytes + bytesRead;
        Serial.print("Message: ");
        Serial.println(message);
    }
    Serial.println("FOOTER");
    digitalWrite(DATA_PIN, HIGH);
    delay(5);
    digitalWrite(DATA_PIN, LOW);
    delay(5);
}

void loop() {
    Serial.println("LOOP");
    read_serial_data();
}