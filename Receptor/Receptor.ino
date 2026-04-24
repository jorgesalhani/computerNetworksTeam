// ==========================================
// TRABALHO REALIZADO POR:
// Adhemar Molon Neto
// Jorge Augusto Salgado Salhani
// Laura Neri Thomaz da Silva
//
// LINK DO VÍDEO DE APRESENTAÇÃO:
// https://youtu.be/5XR75sju2yo
//
// REPOSITORIO GITHUB:
// https://github.com/jorgesalhani/computerNetworksTeam
// ==========================================

#include "Temporizador.h" // Incluído por padronização, embora não seja estritamente necessário para o Receptor Paridade Par neste protocolo específico.

// ==========================================
// CÓDIGO DO RECEPTOR (Paridade Par)
// ==========================================
const int pinoClockR = 2;  // Pino 2 (Usa a Interrupção Externa 0 no Uno)
const int pinoRTSR   = 4;  // Recebe o sinal RTS do Emissor
const int pinoCTSR   = 5;  // Envia o sinal CTS para o Emissor
const int pinoRXR    = 13; // Recebe os dados bit a bit (Obrigatório)

// Variáveis voláteis, pois são modificadas dentro da rotina de interrupção (ISR)
volatile byte dadoRecebido = 0;
volatile byte paridadeRecebida = 0;
volatile int bitAtualR = 0;
volatile bool recebendo = false;

void setup() {
  Serial.begin(9600);

  // Configuração das portas
  pinMode(pinoClockR, INPUT);
  pinMode(pinoRTSR, INPUT);
  pinMode(pinoCTSR, OUTPUT);
  pinMode(pinoRXR, INPUT);

  // Estado inicial de repouso (Receptor não está pronto ainda)
  digitalWrite(pinoCTSR, LOW); 

  // Atrela a função leBitISR para ser disparada toda vez que o sinal de Clock for de 0 para 1 (RISING = borda de subida)
  attachInterrupt(digitalPinToInterrupt(pinoClockR), leBitISR, RISING);
  
  Serial.println("=====================================");
  Serial.println("Receptor (Paridade Par) Iniciado");
  Serial.println("Aguardando conexao...");
  Serial.println("=====================================");
}

void loop() {
  // PASSO 1 e 2: Verifica se o Emissor levantou o RTS (pediu para falar) e se não estamos no meio de uma recepção
  if (digitalRead(pinoRTSR) == HIGH && !recebendo) {
    recebendo = true;
    dadoRecebido = 0;
    bitAtualR = 0;
    
    // Responde ao Emissor: "Estou pronto!"
    digitalWrite(pinoCTSR, HIGH);
    Serial.println("\n[Handshake] RTS detectado. Respondendo CTS = 1.");
    Serial.println("[Handshake] Recebendo dados...");

    // PASSO 5: Aguarda os dados chegarem via interrupção. O laço fica "preso" aqui enquanto o Emissor mantiver o RTS em HIGH.
    while (digitalRead(pinoRTSR) == HIGH) {
      // Loop ocioso aguardando a transmissão finalizar
    }

    // PASSO 6: O Emissor baixou o RTS, sinalizando o fim da transmissão.
    Serial.println("[Handshake] RTS baixou. Fim da recepcao.");
    
    // PASSO 6.1: Valida a paridade do pacote recém-chegado e exibe o resultado
    verificarParidadeEImprimir();

    // PASSO 7: Encerra o ciclo de Handshake baixando o CTS
    digitalWrite(pinoCTSR, LOW);
    recebendo = false;
  }
}

// ==========================================
// ROTINA DE INTERRUPÇÃO (Clock do Emissor)
// ==========================================
void leBitISR() {
  // Executa apenas se o Handshake estiver ativo e ainda não recebemos os 9 bits
  if (recebendo && bitAtualR < 9) {
    int valorBit = digitalRead(pinoRXR); // Lê o estado do pino 13
    
    if (bitAtualR < 8) {
      // Reconstrói o byte de dados (os 8 primeiros bits)
      bitWrite(dadoRecebido, bitAtualR, valorBit);
    } else {
      // O nono bit (índice 8) é o bit de paridade
      paridadeRecebida = valorBit;
    }
    bitAtualR++;
  }
}

// ==========================================
// CONTROLE DE ERROS (Paridade Par)
// ==========================================
void verificarParidadeEImprimir() {
  int contadorDeUns = 0;
  
  // Conta o número de bits em nível lógico '1' nos dados
  for (int i = 0; i < 8; i++) {
    if (bitRead(dadoRecebido, i) == 1) {
      contadorDeUns++;
    }
  }
  
  // Adiciona o bit de paridade à contagem total
  if (paridadeRecebida == 1) {
    contadorDeUns++;
  }

  // Se a quantidade total de bits '1' for par, a transmissão foi bem sucedida
  if (contadorDeUns % 2 == 0) {
    Serial.print(">>> Sucesso! Caractere recebido: ");
    Serial.println((char)dadoRecebido);
  } else {
    Serial.print(">>> Erro de Paridade! Pacote corrompido. Dado incorreto: ");
    Serial.println((char)dadoRecebido);
  }
}
