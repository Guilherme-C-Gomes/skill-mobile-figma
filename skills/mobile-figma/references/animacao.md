# Animação e movimento

Movimento tem função: dizer de onde a coisa veio, o que mudou e se o sistema está trabalhando. Animação que só enfeita atrasa a pessoa e é a primeira coisa que o usuário frequente passa a odiar.

Duas entregas diferentes moram aqui: o **Prototype nativo do Figma**, que a pessoa clica e aprova, e a **spec de motion**, que o dev implementa. Prototype sem spec vira "faz parecido com o Figma" e cada tela sai diferente.

## Tokens de movimento

Defina junto com os tokens de cor, pelo mesmo motivo: sem escala, cada transição sai com uma duração inventada.

```
motion-instant   100ms   feedback de toque, mudança de estado de botão
motion-fast      150ms   hover, foco, tooltip, checkbox
motion-base      200ms   dropdown, accordion, troca de aba
motion-medium    300ms   modal, bottom sheet, transição entre telas
motion-slow      400ms   entrada de tela cheia, onboarding
```

Duas regras que evitam a maior parte dos erros:

**Saída é mais rápida que entrada.** Elemento que sai não precisa ser compreendido, só sumir. Entrada em 300ms costuma sair bem em 200ms.

**Distância maior pede duração maior.** Bottom sheet que sobe a tela inteira em 150ms parece um susto; badge que muda de cor em 400ms parece travamento. Se um elemento percorre o dobro da distância, some algo em torno de 50%, não o dobro.

Acima de 400ms a pessoa percebe como espera. Abaixo de 100ms ela não percebe que houve transição, o que às vezes é exatamente o que se quer.

## Easing

Easing é o que separa movimento vivo de movimento mecânico. Linear só existe para coisa que gira sem parar, como spinner.

| Curva | Uso | Por quê |
|---|---|---|
| **ease-out** | Entrada: elemento que aparece, painel que abre | Começa rápido e desacelera. Parece que responde na hora |
| **ease-in** | Saída: elemento que some, painel que fecha | Acelera para fora. Não rouba atenção na despedida |
| **ease-in-out** | Movimento entre dois pontos visíveis, reordenação de lista | Simétrico, natural para quem acompanha o percurso |
| **spring** | Ação com peso: arrastar, curtir, pull to refresh | Overshoot dá materialidade. Cuidado: em interface de trabalho irrita rápido |
| **linear** | Rotação contínua, barra de progresso indeterminada | Só onde não há começo nem fim |

Valores em CSS que funcionam como padrão:

```
ease-out       cubic-bezier(0.0, 0.0, 0.2, 1)
ease-in        cubic-bezier(0.4, 0.0, 1, 1)
ease-in-out    cubic-bezier(0.4, 0.0, 0.2, 1)
spring suave   cubic-bezier(0.34, 1.30, 0.64, 1)
```

Na API do Figma, os nomes públicos são `EASE_OUT`, `EASE_IN`, `EASE_IN_AND_OUT` (nunca `EASE_IN_OUT`, que é alias inválido) e `EASE_IN_AND_OUT_BACK`.

## O que animar

Anime `opacity` e `transform`. As duas rodam na GPU e não recalculam layout. Animar `width`, `height`, `top`, `left` ou `margin` força reflow e trava em lista longa e em celular fraco. Quando precisar de crescimento, prefira `transform: scale`.

Deslocamento de entrada curto: de 8 a 16px em mobile, até 24 em desktop. Elemento que entra vindo de longe parece pesado e atrasa a leitura.

**Stagger** (atraso em cascata) em lista: de 30 a 50ms entre itens, limitado aos 5 ou 6 primeiros. Cascata em vinte itens faz o último aparecer quase um segundo depois, e aí a lista parece lenta.

## Onde o movimento ganha o lugar dele

Cinco momentos em que a animação paga o custo:

