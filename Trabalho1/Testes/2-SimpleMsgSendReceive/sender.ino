/**
 * Cable setting:
 * Sender || Receiver
 * GND <-> GND
 * TX -> RX
 */

void setup() {
  Serial.begin(9600);
}

void loop() {
  Serial.println("Mensagem de A");
  delay(1000);
}