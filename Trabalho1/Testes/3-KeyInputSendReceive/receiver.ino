/**
 * Cable setting:
 * Sender || Receiver
 * GND <-> GND
 * TX -> RX
 */

void setup() {
  Serial.begin(9600);
  Serial.println("=== Receiver ===");
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    Serial.println(c);
  }
  delay(1000);
}