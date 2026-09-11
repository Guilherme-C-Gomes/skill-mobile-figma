# Fluxo e arquitetura de informação

Como sair de "quero um app de X" para uma lista de telas defensável.

## 1. Job principal

Escreva em uma frase, no formato: *quando [situação], o usuário quer [motivação], para conseguir [resultado]*.

Exemplo: quando o corretor recebe um lead novo no fim do dia, ele quer responder antes do concorrente, para não perder a oportunidade.

Essa frase decide o que é a tela inicial. Se a tela inicial não serve ao job principal em um toque, ela está errada.

## 2. Fluxo em etapas

Liste o caminho do usuário como uma sequência numerada, com decisão explícita em cada ponto de bifurcação.

```
1. Abre o app pela primeira vez
2. Vê a proposta de valor          -> Onboarding (3 telas)
3. Cria conta ou entra             -> Bifurcação: novo ou existente
4. Preenche o mínimo indispensável -> Cadastro curto
5. Chega na Home com dado vazio    -> Estado vazio que ensina
6. Executa o job principal         -> Tela núcleo
7. Vê o resultado                  -> Confirmação
```

Regra de corte: cada etapa a mais entre o passo 1 e o job principal derruba conversão. Se o fluxo tem mais de cinco passos até o primeiro valor entregue, questione em voz alta o que dá para adiar para depois.

## 3. Lista de telas

Derive do fluxo. Para cada tela registre quatro coisas:

| Campo | Para que serve |
|---|---|
| Nome | Vira o nome do arquivo e do frame |
| Decisão do usuário | Se não há decisão nem consumo de informação, a tela não precisa existir |
| Dados na tela | Define a densidade e o layout |
| Saídas | Para onde se vai a partir dali |

## 4. Estados obrigatórios

Para cada tela que mostra dados, desenhe cinco versões. Ignorar isso é a causa número um de retrabalho no front-end.

1. **Vazio**: usuário novo, sem nada cadastrado. Deve ensinar o primeiro passo, com uma ação clara.
2. **Carregando**: skeleton com a forma do conteúdo real, não spinner solto no meio da tela.
3. **Com dados**: o caso normal. Desenhe com conteúdo realista, incluindo o nome mais longo que pode aparecer.
4. **Erro**: falha de rede ou de permissão, com o que fazer a seguir.
5. **Parcial ou limite**: lista com um item só, e lista com muitos itens, para testar a paginação e o corte de texto.

Nem toda tela precisa das cinco em arquivo separado. Priorize as três telas de maior tráfego e trate o resto por descrição.

## 5. Hierarquia dentro da tela

Ordene por importância decidida, não por estética. Método rápido:

- O que o usuário precisa ver em meio segundo fica no topo, com o maior peso tipográfico da tela.
- A ação primária é única e visualmente inconfundível. Duas ações primárias competindo significam zero ação primária.
- Ações destrutivas ficam longe das construtivas e nunca são a mais proeminente.
- Informação de apoio pode ser secundária em cor e tamanho, sem cair abaixo do contraste mínimo.

## 6. Navegação

Escolha um padrão e mantenha:

- **Tab bar** (3 a 5 itens): quando as seções são paralelas e o usuário alterna com frequência.
- **Stack com voltar**: quando o fluxo é linear e profundo.
- **Drawer lateral**: quando há muitas seções de uso pouco frequente. Custa descoberta, use com parcimônia.
- **Web**: navegação horizontal no topo até sete itens, sidebar quando houver hierarquia de segundo nível.

Registre a escolha e o motivo no README da entrega, porque isso volta como pergunta depois.

A navegação escolhida já decide o movimento: seção paralela em tab bar troca sem transição de percurso, fluxo linear empurra para o lado, e detalhe aberto a partir de uma lista pede continuidade do elemento compartilhado. Anote a transição junto com cada ligação do fluxo, seguindo `animacao.md`, para não deixar essa decisão para o dev na pressa.

## 7. Validação antes de desenhar

Confirme com a pessoa antes de partir para as telas. Mostre o fluxo e a lista de telas, e pergunte de forma direta se falta alguma etapa ou se alguma tela pode cair. Corrigir um item de lista custa um minuto, redesenhar oito telas custa a sessão inteira.
