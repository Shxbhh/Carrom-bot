// Declare variables
int distance = 0;   // Striker position
float angle = 0.0;  // Aiming angle
String receivedData; // Stores incoming serial data

void setup() {
  Serial.begin(9600); // Initialize serial communication
  pinMode(8, OUTPUT); // Controls angle reset
  pinMode(9, OUTPUT); // Controls angle adjustment
  pinMode(10, OUTPUT); // Controls position reset
  pinMode(11, OUTPUT); // Controls position adjustment
  
  Serial.write('1'); // Signal that Arduino is ready
}

void loop() {
  // Wait for data from the computer
  if (Serial.available() > 0) {
    while (Serial.available() > 0) {
      receivedData = Serial.readString(); // Read incoming data
    }
    
    // Extract distance and angle from received string
    distance = (receivedData[0] - '0') * 100 + (receivedData[1] - '0') * 10 + (receivedData[2] - '0');
    angle = (receivedData[3] - '0') * 100 + (receivedData[4] - '0') * 10 + (receivedData[5] - '0');

    // Move striker to calculated position
    digitalWrite(10, LOW); // Set direction forward
    moveStepperMotor(11, distance * 2.1 * 100 / 18);
    
    delay(1000); // Pause before aiming

    // Rotate striker to specified angle
    digitalWrite(8, HIGH);
    moveStepperMotor(9, angle * 100 / 180);
    
    delay(1000); // Pause before shot
    
    // (Optional) Trigger striker release - Uncomment if needed
    /*
    delay(10000);
    digitalWrite(2, HIGH);
    digitalWrite(3, LOW);
    delay(200);
    digitalWrite(2, LOW);
    digitalWrite(3, LOW);
    */

    delay(1000); // Pause before reset

    // Reset aiming angle
    digitalWrite(8, LOW);
    moveStepperMotor(9, angle * 100 / 180);

    delay(1000); // Pause before moving back

    // Return striker to original position
    digitalWrite(10, HIGH);
    moveStepperMotor(11, distance * 2.1 * 100 / 18);
  }

  // Signal that the shot is completed
  Serial.write('0');
}

// Function to move stepper motor in steps
void moveStepperMotor(int pin, int steps) {
  for (int i = 0; i < steps; i++) {
    digitalWrite(pin, HIGH);
    delay(10);
    digitalWrite(pin, LOW);
    delay(10);
  }
}


