int count = 1;
int Delay = 2000;
int coordinates[] = {100, 12, -23};
bool waiting_for_ack = false;
String output;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);        //initialise the Serial
  Serial.println("Arduino ready");
  Serial.write("<Beetle ready>");
}

/*
struct {
  char startMarker;
  int8_t x;      // 2 bytes int
  int8_t y;      // 2 bytes int
  int8_t z;      // 2 bytes int
  int8_t checksum; // 2 bytes int
  char endMarker;
} TPacket;
*/

void loop() {
  delay(Delay);
  if (not waiting_for_ack){
    //Serial.write("<Beetle 1 says: Hello, this is a long message>");
    Serial.write("<Beetle 2 says: I fking hate this module. Why does this module even exist. Just fking get over and done with!!!!>");
  }
  
  waiting_for_ack = true;
  
  if (Serial.available() == 0) {
    output = String( "<Beetle2 says : timeout! " + String(count) + " test>" );
    Serial.print(output);
  } else {
    String teststr = Serial.readString();
      if (teststr == "ok") {
        count++;
        output = String( "<Beetle2 says : ack received! " + String(count) + " test>" );
      } else {
        output = String( "<Beetle2 says : bad ack! " + String(count) + " test>" );
      }
      Serial.print(output);
  }
}
