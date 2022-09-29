#include <IRremote.h>

#define RECV_PIN 2
#define LED_RECV 3

int RED_ENCODING_VALUE = 0xFF6897;

IRrecv irrecv(RECV_PIN);
decode_results results;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  irrecv.enableIRIn();
}

void loop() {
  // put your main code here, to run repeatedly:
  if (irrecv.decode(&results)) {
    if (results.value == RED_ENCODING_VALUE) {
      Serial.println("RED shot");
      digitalWrite(LED_RECV, HIGH);
      delay(300);
      digitalWrite(LED_RECV, LOW);
    }
    irrecv.resume();
  }
}
