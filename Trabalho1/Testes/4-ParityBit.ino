void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    Serial.println(c, BIN);
    Serial.println(getEvenParityBit(c));
  }
  delay(1000);
}

byte getEvenParityBit(byte data) {
  byte count = 0;

  while (data > 0) {
    if (data % 2 == 1) {
      count++;
    }
    // Bit shift
    //  0110101 -> 0011010
    data = data >> 1;
  }

  return count % 2;  // 0 = even, 1 = odd
}