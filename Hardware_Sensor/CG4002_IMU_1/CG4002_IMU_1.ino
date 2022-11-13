#include "I2Cdev.h"

#include "MPU6050_6Axis_MotionApps20.h"
//#include "MPU6050.h" // not necessary if using MotionApps include file

// Arduino Wire library is required if I2Cdev I2CDEV_ARDUINO_WIRE implementation
// is used in I2Cdev.h
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    #include "Wire.h"
#endif

MPU6050 mpu;

#define OUTPUT_READABLE_YAWPITCHROLL

bool ready_to_run;    // Decides if handshake as been made.
bool send_data;       // Sends a series of data, but only once.
long x, y, z;         // Coordinates from IR and accelerometers.
int beetleNo;         // For labelling the beetles.

int ACCEL_X_MOVEMENT_THRESHOLD = 800;
int ACCEL_Y_MOVEMENT_THRESHOLD = 800;
int ACCEL_Z_MOVEMENT_THRESHOLD = 800;

int MAX_MOVEMENT_POINTS = 25;
int DELAY = 50;

// MPU control/status vars
bool dmpReady = false;  // set true if DMP init was successful
uint8_t devStatus;      // return status after each device operation (0 = success, !0 = error)
uint16_t packetSize;    // expected DMP packet size (default is 42 bytes)
uint16_t fifoCount;     // count of all bytes currently in FIFO
uint8_t fifoBuffer[64]; // FIFO storage buffer

// orientation/motion vars
Quaternion q;           // [w, x, y, z]         quaternion container
VectorInt16 aa;         // [x, y, z]            accel sensor measurements
VectorInt16 aaReal;     // [x, y, z]            gravity-free accel sensor measurements
VectorInt16 aaWorld;    // [x, y, z]            world-frame accel sensor measurements
VectorFloat gravity;    // [x, y, z]            gravity vector
float euler[3];         // [psi, theta, phi]    Euler angle container
float ypr[3];           // [yaw, pitch, roll]   yaw/pitch/roll container and gravity vector

// ================================================================
// ===                      INITIAL SETUP                       ===
// ================================================================

void setup() {
    // join I2C bus (I2Cdev library doesn't do this automatically)
    #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
        Wire.begin();
        Wire.setClock(400000); // 400kHz I2C clock. Comment this line if having compilation difficulties
    #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
        Fastwire::setup(400, true);
    #endif

    ready_to_run = false;
    send_data = true;
    beetleNo = 2;             // CHANGE THIS NUMBER FOR EACH BEETLE!

    // initialize serial communication
    // (115200 chosen because it is required for Teapot Demo output, but it's
    // really up to you depending on your project)
    Serial.begin(115200);
    while (!Serial); // wait for Leonardo enumeration, others continue immediately

    // NOTE: 8MHz or slower host processors, like the Teensy @ 3.3V or Arduino
    // Pro Mini running at 3.3V, cannot handle this baud rate reliably due to
    // the baud timing being too misaligned with processor ticks. You must use
    // 38400 or slower in these cases, or use some kind of external separate
    // crystal solution for the UART timer.

    // initialize device
    // Serial.println(F("Initializing I2C devices..."));
    mpu.initialize();

    // verify connection
    // Serial.println(F("Testing device connections..."));
    // Serial.println(mpu.testConnection() ? F("MPU6050 connection successful") : F("MPU6050 connection failed"));

    // wait for ready
    // Serial.println(F("\nSend any character to begin DMP programming and demo: "));
    // while (Serial.available() && Serial.read()); // empty buffer
    // while (!Serial.available());                 // wait for data
    while (Serial.available() && Serial.read()); // empty buffer again

    // load and configure the DMP
    // Serial.println(F("Initializing DMP..."));
    devStatus = mpu.dmpInitialize();

    // supply your own gyro offsets here, scaled for min sensitivity
    mpu.setXGyroOffset(-26);
    mpu.setYGyroOffset(-2);
    mpu.setZGyroOffset(6);
    mpu.setXAccelOffset(-2434);
    mpu.setYAccelOffset(-2);
    mpu.setZAccelOffset(881); // 1688 factory default for my test chip

    // make sure it worked (returns 0 if so)
    if (devStatus == 0) {
        // Calibration Time: generate offsets and calibrate our MPU6050
        // mpu.CalibrateAccel(6);
        // mpu.CalibrateGyro(6);
        // mpu.PrintActiveOffsets();
        // turn on the DMP, now that it's ready
        // Serial.println(F("Enabling DMP..."));
        mpu.setDMPEnabled(true);

        // set our DMP Ready flag so the main loop() function knows it's okay to use it
        dmpReady = true;

        // get expected DMP packet size for later comparison
        packetSize = mpu.dmpGetFIFOPacketSize();
    } else {
        // ERROR!
        // 1 = initial memory load failed
        // 2 = DMP configuration updates failed
        // (if it's going to break, usually the code will be 1)
        // Serial.print(F("DMP Initialization failed (code "));
        // Serial.print(devStatus);
        // Serial.println(F(")"));
    }
}



