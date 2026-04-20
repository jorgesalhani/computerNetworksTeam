/**
 * Cable setting:
 * Sender || Receiver
 * GND <-> GND
 * TX -> RX
 */

void setup() {
  Serial.begin(9600);
  // Serial.println("=== Sender ===");
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    // Serial.println(c);
    Serial.write(c);
  }
  delay(1000);
}