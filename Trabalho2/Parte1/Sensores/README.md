# Sensores

## Protocolo

HEADER | DATA 

HEADER: 
1. **id_sensor**: identificador da componente
2. **tipo_componente**: tipo da componente
3. **aceitar_sinal**: flag (0|1) para que o sinal recebido seja efetivamente reconhecido como um comando

> **Hipótese:**
> 
> Existe uma lista com cada componente previamente cadastrada

DATA:
1. dados (a depender do sensor)

## Presença de pessoas

DATA:
1. sala_vazia

## Leitor de cartão de alunas

DATA:
1. nome_aluna
2. numero_aluna

## Chave ON/OFF do projetor

DATA:
1. modo_projetor