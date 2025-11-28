boolean segnalStart = false;
void setup() {
  pinMode(4, OUTPUT); //turn left motor
  pinMode(5, OUTPUT); //speed left motor
  pinMode(6, OUTPUT); //speed right motor
  pinMode(7, OUTPUT); //turn right motor
  Serial.begin(115200);
  delay(1000);
  while (!Serial) {
    delay(20);
  }
}

void rightTurn(int speed) {
  digitalWrite(7, 1);
  digitalWrite(4, 0);
  analogWrite(6, speed);
  analogWrite(5, speed);

}


void leftTurn(int speed) {
  digitalWrite(7, 0);
  digitalWrite(4, 1);
  analogWrite(6, speed);
  analogWrite(5, speed);
}

void stopAllMotors() {
  digitalWrite(4, 0);
  digitalWrite(5, 0);
  digitalWrite(6, 0);
  digitalWrite(7, 0);

}
void loop() {
  if (Serial.available()) {
    String msg = Serial.readString();
    if (msg == "start") {
      segnalStart = true;
    }
  }
  if (segnalStart) {
    leftTurn(255);
    delay(3000);
    stopAllMotors();
    while (1);
  }


}
