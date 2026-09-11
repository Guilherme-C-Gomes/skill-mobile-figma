# Layout

A etapa que quase todo mundo pula. Cor e sombra são o que se percebe; layout é o que faz a tela parecer profissional ou amadora sem que a pessoa saiba explicar por quê.

Layout resolve quatro perguntas, nesta ordem: **onde as coisas ficam** (grid), **quanto respiro têm** (ritmo), **como se alinham** (ordem) e **o que acontece quando a largura muda** (responsividade).

## Grid por plataforma

O grid não é enfeite de designer: é o que garante que dez telas feitas em momentos diferentes pareçam do mesmo produto.

```
Mobile 390          margem 16   1 coluna     gutter 16
Mobile 360          margem 16   1 coluna     gutter 12
Tablet 834          margem 24   8 colunas    gutter 16
Desktop 1440        margem 80   12 colunas   gutter 24   conteúdo máx 1200
Desktop denso       margem 24   12 colunas   gutter 16   conteúdo largura total
```

Margem em mobile abaixo de 16 aperta o texto contra a borda e a leitura piora de verdade, não é preferência. Acima de 24 desperdiça largura numa tela que já é estreita.

Em web, conteúdo de leitura corrida vive entre 60 e 75 caracteres por linha. Passou disso, o olho perde a linha na volta. Isso costuma dar de 640 a 720px de largura de texto, mesmo num container de 1200.

## Orçamento vertical em mobile

Em celular o espaço não é elástico: é um orçamento fechado, e vale fazer a conta **antes** de desenhar. Em 390×844 com barra inferior flutuante:

```
hero / cabeçalho        156
filtros (pílulas)        44   + 14 de respiro
campo de busca           48   + 28
overline de seção        ~28
─────────────────────────────
sobra para cards        ~390  →  TRÊS cards de ~130 com vãos de 12
barra inferior           60   a partir de y = 752
```

Cabem três cards. O quarto não cabe, e insistir nele produz o defeito que a pessoa vai apontar em seguida: metade do card escondida atrás da barra. Quando a informação não couber, dobre ela dentro de um card existente — "próximo treino" cabe como segunda linha do card de presença — em vez de espremer mais um.

Duas linhas que o conteúdo não deve cruzar, e que valem como checagem automática:

- **nenhuma linha de base de texto abaixo de 706** — dali para baixo o véu já apaga;
- **nenhuma caixa terminando depois de 748** — dali em diante fica atrás da barra e lê como elemento cortado.

Lista é a exceção parcial: linha que desaparece sob o véu lê como "tem mais, role" e é o comportamento certo. Card informativo cortado no meio não lê como nada além de defeito.

O orçamento muda com a tela. Em 360×800 (Android médio), margem e conteúdo caem de 20/350 para 16/328 e sobra espaço para dois cards e meio — o terceiro passa a ser a peça que rola.

## Ritmo vertical

O espaçamento comunica agrupamento antes de qualquer borda ou fundo. Proximidade é a pista mais forte que existe.

A regra que resolve 90% dos casos: **o espaço entre grupos é maior que o espaço dentro do grupo**. Se o rótulo está a 8px do campo e o campo seguinte está a 8px também, o olho não sabe o que pertence a quê.

```
dentro de componente      4 a 8
entre componentes irmãos  12 a 16
entre blocos relacionados 24
entre seções              32 a 48
respiro de topo de tela   48 a 64
```

Todo valor sai da escala de 4. Se 18px parece necessário, o problema está no tamanho de outra coisa, não no espaçamento.

Erro clássico: padding vertical maior que o horizontal em card, ou o contrário, sem motivo. Card com padding 16 em cima e 24 nas laterais parece torto e ninguém consegue apontar onde.

## Auto layout

No Figma, auto layout é o que faz o arquivo sobreviver a uma mudança de conteúdo. Sem ele, trocar um texto por um mais longo quebra a tela e alguém reposiciona tudo na mão.

O que vira auto layout:

- Qualquer pilha vertical de blocos: a tela inteira, o conteúdo de um card, um formulário.
- Qualquer linha de itens: cabeçalho, barra de ações, linha de tags, rodapé de botões.
- Listas e grades de card.

O que fica posicionado à mão: elemento decorativo, sobreposição, badge ancorado num canto, marca d'água.

Configuração que evita retrabalho:

