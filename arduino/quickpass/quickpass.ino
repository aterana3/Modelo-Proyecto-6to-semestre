#include <Servo.h>

const int sensorEntrada = 13;
const int sensorSalida = 12;
const int servoPin = 11;
const int ldrPin = A11;

const int ledPin = 10;

Servo barrera;
bool fotoTomada = false;
int ldrUmbral = 300;

void setup() {
  Serial.begin(9600);
  pinMode(sensorEntrada, INPUT);
  pinMode(sensorSalida, INPUT);
  pinMode(ledPin, OUTPUT);
  barrera.attach(servoPin);
  barrera.write(0);
}

void loop() {
  if (digitalRead(sensorEntrada) == LOW && !fotoTomada) {
    Serial.println("CAPTURE");
    fotoTomada = true;
  }

  if (Serial.available() > 0) {
    String response = Serial.readStringUntil('\n');
    if (response == 'SUCCESS' && fotoTomada) {
      abrirBarrera();
    }
  }

  if (digitalRead(sensorSalida) == LOW && fotoTomada) {
    cerrarBarrera();
    fotoTomada = false;
  }

  int ldrValor = analogRead(ldrPin);
  if (ldrValor > ldrUmbral) {
    digitalWrite(ledPin, HIGH);
  } else {
    digitalWrite(ledPin, LOW);
  }
}

void abrirBarrera() {
  barrera.write(90);
  delay(1000);
}

void cerrarBarrera() {
  barrera.write(0);
}