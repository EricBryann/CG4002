bool ready_to_run;    // Decides if handshake as been made.
bool send_data;       // Sends a series of data, but only once.
long x, y, z;         // Coordinates from IR and accelerometers.
int beetleNo;         // For labelling the beetles.

void setup() {
  Serial.begin(115200);     // Starts the beetle.
  ready_to_run = false;     
  send_data = true;
  beetleNo = 2;             // CHANGE THIS NUMBER FOR EACH BEETLE!
}

void loop() {
  
  if (ready_to_run == false && Serial.available()) { // Wait for handshake
    String handshake = Serial.readString();
    if (handshake == "start") {
      ready_to_run = true;
      Serial.print("<INCOMING DATA FROM B" + String(beetleNo) + "!!>");
      delay(1000);
    }
  }
  
  if (ready_to_run) { // Handshake has been made
    if (send_data) {  
      for (int i = 1; i<=5000 ; i++) {
        x = random(300);
        y = random(300);
        z = random(300);
        String data_to_send = "<Set " + String(i) + " from B" + String(beetleNo) + ": " + String(x) + ", " + String(y) + ", " + String(z) + ">"; 
        Serial.print(data_to_send);
        delay(150);
        while(Serial.available()==0){   // Wait for Python to complete processing previous data. Stop and Wait implemented currently.
          Serial.print(data_to_send);   
          delay(150);
        }
      }
      Serial.write("END");
      send_data = false;  //Stops sending anymore data.
    }
  }
}
