#include "serialio.h"
#include "pb.h"
#include "pb_decode.h"
#include "messages.pb.h"

/**
 * Serial protocol
 *
 * Header - 0x12
 * Type 
 * Payload
 * Footer - 0x13
 *
 * Everything between header and footer is escaped to ensure that the
 header and footer are only ever transmitted as headers and footers. Escaping happens by sending 0x14 followed by ^(byte). Have to escape 0x12, 0x13, 0x14. 
 * State machine for reading:
 * SEARCHING - looking for 0x12
 * READING - filling buffer
 * READING_GOT_ESCAPE - skip writing to buffer, write ^(next) to buffer
 * DONE - read 0x13
*/

int g_xout = 0;
int g_yout = 0;

#define HEADER 0x40
#define FOOTER 0x41
#define ESCAPE_CHAR 0x42

void handle_move(char* buffer, int len);
void handle_nack(char* buffer, int len);
void handle_ack(char* buffer, int len);

static type_callback_map_t callbacks[] = {
  { NACK, &handle_nack },
  { ACK, &handle_ack },
  { MOVE, &handle_move }, 
  { 0, 0 }
};

serial_state_t serial_searching(uint8_t* idx, char* buffer, char input) {
  if(input != HEADER) {
    return SEARCHING;
  }
  *idx = 0;
  buffer[*idx] = 0;
  return READING;
}

serial_state_t serial_reading(uint8_t* idx, char* buffer, char input) {
  if(input == ESCAPE_CHAR) {
    return READING_ESCAPED;
  }
  if(input == FOOTER) {
    return DONE;
  }
  buffer[*idx] = input;
  (*idx) += 1;
  return READING;
}

serial_state_t serial_reading_esc(uint8_t* idx, char* buffer, char input) {
  buffer[*idx] = ~input;
  (*idx) += 1;
  return READING;
}

serial_state_t serial_done(uint8_t* idx, char* buffer) {
  type_callback_map_t* cur = callbacks;
  while(cur->callback != 0) {
    if (cur->message_type == buffer[0]) {
      buffer[*idx] = 0;
      cur->callback(&buffer[1], (*idx)-1);
      break;
    }
    cur++;
  }
  return SEARCHING;
}

void serialio_feed() {
  static char buffer[32] = {0};
  static uint8_t idx = 0;
  static serial_state_t state = SEARCHING;

  int input = 0;

  if((input = SerialUSB.read()) != -1) {
    switch(state) {
    case SEARCHING: state = serial_searching(&idx, buffer, (char)input); break;
    case READING: state = serial_reading(&idx, buffer, (char)input); break;
    case READING_ESCAPED: state = serial_reading_esc(&idx, buffer, (char)input); break;
    default:
      break;
    }
    if (state == DONE) { // Special case DONE because it doesn't need any input
      state = serial_done(&idx, buffer); 
    }
  }
}

/*****************************************/
/* Callbacks for handling messages */

void handle_move(char* buffer, int len) {
  Serial.println("Got Move");
  pb_istream_t stream = pb_istream_from_buffer((uint8_t *)buffer, len);
  bool status;
  Move message;

  status = pb_decode(&stream, Move_fields, &message);
  if(status) {
    g_xout = (message.x >> 8) & 0xFF;
    g_yout = (message.y >> 8) & 0xFF;
    Serial.print("x:y ");
    Serial.print(g_xout);
    Serial.print(", ");
    Serial.println(g_yout);
  }
}
void handle_nack(char* buffer, int len) {

}
void handle_ack(char* buffer, int len) {

}