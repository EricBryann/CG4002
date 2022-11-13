#include "IRremote.h"

#define LED 3
#define PIN_SEND 2
#define BUTTON 5

int GREEN_ENCODING_VALUE = 0xFF6890;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(LED, OUTPUT);
  IrSender.begin(PIN_SEND);
}

int buttonState = 0;
int numBullets = 6;
int prevButtonState = 0;

bool ready_to_run = false;

byte data_packet[13];

void loop() {
  while(!ready_to_run) {
    if (Serial.available() && Serial.readString() == "start") { // Wait for handshake
        ready_to_run = true;
//        Serial.print("<INCOMING DATA FROM B Emitter !!>");
        delay(1000);
    }
  }
  buttonState = digitalRead(BUTTON);
  if (prevButtonState == LOW && buttonState == HIGH) {
    IrSender.sendNEC(GREEN_ENCODING_VALUE, 32);
//    Serial.println("<GREEN shoot>");
      data_packet[0] = byte('A'); //starting byte is 'A' means shoot
      for (int i = 1; i <= 12; i++) {
        data_packet[i] = byte(0);
      }
      Serial.write(data_packet, 13);
    // numBullets--;

    // if (numBullets == 0) numBullets = 6;

    // for(int i = 0; i < numBullets; i++) {
      digitalWrite(LED, HIGH);
      delay(500);
      digitalWrite(LED, LOW);
      // delay(200);
    // }
  }

  prevButtonState = buttonState;
  delay(100);
}