1. **Origem e destino.** Modal que cresce do botão que o abriu ensina a relação. Modal que aparece no centro do nada não ensina nada.
2. **Carregamento.** Skeleton com a forma do conteúdo real, com pulso lento de 1.5 a 2s. Spinner solto no meio da tela é a opção de quando não se sabe o formato do que vem.
3. **Confirmação.** Sucesso precisa de um sinal curto, de 200 a 300ms. Sem ele a pessoa clica de novo.
4. **Mudança de estado.** Item que sai de uma lista deve sumir com transição, senão o resto "pula" e a pessoa perde o lugar.
5. **Continuidade entre telas.** Elemento compartilhado que persiste entre a lista e o detalhe mantém o contexto. É exatamente o caso do Smart Animate.

E onde ele atrapalha: animação em ação repetida dezenas de vezes por dia, animação bloqueando entrada de dado, e qualquer coisa que a pessoa precise esperar terminar para clicar.

## Prototype nativo no Figma

O Prototype é o que a pessoa consegue clicar e aprovar antes de existir código.

**Pré-requisito**: os frames precisam existir e estar nomeados. Prototype ligando frames com nome genérico vira um emaranhado que ninguém mantém.

Montagem, na ordem:

1. **Defina o frame inicial** do fluxo.
2. **Ligue as ações principais** de cada tela ao destino, com o gatilho certo: toque para botão, arrastar para carrossel e bottom sheet, `while hovering` para menu de desktop.
3. **Escolha a animação da ligação**: `Instant` para navegação lateral entre abas, `Move in` ou `Push` para avanço em fluxo linear, `Slide up` para bottom sheet e modal, `Smart Animate` quando há elemento compartilhado.
4. **Cubra a volta.** Fluxo que só vai para frente não testa nada. Ligue o voltar, o fechar do modal e o cancelar.
5. **Ligue os estados**, não só as telas: vazio para com dados, campo em repouso para campo com erro. É aí que o Prototype vira ferramenta de decisão em vez de slideshow.

### Smart Animate