// ================================================================
// ===                    MAIN PROGRAM LOOP                     ===
// ================================================================

int initialDelay = 0;
int movementPoint = 0;

byte data_packet[13];

void loop() {
    // if programming failed, don't try to do anything
    if (!dmpReady) return;

    while(!ready_to_run) {
      if (Serial.available() && Serial.readString() == "start") { // Wait for handshake
          ready_to_run = true;
          //Serial.print("<INCOMING DATA FROM B" + String(beetleNo) + "!!>");
          delay(1000);
      }
    }

    mpu.resetFIFO();
    fifoCount = mpu.getFIFOCount();
    while (fifoCount < packetSize) {
      fifoCount = mpu.getFIFOCount();
    }

    while (fifoCount >= packetSize) {      
      mpu.getFIFOBytes(fifoBuffer, packetSize);
      fifoCount -= packetSize;
    }
    
    mpu.dmpGetQuaternion(&q, fifoBuffer);
    mpu.dmpGetGravity(&gravity, &q);
    mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);

    mpu.dmpGetAccel(&aa, fifoBuffer);
    mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity);
    mpu.dmpGetLinearAccelInWorld(&aaWorld, &aaReal, &q);

    if (initialDelay <= 150) {
      initialDelay++;
    }

    if (movementPoint >= MAX_MOVEMENT_POINTS) {
      movementPoint = 0;
      delay(50);
    }

    if (initialDelay <= 150 || (!(movementPoint > 0 && movementPoint < MAX_MOVEMENT_POINTS) && (abs(aaWorld.x) < ACCEL_X_MOVEMENT_THRESHOLD && abs(aaWorld.y) < ACCEL_Y_MOVEMENT_THRESHOLD && abs(aaWorld.z) < ACCEL_Z_MOVEMENT_THRESHOLD))) {
      // means not moving
      movementPoint = 0;
    } else {
      ypr[0] = ypr[0] * 180 / M_PI;
      ypr[1] = ypr[1] * 180 / M_PI;
      ypr[2] = ypr[2] * 180 / M_PI;

      int16_t y = (int16_t)(ypr[0] * 100);
      int16_t p = (int16_t)(ypr[1] * 100);
      int16_t r = (int16_t)(ypr[2] * 100);

      int16_t ax = (int16_t)aaWorld.x;
      int16_t ay = (int16_t)aaWorld.y;
      int16_t az = (int16_t)aaWorld.z;

      data_packet[0] = byte('C');
      data_packet[1] = byte( (ax >> 8) & 0xff);
      data_packet[2] = byte(ax & 0xff);
      data_packet[3] = byte( (ay >> 8) & 0xff);
      data_packet[4] = byte(ay & 0xff);
      data_packet[5] = byte( (az >> 8) & 0xff);
      data_packet[6] = byte(az & 0xff);

            
      data_packet[7] = byte( (y >> 8) & 0xff);
      data_packet[8] = byte(y & 0xff);
      data_packet[9] = byte( (p >> 8) & 0xff);
      data_packet[10] = byte(p & 0xff);
      data_packet[11] = byte( (r >> 8) & 0xff);
      data_packet[12] = byte(r & 0xff);
      Serial.write(data_packet, 13);
      
      movementPoint++;
    }

    delay(DELAY);
}
