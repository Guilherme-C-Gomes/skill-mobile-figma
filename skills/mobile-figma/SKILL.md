---
name: mobile-figma
description: Desenha o app mobile inteiro — fluxo, design system, telas, estados, movimento — e entrega dentro do Figma, por conector, por plugin local ou por arquivos prontos para importar. Use sempre que o pedido envolver app, aplicativo, celular, iOS, Android, tela de app, Figma, UI, UX, interface, protótipo, wireframe, mockup, fluxo de usuário, layout, design system, tokens, componentes, estados de tela, animação, motion, transição, microinteração, Smart Animate, barra de navegação, bottom sheet, alvo de toque, acessibilidade, contraste, WCAG, UX writing ou handoff para dev. Use também quando a pessoa só descreve a situação ("preciso desenhar o app", "quero ver antes de mandar pro dev", "isso ficou feio", "esse botão ficou estranho", "tá vazando o texto", "some com essa faixa"). Use ainda para revisar ou consertar telas de Figma que a pessoa colar, subir, conectar ou mandar print — inclusive print de detalhe pedindo um ajuste pontual.
---

# Mobile Figma

Skill de ponta a ponta para UI/UX de aplicativo: diagnóstico, fluxo, design system, layout, telas desenhadas, movimento, auditoria e handoff. Foco em mobile — 390×844 como referência, dedo como ponteiro, barra inferior, safe area.

Três princípios organizam tudo aqui.

**Decisão errada barata vem antes de decisão cara.** Fluxo antes de layout, layout antes de pixel, pixel antes de movimento. Quem inverte desenha bonito a coisa errada e descobre tarde.

**Gere, não desenhe.** A partir de três ou quatro telas, escrever um gerador em Python que cospe os SVGs vence desenhar tela por tela — não por elegância, mas porque toda correção passa a ser sistêmica. A pessoa vai dizer "esse chip está muito oval" olhando uma tela, e a correção precisa valer nas dez. Ver `references/gerador.md`.

**Meça, não estime.** Largura de texto, contraste, sobreposição e distribuição são conta, não olho. A maior parte do que a pessoa reclama depois — texto vazando do botão, coisa desalinhada, elemento atrás da barra — é erro de estimativa que um script pega antes da entrega. Ver `references/validadores.md`.

## Passo zero: descobrir onde a entrega vai cair

Antes de qualquer coisa, veja o que a sessão tem. Isso muda a entrega inteira, então não adivinhe: teste chamando `mcp__Figma__whoami`.

| Situação | Caminho | Entrega |
|---|---|---|
| `mcp__Figma__*` responde e há cota | **A — conector** | Frames, variáveis e Prototype criados direto no arquivo |
| Conector sem cota, ou muitas telas, ou o trabalho vai se repetir | **C — plugin local** | Um plugin de desenvolvimento que carrega o projeto inteiro dentro dele e escreve no arquivo com **zero chamada de API** |
| Sem conector e sem Figma desktop | **B — arquivos** | SVG por tela e HTML clicável, para a pessoa importar |

O caminho C é o menos óbvio e quase sempre o certo em projeto de app inteiro. O plano Starter do Figma dá **20 chamadas por mês** — não cobre nem uma rodada de dez telas, e cada ajuste depois queima mais. O plugin resolve isso de vez e ainda vira um ciclo de trabalho: você inspeciona pela web, diagnostica, entrega o protótipo para aprovação, troca os arquivos na pasta do plugin, e a pessoa só aperta "Rodar". Ver `references/plugin-figma.md`.

Diga em uma frase qual caminho você vai seguir e por quê. E **nunca prometa mais do que o caminho permite**: no caminho B a frase honesta é "entrego as telas prontas para importar", não "vou criar no seu Figma".

Detalhes: `references/figma-mcp.md` (A), `references/plugin-figma.md` (C), `references/export-figma.md` (B).

## Roteamento por tipo de pedido

| Situação | Modo | Onde ir |
|---|---|---|
| App novo, nada desenhado | **Criar** | Fluxo padrão abaixo |
| Já existe arquivo, link, print | **Auditar** | `references/diagnostico.md` → `references/auditoria-e-handoff.md` |
| Padronizar cor, tipografia, componentes | **Sistema** | `references/design-system.md` |
| "Está feio", "não gostei", "melhora isso" | **Refinar** | `references/layout.md` + `references/diagnostico.md` |
| Print de um detalhe: "isso ficou estranho" | **Corrigir** | Ciclo de correção, mais abaixo |
| Design pronto, quer código ou specs | **Handoff** | `references/auditoria-e-handoff.md` |
| Transição, movimento, protótipo navegável | **Movimento** | `references/animacao.md` |
| "Faz igual a esse app aqui" + vídeo ou print | **Copiar referência** | `references/referencia-visual.md` |

