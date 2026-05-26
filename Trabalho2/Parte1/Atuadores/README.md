# Atuadores

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

## Sistema de iluminação

DATA:
1. modo_iluminacao

## Alimentador do projetor

DATA:
1. modo_projetor

## Alimentador do ar-condicionado

DATA:
1. modo_ar_condicionado