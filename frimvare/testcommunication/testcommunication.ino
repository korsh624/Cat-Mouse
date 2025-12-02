String inputString = "";

void setup() {
  Serial.begin(115200);
  pinMode(13, OUTPUT); // светодиод
}
boolean readMsg(){
  if (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {                // строка завершена
      inputString.trim();
      if (inputString == "start") {
        return true;
      }
      if (inputString == "stop") {
        digitalWrite(13, LOW);      // выключить LED
        Serial.println("LED OFF");
      }
      inputString = "";
    } else {
      inputString += c;
    }
  }
  return false;
}
void loop() {
  if (readMsg()){
    digitalWrite(13,1);
    delay(1000);
    digitalWrite(13,0);
  }
}
