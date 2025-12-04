// ----- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ -----

volatile int l_state = 0;   // тики левого мотора (в прерывании -> volatile)
volatile int r_state = 0;   // тики правого мотора

const int PIN_LEFT_DIR  = 4;   // направление левого мотора
const int PIN_LEFT_PWM  = 5;   // скорость левого мотора (PWM)
const int PIN_RIGHT_PWM = 6;   // скорость правого мотора (PWM)
const int PIN_RIGHT_DIR = 7;   // направление правого мотора
const int PIN_LED       = 13;  // индикатор

// Буфер для приёма строки из Serial
const byte CMD_BUF_LEN = 32;
char cmdBuf[CMD_BUF_LEN];
byte cmdPos = 0;


// ----- НАСТРОЙКА -----

void setup() {
  attachInterrupt(0, l_tik, CHANGE); // пин 2 на Arduino UNO
  attachInterrupt(1, r_tik, CHANGE); // пин 3 на Arduino UNO

  pinMode(PIN_LEFT_DIR,  OUTPUT);
  pinMode(PIN_LEFT_PWM,  OUTPUT);
  pinMode(PIN_RIGHT_PWM, OUTPUT);
  pinMode(PIN_RIGHT_DIR, OUTPUT);
  pinMode(PIN_LED,       OUTPUT);

  Serial.begin(115200);
  delay(1000);

  // Очистим входной буфер от мусора
  while (Serial.available()) {
    Serial.read();
  }

  digitalWrite(PIN_LED, HIGH);
  Serial.println(F("Arduino готов. Вращаюсь в ожидании команды 'start'."));
}


// ----- ПРИЁМ КОМАНДЫ -----

// true, если считана команда "start"
bool readStartCommand() {
  while (Serial.available()) {
    char c = (char)Serial.read();

    if (c == '\n' || c == '\r') {
      // Конец строки
      cmdBuf[cmdPos] = '\0';      // завершаем строку
      if (cmdPos > 0) {
        Serial.print(F("RX: '"));
        Serial.print(cmdBuf);
        Serial.println(F("'"));

        bool isStart = (strcmp(cmdBuf, "start") == 0);
        cmdPos = 0;
        cmdBuf[0] = '\0';

        if (isStart) {
          Serial.println(F("Команда 'start' принята."));
          return true;
        }
      } else {
        // Пустая строка - игнор
        cmdPos = 0;
      }
    } else {
      // Накопление символов
      if (cmdPos < CMD_BUF_LEN - 1) {
        cmdBuf[cmdPos++] = c;
      } else {
        // Переполнение буфера - сброс
        cmdPos = 0;
      }
    }
  }
  return false;
}


// ----- ДВИЖЕНИЕ -----

void stopAllMotors() {
  digitalWrite(PIN_LEFT_DIR,  LOW);
  digitalWrite(PIN_RIGHT_DIR, LOW);
  analogWrite(PIN_LEFT_PWM,   0);
  analogWrite(PIN_RIGHT_PWM,  0);
}

void rightTurn(int speed) {
  digitalWrite(PIN_RIGHT_DIR, HIGH);
  digitalWrite(PIN_LEFT_DIR,  LOW);
  analogWrite(PIN_RIGHT_PWM,  speed);
  analogWrite(PIN_LEFT_PWM,   speed);
}

void leftTurn(int speed) {
  digitalWrite(PIN_RIGHT_DIR, LOW);
  digitalWrite(PIN_LEFT_DIR,  HIGH);
  analogWrite(PIN_RIGHT_PWM,  speed);
  analogWrite(PIN_LEFT_PWM,   speed);
}

void resetstate() {
  noInterrupts();
  l_state = 0;
  r_state = 0;
  interrupts();
}

// Движение вперёд на n тиков, с таймаутом
void forvard(int n) {
  Serial.println(F("FORWARD start"));
  resetstate();
  unsigned long t0 = millis();
  const unsigned long MAX_TIME = 15000;  // 15 секунд на всякий случай

  while (true) {
    int l, r;
    noInterrupts();
    l = l_state;
    r = r_state;
    interrupts();

    if (l >= n && r >= n) {
      break;
    }

    if (millis() - t0 > MAX_TIME) {
      Serial.println(F("FORWARD timeout!"));
      break;
    }

    digitalWrite(PIN_RIGHT_DIR, HIGH);
    digitalWrite(PIN_LEFT_DIR,  HIGH);
    analogWrite(PIN_RIGHT_PWM, 255);
    analogWrite(PIN_LEFT_PWM,  255);
  }

  stopAllMotors();
  Serial.print(F("FORWARD done. l_state="));
  Serial.print(l_state);
  Serial.print(F(" r_state="));
  Serial.println(r_state);
}

// Движение назад на n тиков, с таймаутом
void resvard(int n) {
  Serial.println(F("BACKWARD start"));
  resetstate();
  unsigned long t0 = millis();
  const unsigned long MAX_TIME = 15000;  // 15 секунд на всякий случай

  while (true) {
    int l, r;
    noInterrupts();
    l = l_state;
    r = r_state;
    interrupts();

    if (l >= n && r >= n) {
      break;
    }

    if (millis() - t0 > MAX_TIME) {
      Serial.println(F("BACKWARD timeout!"));
      break;
    }

    digitalWrite(PIN_RIGHT_DIR, LOW);
    digitalWrite(PIN_LEFT_DIR,  LOW);
    analogWrite(PIN_RIGHT_PWM, 255);
    analogWrite(PIN_LEFT_PWM,  255);
  }

  stopAllMotors();
  Serial.print(F("BACKWARD done. l_state="));
  Serial.print(l_state);
  Serial.print(F(" r_state="));
  Serial.println(r_state);
}


// ----- ОБРАБОТЧИКИ ПРЕРЫВАНИЙ -----

void l_tik() {
  l_state += 1;
}

void r_tik() {
  r_state += 1;
}


// ----- ОСНОВНОЙ ЦИКЛ -----

void loop() {
  // 1. Вращаемся влево, пока не придёт команда "start"
  Serial.println(F("Вращаюсь влево в ожидании команды 'start'..."));
  while (!readStartCommand()) {
    leftTurn(200);   // скорость можешь подобрать
    // без delay, чтобы часто проверять UART
  }

  // 2. Команда получена — останавливаемся
  stopAllMotors();
  Serial.println(F("Получен 'start', выполняю движение вперёд-назад"));

  // мигнём светодиодом
  digitalWrite(PIN_LED, HIGH);
  delay(100);
  digitalWrite(PIN_LED, LOW);

  // 3. Выполняем последовательность движения
  forvard(3600);
  delay(1000);
  resvard(2400);
  delay(1000);

  Serial.println(F("Последовательность выполнена. Снова жду 'start' и вращаюсь."));
  // после этого loop() начнётся заново, и робот опять будет крутиться в ожидании следующего 'start'
}
