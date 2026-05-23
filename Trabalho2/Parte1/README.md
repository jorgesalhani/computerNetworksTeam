## Projeto
Enquete inteligente, com base em modelo de controle de estoque

## Funcionalidades

### Cadastro de nova enquete

**Protocolo de conteúdo**
- opcode | label | question1 | question2 | question3 | ...

opcode = w

label = título da enquete (única)

[Visão geral](Cadastrar/geral.png)

[Fluxo completo](Cadastrar/completo.png)

### Obter enquete

**Protocolo de conteúdo**
- opcode | label

opcode = r

label = título da enquete

[Visão geral](ObterEnquete/geral.png)

[Fluxo completo](ObterEnquete/completo.png)