Os modos se combinam. "Melhora meu app" quase sempre é diagnóstico + refino + movimento.

---

## Fluxo padrão

### Etapa 0 — Diagnóstico interativo

Define a qualidade de tudo que vem depois. Briefing raso produz tela genérica, e tela genérica é a reclamação número um.

**Pergunte com `AskUserQuestion`, não com texto corrido.** Parágrafo faz a pessoa responder metade; opção clicável ela responde inteira em segundos. No máximo quatro perguntas por rodada, 2 a 4 alternativas concretas cada, a que você recomendaria em primeiro lugar.

Regra de ouro: **não pergunte o que já foi dito.** Releia a mensagem, extraia tudo que dá para inferir, pergunte só o buraco.

`references/diagnostico.md` traz as baterias por tipo de app e o que fazer quando a resposta é "sei lá, faz do seu jeito". Se a pessoa mandar seguir, siga com premissas explícitas — bloquear por falta de briefing perfeito custa mais que assumir e mostrar.

### Etapa 1 — Fluxo e arquitetura

Mapeie o caminho antes do pixel. Entregue no chat: fluxo principal numerado, lista de telas com a decisão que o usuário toma em cada uma, e os estados por tela (vazio, carregando, erro, sucesso, com dados).

Peça confirmação aqui. Mudar item de lista custa um minuto; redesenhar dez telas custa a sessão. Método em `references/fluxo-e-arquitetura.md`.

### Etapa 2 — Design system enxuto

Tokens antes de telas. O mínimo: espaçamento, escala tipográfica, paleta semântica, raio, elevação, estados, e **movimento** (duração e easing) — que quase sempre é esquecido e vira decisão do dev na pressa.

Nos caminhos A e C os tokens viram **variáveis de verdade no Figma**. É o que separa um arquivo que a equipe usa de um que ninguém mantém. Escalas em `references/design-system.md`.

### Etapa 3 — Layout e orçamento de tela

Etapa mais pulada e causa número um de "ficou amador". Antes de cor e sombra, resolva estrutura: margem, ritmo vertical, alinhamento, densidade.

Em mobile o espaço é um orçamento fechado, e vale fazer a conta antes de desenhar. Em 390×844 com barra inferior:

```
hero / cabeçalho        156
filtros (pílulas)        44   + 14 de respiro
campo de busca           48   + 28
overline de seção        ~28
─────────────────────────────
sobra para cards        ~390  →  cabem TRÊS cards de ~130 com vãos de 12
barra inferior           60   a partir de y=752
```

O quarto card não cabe. Insistir nele produz exatamente o defeito que a pessoa vai apontar: metade do card escondida atrás da barra. Quando não couber, a saída é dobrar a informação dentro de um card que já existe, não espremer mais um.

Duas linhas que o conteúdo não deve cruzar, e que valem como regra automática: **nenhuma linha de base de texto abaixo de 706**, **nenhuma caixa terminando depois de 748**. Entre 706 e 752 o véu já apaga; depois de 752 fica atrás da barra e lê como elemento cortado, não como conteúdo rolando.

`references/layout.md` tem grid, densidade, ritmo e os erros que denunciam design amador.

### Etapa 4 — Desenhar as telas

**Caminho A**: monte no Figma seção por seção, reaproveitando componentes e variáveis que já existem antes de criar novos. Carregue as skills do próprio conector (`figma-use`, `figma-generate-design`) — são pré-requisito obrigatório e pulá-las gera falha difícil de depurar.

**Caminhos B e C**: SVG por tela, gerado por código. A partir de três telas, monte o gerador antes de desenhar (`references/gerador.md`) — o custo se paga na primeira correção. Regras de SVG que valem sempre estão em `references/export-figma.md`; as que mais custam caro se esquecidas:

- **Nomeie todo grupo.** O `id` vira o nome da camada, e nome de camada é o que faz o Smart Animate funcionar depois. Underscore, sem acento.
- **Texto como `<text>`, nunca path.** Vetorizado não é editável e mata o valor da entrega.
- **Cor por hex literal**, nunca `var()`.
- **Retângulo de fundo do tamanho do viewport** como primeiro elemento.
- **Largura de pílula, selo e botão sai de medição de texto**, nunca de chute. Ver `scripts/medida_texto.py`. Todo relato de "o nome está vazando do botão" nasce de largura chutada.

