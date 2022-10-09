#include "IRremote.h"

#define RECV_PIN 2
#define LED_RECV 3

int GREEN_ENCODING_VALUE = 0xFF6890;

IRrecv irrecv(RECV_PIN);
decode_results results;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(LED_RECV, OUTPUT);
  irrecv.enableIRIn();
}

bool ready_to_run = false;
byte data_packet[13];

void loop() {
  //handshake
  while(!ready_to_run) {
    if (Serial.available() && Serial.readString() == "start") { // Wait for handshake
        ready_to_run = true;
//        Serial.print("<INCOMING DATA FROM B Receiver !!>");
        delay(1000);
    }
  }
  // put your main code here, to run repeatedly:
  if (irrecv.decode(&results)) {
    if (results.value == GREEN_ENCODING_VALUE) {
//      Serial.println("<GREEN shot>");
      data_packet[0] = byte('B'); //starting byte is 'B' means shot
      for (int i = 1; i <= 12; i++) {
        data_packet[i] = byte(0);
      }
      Serial.write(data_packet, 13);
      digitalWrite(LED_RECV, HIGH);
      delay(300);
      digitalWrite(LED_RECV, LOW);
    }
    irrecv.resume();
  }
}
