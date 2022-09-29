#include <IRremote.h>

#define RECV_PIN 2
#define LED_RECV 3

int GREEN_ENCODING_VALUE = 0xFF6890;

IRrecv irrecv(RECV_PIN);
decode_results results;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(LED_RECV, OUTPUT);
  irrecv.enableIRIn();
}

void loop() {
  // put your main code here, to run repeatedly:
  if (irrecv.decode(&results)) {
    if (results.value == GREEN_ENCODING_VALUE) {
      Serial.println("GREEN shot");
      digitalWrite(LED_RECV, HIGH);
      delay(300);
      digitalWrite(LED_RECV, LOW);
    }
    irrecv.resume();
  }
}