Nos três caminhos: comece por **três telas**, mostre, e só siga depois do aceite.

### Etapa 5 — Movimento

Movimento comunica de onde a coisa veio, o que mudou e se o sistema está trabalhando. Defina os tokens de movimento junto com os de cor e monte o Prototype ligando os frames.

Duas coisas que este método aprendeu apanhando, e que estão detalhadas em `references/animacao.md`:

**Um quadro não anima nada.** Toda animação no Figma precisa de dois estados. Brilho que varre, esqueleto que pulsa, letra que entra — se existe um frame só, não há o que interpolar, por mais bem escrito que esteja o CSS do protótipo HTML.

**O Smart Animate casa camadas por nome E por posição na hierarquia.** Um indicador que precisa viajar entre telas não pode morar dentro do grupo da aba: ele tem de ser sempre o mesmo nome, sempre filho do mesmo pai, mudando só a coordenada.

### Etapa 6 — Auto-diagnóstico

Antes de dizer "pronto", vire crítico do próprio trabalho. Rode os validadores:

```bash
python3 scripts/check_svg_figma.py caminho/das/telas/ --mobile
```

Corrija todo ERRO. AVISO é julgamento seu. O que cada checagem procura e por quê está em `references/validadores.md`.

Depois **devolva perguntas de refino**, não só o arquivo. A pessoa quase nunca sabe articular o que incomodou; sua função é oferecer os eixos de escolha. `AskUserQuestion` com no máximo três perguntas, cada uma sobre uma decisão que teria alternativa defensável. Catálogo em `references/diagnostico.md`.

### Etapa 7 — Entrega

**A**: link do arquivo, página, nomes dos frames. Liste o que você criou versus o que reaproveitou.

**C**: escreva os arquivos direto na pasta do plugin e peça só o hot reload. Diga o que o relatório do plugin vai mostrar.

**B**: salve em `/mnt/user-data/outputs/`, numerado na ordem do fluxo:

```
telas/
  00-design-system.svg
  01-splash.svg
  02-login.svg
  03-home.svg
README.md
```

O README traz: como importar, tokens em JSON, tokens de movimento, premissas assumidas, e o que ficou de fora.

Nos três casos, no chat escreva no máximo dois parágrafos. As telas falam por si.

---

## O ciclo de correção

Depois da primeira entrega, a maior parte do trabalho vira isto: a pessoa manda um print recortado com uma seta vermelha e uma frase curta — "ficou estranho", "está vazando", "remove essa faixa". Esse é o modo mais frequente da skill e vale ter método.

**Meça antes de concordar.** A frase da pessoa descreve o sintoma, não a causa, e a causa raramente está onde a seta aponta. "O Ajustes está desalinhado" pode ser a barra distribuindo por centros iguais com rótulos de larguras diferentes — a aba está perfeitamente centrada, o que está errado é o vão. Renderize, meça em pixels, e só então decida. Concordar rápido com o diagnóstico errado gasta uma rodada inteira.

**Conserte na origem, nunca na tela.** Se o gerador existe, a correção é uma linha no gerador e todas as telas mudam juntas. Correção aplicada num SVG só reaparece na próxima geração.

E a origem tem dois lados. Do lado do gerador, é a função. **Do lado do Figma, é o Auto Layout**: uma barra distribuída à mão volta a torcer na primeira vez que alguém editar um rótulo; a mesma barra em Auto Layout com espaçamento definido se redistribui sozinha. Sempre que corrigir uma distribuição, um alinhamento ou um espaçamento, diga também qual Auto Layout impede a volta — é o que faz a correção sobreviver depois que você sair da conversa.

**Varra as outras telas atrás do mesmo defeito.** A pessoa viu numa; quase sempre está em cinco. Vale rodar a medição no conjunto inteiro antes de responder.

**Todo defeito que escapou vira validador.** Foi assim que nasceram as quatro checagens de `references/validadores.md`: cada uma é um erro que chegou ao usuário uma vez. Acrescentar a checagem custa dez minutos e impede a classe inteira de voltar.

**Quando o defeito for no Figma e não no protótipo**, o problema quase nunca é o desenho — é uma regra da plataforma. Antes de adivinhar, confirme na documentação (`help.figma.com`) e diga qual regra era. Nome de camada, hierarquia, número de quadros e efeito de camada respondem pela maioria dos casos.

