void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600); 

  // Baud rate = 9600 palavras
  // É possível transmitir baud/bits = bits por segundo
  //  considerando 8 bits de dados (1byte) + 1 bit de início + 1 bit de fim
  //  total = 10 bits
  
  // Neste caso
  //  9600 / 10 = 960 bps
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.print("A");
}
