##  Guia de Execução no Tinkercad (Passo a Passo)

Para validar este projeto no simulador, podes aceder ao projeto já configurado ou montá-lo do zero seguindo as instruções abaixo:

###  Link do Projeto Pronto
[**Acessar Simulação no Tinkercad**](https://www.tinkercad.com/things/c15tYW3SdmV/editel?sharecode=Aab0_H0qePabNXiK02hk2zRKYodX9ZJCAUkQrbtBxq8)

---

### 1. Preparação dos Componentes
1. Acesse o [Tinkercad Circuits](https://www.tinkercad.com/).
2. Adiciona **duas placas Arduino Uno R3** à área de trabalho.
3. Nomeia a placa superior como **Emissor** e a inferior como **Receptor**.

### 2. Montagem do Circuito (Cablagem)
Conecta os pinos entre as duas placas seguindo esta tabela de cores para facilitar a identificação visual:

| Sinal Físico | Cor do Fio | Pino (Emissor) | Pino (Receptor) | Função Teórica |
| :--- | :--- | :---: | :---: | :--- |
| **GND** | Preto | GND | GND | Referência elétrica comum (Obrigatório) |
| **Dados (TX/RX)** | Amarelo | 13 | 13 | Linha de transmissão dos bits (Camada Física) |
| **Clock** | Azul | 12 | 2 | Sincronização síncrona (Interrupção no pino 2) |
| **RTS** | Verde | 4 | 4 | Handshake: Request to Send |
| **CTS** | Laranja | 5 | 5 | Handshake: Clear to Send |

### 3. Configuração do Código
Para cada placa, realiza os seguintes passos:
1. Clica na placa pretendida.
2. Abre o painel **Código** no canto superior direito.
3. Altera o modo de visualização de "Blocos" para **"Texto"**.
4. **Para o Emissor:** Cola o conteúdo de `Emissor.ino`. *Nota: Como o Tinkercad não aceita ficheiros .h separados, as funções do Temporizador devem estar no final deste ficheiro.*
5. **Para o Receptor:** Cola o conteúdo de `Receptor.ino`.

### 4. Simulação e Teste de Comunicação
1. Clica em **Iniciar Simulação**.
2. Abre o **Monitor Serial** na parte inferior do ecrã.
3. Certifica-te de que o Monitor Serial do **Emissor** está selecionado para escrita.
4. Digita um caractere (ex: `a`) e prime **Enter**.
5. No Monitor Serial do **Receptor**, verás o processo de Handshake e a mensagem: `>>> Sucesso! Caractere recebido: a`, confirmando que a paridade par foi validada.