**Explique a causa em uma frase quando responder.** "Removi" ensina nada; "aquilo era o anel de foco, que numa tela parada só faz o campo parecer diferente sem motivo" ensina o critério e reduz a rodada seguinte.

---

## Acessibilidade: piso não negociável

Verifique em toda tela. Erro descoberto no handoff custa retrabalho de front-end inteiro.

- Contraste 4.5:1 para texto normal, 3:1 para texto grande (18pt, ou 14pt bold) e para elemento de interface.
- Alvo de toque de 44×44pt, sem sobrepor o vizinho.
- Estado de foco visível em tudo interativo, distinto do hover — mas documentado na folha do design system, não aceso numa tela parada, senão parece defeito.
- Informação nunca só por cor.
- Ordem de leitura lógica na hierarquia de camadas, porque ela vira ordem de tab no código.
- Movimento respeita `prefers-reduced-motion`.
- Barra de navegação só com ícone perde clareza para quem usa o app de vez em quando. Se a pessoa pedir, faça — e registre o nome no `aria-label` e no nome da camada, mantenha o alvo de toque na fatia inteira, e ofereça o meio-termo de mostrar o rótulo só na aba ativa.

Calcule contraste, não estime — a olho o erro acontece justamente entre 3:1 e 5:1. E calcule **sobre a cor composta**, não sobre o token: texto sobre vidro translúcido está sobre a mistura, não sobre o valor nominal.

```bash
python3 scripts/contraste.py "#667085" "#FFFFFF"
python3 scripts/contraste.py "#D06CF5" --sobre "#FFFFFF@0.16" "#0A0A12"
```

## UX writing dentro das telas

Texto de interface é design. Nunca escreva "Lorem ipsum" em tela que vai para aprovação: texto falso sempre tem o tamanho conveniente e esconde problema real de layout.

- Botão diz o que acontece: "Criar conta", não "Enviar".
- Erro diz o que fazer: "Senha precisa de 8 caracteres", não "Dados inválidos".
- Estado vazio ensina o primeiro passo.
- Rótulo acima do campo, sempre visível. Placeholder não substitui rótulo.
- Números das telas têm de bater entre si. Card dizendo "6 em queda" e lista mostrando 4 é o tipo de incoerência que destrói a confiança na entrega inteira.

## Erros comuns que essa skill existe para evitar

- Pular o diagnóstico e adivinhar o briefing. Tela genérica nasce aqui.
- Pular o fluxo e ir direto ao visual. Retrabalho garantido.
- Pular o layout e ir direto a cor e sombra. É por isso que "fica amador".
- Desenhar tela por tela quando já são mais de três. A primeira correção cobra a conta.
- Chutar largura de texto. Vira "o nome está vazando do botão".
- Espremer mais um card na tela. Vira "está sobrepondo a barra".
- Desenhar só o estado feliz. Erro, vazio e carregando são metade do front-end.
- Entregar animação com um quadro só e achar que o Figma vai inventar o resto.
- Deixar o indicador ativo dentro do grupo da aba e não entender por que ele não desliza.
- Queimar a cota do conector em projeto grande em vez de montar o plugin.
- Entregar e calar. Sem perguntas de refino a pessoa fica com um "hmm" que não vira feedback.

## Referências

Leia sob demanda, não tudo de uma vez:

- `references/plugin-figma.md`: caminho C, o plugin local, ciclo de atualização, efeitos que só existem lá.
- `references/gerador.md`: pipeline em Python, medição de texto, variantes por clone e retoque.
- `references/validadores.md`: as checagens, o que cada uma pegou na prática, como acrescentar a próxima.
- `references/animacao.md`: tokens, Prototype, Smart Animate, por que a animação não sai, specs de motion.
- `references/material-vidro.md`: vidro líquido, onde aplica e onde estraga, desfoque real.
- `references/referencia-visual.md`: ler um app de referência a partir de vídeo ou print.
- `references/diagnostico.md`: baterias de perguntas, diagnóstico de arquivo existente, perguntas de refino.
- `references/figma-mcp.md`: caminho A, sequência do conector, skills obrigatórias, limites de plano.
- `references/layout.md`: grid, densidade, ritmo vertical, refino visual.
- `references/fluxo-e-arquitetura.md`: jornada, arquitetura de informação, estados.
- `references/design-system.md`: escalas, paleta semântica, tokens, anatomia de componentes.
- `references/export-figma.md`: caminho B, regras de SVG, o que quebra na importação.
- `references/auditoria-e-handoff.md`: crítica de design, checklist WCAG, specs para dev.