- **Direção e espaçamento** vindos da escala, nunca digitados avulso.
- **Padding** igual ao token da tela, não valor arredondado no olho.
- **Alinhamento** explícito. Item de lista alinhado ao topo quando os textos têm alturas diferentes, centralizado quando têm a mesma.
- **Preencher container** (fill) no elemento que deve crescer, **abraçar conteúdo** (hug) no que deve encolher. Botão de largura total em mobile é fill; chip de tag é hug.
- **Espaço entre itens** (space between) para empurrar ação para a borda oposta, em vez de spacer vazio.

No caminho SVG isso não existe: o SVG carrega posição absoluta. Por isso o README precisa dizer onde aplicar auto layout depois de importar, e por isso o HTML com flexbox importado via `html.to.design` chega mais perto de um arquivo pronto.

## Alinhamento

Alinhamento é a diferença mais barata entre amador e profissional.

- **Uma borda de alinhamento por lado.** Todo conteúdo começa na mesma margem esquerda. Cada exceção precisa de motivo.
- **Alinhamento ótico ganha do matemático** quando a forma engana o olho. Ícone de play centralizado matematicamente dentro de círculo parece deslocado para a esquerda; empurre alguns pixels. Vale para triângulo, seta e letra com haste.
- **Texto e ícone na mesma linha** alinham pela linha de base ótica, não pela caixa. Ícone de 20px ao lado de texto de 16px costuma pedir 1 a 2px de ajuste.
- **Números em coluna alinham à direita** e usam variante tabular da fonte, senão a coluna dança a cada dígito.

## Densidade

Densidade é decisão de produto, não de gosto. Escolha uma e mantenha na tela inteira; densidade que muda de bloco para bloco é o que faz a tela parecer costurada de pedaços.

| Densidade | Altura de item | Padding | Quando |
|---|---|---|---|
| Confortável | 56 a 64 | 16 | Uso ocasional, consumidor final |
| Padrão | 48 | 12 a 16 | Maioria dos casos |
| Compacta | 36 a 40 | 8 | Operador que passa o dia na tela, muito dado |

Compacta só funciona com contraste e alinhamento impecáveis, porque perde a folga que perdoa erro.

## Responsividade

Design entregue em uma largura só força o dev a inventar, e ele vai inventar diferente do que você imaginou. Descreva o comportamento mesmo quando não desenhar todas as larguras.

Pontos de quebra usuais:

```
até 599      mobile      1 coluna, navegação inferior, ação fixa no rodapé
600 a 904    tablet      2 colunas, navegação pode ir para o topo
905 a 1239   laptop      conteúdo centralizado com máximo, sidebar aparece
1240+        desktop     12 colunas, sidebar fixa, tabela com todas as colunas
```

Para cada bloco importante, registre em uma linha: o que empilha, o que some, o que vira menu, e o que muda de posição. Tabela é o caso mais delicado — decida quais colunas caem primeiro e se as restantes viram card empilhado.

## O que denuncia design amador

Lista de checagem rápida, na ordem em que o olho pega:

- Espaçamento fora da escala, tipo 13px, 27px, 35px.
- Raio inconsistente: botão com 8 e campo com 6 na mesma tela.
- Duas ações competindo pelo mesmo destaque. Duas primárias significam nenhuma primária.
- Texto encostado na borda do container.
- Altura de linha padrão da ferramenta em texto corrido, apertado demais.
- Sombra forte demais, ou sombra em tudo, o que achata a hierarquia em vez de criar.
- Ícones de espessuras e famílias diferentes na mesma tela.
- Mais de duas famílias tipográficas.
- Cinza de texto secundário escolhido no olho, reprovando em contraste.
- Card com larguras diferentes na mesma lista.
- Estado vazio esquecido, aparecendo como um bloco em branco.

## Refino visual, na ordem certa

Quando a pessoa diz "está feio" mas não sabe apontar, ataque nesta ordem. Cada passo revela o próximo, e mexer em cor antes de resolver estrutura é maquiar problema.

1. **Alinhamento** — colocar tudo nas mesmas bordas.
2. **Espaçamento** — tudo na escala, agrupamento por proximidade.
3. **Hierarquia tipográfica** — no máximo três tamanhos por tela, contraste feito com peso.
4. **Cor** — reduzir a quantidade de cores, deixar a cor da marca para a ação principal.
5. **Profundidade** — escolher entre borda e sombra, não os dois no mesmo elemento.
6. **Detalhe** — raio consistente, ícone da mesma família, alinhamento ótico.

Na prática, os passos 1 e 2 sozinhos resolvem a maioria dos "está feio", e são os mais rápidos de aplicar.
