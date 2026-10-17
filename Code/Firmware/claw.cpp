//this claw uses a seperate esp32 rather than the pi pico

#include <Arduino.h>
#include <ESP32Servo.h>

Servo clawServo;

const int BUTTON_PIN = 12; 
const int SERVO_PIN  = 4;  // Servo signal pin

const int CLAW_OPEN_ANGLE  = 110;  
const int CLAW_CLOSE_ANGLE = 180; //reduce this a little since if its too tight the servo might shear

bool clawIsClosed = false;

void setup() {
  Serial.begin(115200);
  delay(1000); 

  pinMode(BUTTON_PIN, INPUT_PULLUP);

  ESP32PWM::allocateTimer(0); //reserving a hardware timer

  
  clawServo.setPeriodHertz(50); //making use of that timer to send a signal 50 times every second
  clawServo.attach(SERVO_PIN, 500, 2500); // changes the pulse widths a little cuz the angles werent actually accurate to the movement of the servo

  // Start open
  clawServo.write(CLAW_OPEN_ANGLE);
  Serial.println("CLAW SYSTEM ACTIVE");
}

void loop() {

  if (digitalRead(BUTTON_PIN) == LOW) {
    
    // Toggle the state
    clawIsClosed = !clawIsClosed; 

    if (clawIsClosed) {
      Serial.println("OPENING");
      clawServo.write(CLAW_CLOSE_ANGLE);
    } else {
      Serial.println("CLOSING");
      clawServo.write(CLAW_OPEN_ANGLE); //might want to change the speed here :D
    }

    while(digitalRead(BUTTON_PIN) == LOW) {
      delay(10); 
    }
    
    //debounce
    delay(50); 
  }
}