Smart Animate interpola entre dois frames casando camadas por **nome e posição na hierarquia** — os dois, não um ou outro ([documentação do Figma](https://help.figma.com/hc/en-us/articles/360039818874-Smart-animate-layers-between-frames)). Camada com nome diferente, ou com o mesmo nome dentro de outro pai, não casa: ela some e a outra aparece.

Por isso a convenção de nomes não é burocracia. É a única coisa que faz o Smart Animate funcionar.

Regras práticas:

- Nome idêntico **e** mesmo pai nos dois frames.
- Anime posição, tamanho, opacidade, cor e rotação. Mudança de conteúdo de texto interpola mal.
- Duração de 200 a 300ms com ease-out cobre quase tudo.
- Elemento que existe só no frame de destino entra com fade automático. Se quiser controle, ponha ele nos dois frames com opacidade 0 na origem.
- Sombra (drop shadow, inner shadow) **impede** o Smart Animate: o Figma cai para dissolve sem avisar.

## Por que a animação não saiu no Figma

Diagnóstico das duas causas que respondem por quase todos os casos de "no protótipo HTML funciona e no Figma não".

### Causa 1: um quadro só

Toda animação no Figma é interpolação entre **dois estados**. Se existe um frame só, não há o que interpolar — e nenhum CSS bem escrito no protótipo muda isso. Brilho que varre, esqueleto que pulsa, número que sobe: todos precisam de par.

O padrão para varredura é um retângulo com gradiente diagonal que **descansa fora da tela nas duas pontas**:

```
03 Carregando       → reflexo em x = -260   (fora, à esquerda)
03b Carregando lendo → reflexo em x = +430  (fora, à direita)
```

Ligue os dois com Smart Animate e o reflexo atravessa. Como ele está fora do frame em ambos os repousos, só aparece durante o percurso. Isso exige `clipsContent = true` no frame, senão ele fica à vista parado ao lado da tela.

Cascata de várias peças (letras de uma marca entrando uma a uma) pede um quadro por grupo de peças, não um por peça: dois ou três quadros costumam bastar, revelando duas peças por vez.

### Causa 2: o indicador mora dentro do grupo errado

Um indicador que precisa **viajar** entre telas — a pílula da aba ativa, o sublinhado da tab, o ponto do carrossel — não pode morar dentro do grupo do item ativo. Numa tela ele seria `Nav_Inicio_Pill` dentro de `Nav_Inicio`; na outra, `Nav_Ajustes_Pill` dentro de `Nav_Ajustes`. Nome diferente, pai diferente: falha nos dois critérios, e o Figma cai para dissolve.

A correção é tirá-lo dos grupos e deixá-lo como irmão de nome fixo:

```
Nav_Bottom
  Nav_Fundo
  Nav_Lente_Halo     ← sempre este nome, sempre aqui, só o x muda
  Nav_Lente
  Nav_Lente_Brilho
  Nav_Inicio  (alvo + ícone)
  Nav_Participantes
  …
```

E a transição entre abas precisa ser **Smart Animate**, não Instant nem Dissolve — é a transição que carrega a viagem.

### Como confirmar em vez de adivinhar

Quando algo não sai como esperado no Figma, o problema quase nunca é o desenho: é uma regra da plataforma. Nome de camada, hierarquia, número de quadros, efeito bloqueante e tipo de transição respondem pela maioria. Consulte `help.figma.com` antes de tentar outra coisa, e diga à pessoa qual era a regra — isso encurta a rodada seguinte.

### Quando o conector estiver ativo

O conector do Figma consegue escrever movimento no arquivo, com keyframes manuais, estilos de animação e duração de timeline. Isso é uma camada diferente de Prototype: Prototype liga frames, motion anima nós dentro de um frame.

Antes de qualquer chamada de escrita de movimento, carregue as skills do próprio conector: `figma-use` mais `figma-use-motion`. Elas são pré-requisito obrigatório e pulá-las gera erro difícil de diagnosticar.

Dois limites que valem saber de antemão:

- **As APIs de motion são liberadas por flag de conta.** Se a chamada responder que a API não é suportada, o recurso não está habilitado para essa conta. Diga isso à pessoa, entregue a spec de motion e o Prototype, e siga. Não fique repetindo a chamada.
- **Captura de tela mostra só o estado em repouso.** Para conferir movimento é preciso exportar vídeo, que é lento e caro. Faça isso só quando a correção não for evidente, e extraia vários quadros de uma exportação só em vez de exportar de novo a cada ajuste.

## Efeitos que só existem via plugin

Desfoque de fundo não cabe em SVG e `createNodeFromSvg` também não carrega. Se o design usa vidro, o material só fica completo quando o plugin aplica o efeito depois da importação:

```js
no.effects = [{ type: 'BACKGROUND_BLUR', radius: 28, visible: true }];
```

Ver `references/plugin-figma.md` e `references/material-vidro.md`.

## Spec de motion para o dev

Sem isso, cada tela sai com uma animação diferente. Formato que o front-end implementa direto:

```
Interação: abrir bottom sheet de filtros
Gatilho:   toque em "Filtrar"
Anima:     transform translateY de 100% para 0
           overlay opacity de 0 para 1
Duração:   300ms sheet, 200ms overlay
Easing:    ease-out cubic-bezier(0, 0, 0.2, 1)
Saída:     200ms ease-in, mesma propriedade invertida
Reduzido:  sem deslocamento, só fade de 100ms
```

Entregue uma dessas por interação relevante — normalmente de 5 a 8 cobrem o app inteiro, porque a maioria das transições se repete.

## Movimento reduzido

`prefers-reduced-motion` não é detalhe de acessibilidade opcional: movimento grande dispara enjoo e tontura de verdade em quem tem sensibilidade vestibular.

A alternativa não é remover o feedback, é trocar deslocamento por opacidade:

- Slide vira fade.
- Escala e overshoot viram mudança direta.
- Parallax e movimento automático de fundo desaparecem.
- Feedback de estado continua existindo, só que sem percurso.

Registre isso na spec como uma linha "Reduzido:" por interação, como no exemplo acima. É o campo que o dev mais esquece e o mais barato de incluir.
