boolean signalStart = false;
boolean squareInFocus = false;
String inputString = "";
int l_state = 0; //тики левого мотора
int r_state = 0; //тики правого мотора
void setup() {
  attachInterrupt(0, l_tik, CHANGE); //аппаратное прерывание левого мотора
  attachInterrupt(1, r_tik, CHANGE); //аппаратное прерывание правого мотора

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

boolean readMsg() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {                // строка завершена
      inputString.trim();
      if (inputString == "start") {
        return true;
      }
      inputString = "";
    } else {
      inputString += c;
    }
  }
  return false;
  Serial.flush();
}

void rightTurn(int speed) {
  digitalWrite(7, 1);
  digitalWrite(4, 0);
  analogWrite(6, speed);
  analogWrite(5, speed);

}
// поворот направо с определенной скоростью

void leftTurn(int speed) {
  digitalWrite(7, 0);
  digitalWrite(4, 1);
  analogWrite(6, speed);
  analogWrite(5, speed);
}
// поворот налево с определенной скоростью
void stopAllMotors() {
  digitalWrite(4, 0);
  digitalWrite(5, 0);
  digitalWrite(6, 0);
  digitalWrite(7, 0);

}

void resvard(int n) {
  resetstate();
  while ((l_state < n) and (r_state < n)) {
    Serial.print("l_state ");
    Serial.print(l_state);
    Serial.print(" r_state ");
    Serial.println(r_state);
    digitalWrite(7, 0);
    digitalWrite(4, 0);
    analogWrite(6, 255);
    analogWrite(5, 255);
  }
  stopAllMotors();
  //Эта функция дает команду отъехать на количество тиков на энкодерах, 1600 - 1 оборот колеса после приезда она сбрасывает состояние энкодеров
}


void forvard(int n) {
  resetstate();
  while ((l_state < n) and (r_state < n)) {
    Serial.print("l_state ");
    Serial.print(l_state);
    Serial.print(" r_state ");
    Serial.println(r_state);
    digitalWrite(7, 1);
    digitalWrite(4, 1);
    analogWrite(6, 255);
    analogWrite(5, 255);
  }
  stopAllMotors();
  //Эта функция дает команду ехать вперед на количество тиков на энкодерах, 1600 - 1 оборот колеса после приезда она сбрасывает состояние энкодеров
}

void l_tik() {
  l_state += 1;
}
void r_tik() {
  r_state += 1;
}
void resetstate() {
  l_state = 0;
  r_state = 0;
}


void loop() {

  while (squareInFocus == false) {
    leftTurn(200);
    squareInFocus = readMsg();
  }
  stopAllMotors();
  forvard(4800);
  delay(1000);
  resvard(4800);
  delay(1000);
  squareInFocus = false;
  Serial.flush();


}
