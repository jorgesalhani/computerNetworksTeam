#include "Temporizador.h"

// ==========================================
// CÓDIGO DO EMISSOR
// ==========================================
const int pinoClockE = 12; // Pino que envia o sinal de Clock
const int pinoRTSE   = 4;  // Envia o sinal RTS (Request To Send)
const int pinoCTSE   = 5;  // Lê o sinal CTS (Clear To Send)
const int pinoTXE    = 13; // Envia os Dados (Obrigatório)

volatile byte dadoParaEnviar = 0;
volatile byte paridadeEnvio = 0;
volatile int bitAtualE = 0;
volatile bool transmitindo = false;

void setup() {
  Serial.begin(9600);

  // Configuração das portas
  pinMode(pinoClockE, OUTPUT);
  pinMode(pinoRTSE, OUTPUT);
  pinMode(pinoCTSE, INPUT);
  pinMode(pinoTXE, OUTPUT);

  // Estado inicial de repouso (tudo em zero)
  digitalWrite(pinoClockE, LOW);
  digitalWrite(pinoRTSE, LOW);
  digitalWrite(pinoTXE, LOW);

  // Define a velocidade (Baud Rate do clock) - 10 Hz para testes visuais
  configuraTemporizador(10); 
  
  Serial.println("=====================================");
  Serial.println("Emissor Iniciado");
  Serial.println("Digite um caractere para enviar...");
  Serial.println("=====================================");
}

void loop() {
  // Verifica se não está no meio de uma transmissão e se chegou algo no Serial Monitor
  if (!transmitindo && Serial.available() > 0) {
    char c = Serial.read();
    
    // Ignora o "Enter" (quebra de linha) do teclado USB
    if (c == '\n' || c == '\r') return; 

    dadoParaEnviar = c;
    paridadeEnvio = calculaParidadePar(dadoParaEnviar);
    bitAtualE = 0;

    Serial.print("\n>>> Preparando envio do caractere: '");
    Serial.print(c);
    Serial.println("'");

    // PASSO 1: Levanta o RTS pedindo para iniciar a comunicação
    digitalWrite(pinoRTSE, HIGH);
    Serial.println("[Handshake] RTS = 1. Aguardando CTS...");

    // PASSO 2: Segura o fluxo (trava) até o receptor estar pronto (CTS = HIGH)
    while(digitalRead(pinoCTSE) == LOW) {}
    
    Serial.println("[Handshake] CTS = 1. Iniciando envio com Clock...");

    transmitindo = true;
    iniciaTemporizador(); // O hardware começa a interromper e enviar os bits automaticamente

    // PASSO 4: Aguarda o envio físico terminar na interrupção
    while(transmitindo) {} 
    
    // PASSO 7: Aguarda o receptor baixar o CTS confirmando que processou o pacote
    while(digitalRead(pinoCTSE) == HIGH) {} 

    Serial.println("--- Transmissao 100% concluida! ---");
  }
}

// ==========================================
// CÁLCULO DA PARIDADE PAR
// ==========================================
byte calculaParidadePar(byte dado) {
  int contadorDeUns = 0;
  for (int i = 0; i < 8; i++) {
    if (bitRead(dado, i) == 1) contadorDeUns++;
  }
  // Se já tem um número par de '1's, a paridade é 0. Se for ímpar, é 1.
  return (contadorDeUns % 2 == 0) ? 0 : 1;
}

// ==========================================
// ROTINA DE INTERRUPÇÃO (TIMER1)
// ==========================================
ISR(TIMER1_COMPA_vect) {
  if (bitAtualE < 9) { // 8 bits de dado + 1 de paridade
    int valorBit;
    
    if (bitAtualE < 8) {
      valorBit = bitRead(dadoParaEnviar, bitAtualE);
    } else {
      valorBit = paridadeEnvio; // O 9º bit é a paridade calculada
    }

    // 1. Coloca o nível lógico correto no fio de Dados
    digitalWrite(pinoTXE, valorBit);

    // 2. Dá o pulso de Clock (Borda de subida que o receptor vai ler)
    digitalWrite(pinoClockE, HIGH); 
    digitalWrite(pinoClockE, LOW);  

    bitAtualE++;
  } else {
    // PASSO 5: Terminou os 9 bits, para o timer e finaliza o pedido (baixa RTS)
    paraTemporizador();
    digitalWrite(pinoRTSE, LOW);
    transmitindo = false;
  }
}