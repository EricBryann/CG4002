#include <IRremote.h>

#define LED 3
#define PIN_SEND 2
#define BUTTON 5

int GREEN_ENCODING_VALUE = 0xFF6890;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(LED, OUTPUT);
  IrSender.begin(PIN_SEND);
}

int buttonState = 0;
int numBullets = 6;
int prevButtonState = 0;

void loop() {
  buttonState = digitalRead(BUTTON);
  if (prevButtonState == LOW && buttonState == HIGH) {
    IrSender.sendNEC(GREEN_ENCODING_VALUE, 32);
    Serial.println("Green shoot");
    numBullets--;

    if (numBullets == 0) numBullets = 6;

    for(int i = 0; i < numBullets; i++) {
      digitalWrite(LED, HIGH);
      delay(200);
      digitalWrite(LED, LOW);
      delay(200);
    }
  }

  prevButtonState = buttonState;
  delay(100);
}
