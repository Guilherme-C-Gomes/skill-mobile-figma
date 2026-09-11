# Ler uma referência visual

"Faz igual a esse app aqui" vem quase sempre com um vídeo de tela gravado no celular, ou dois ou três prints. É a forma mais rica de briefing que existe — e a mais fácil de interpretar errado, porque a memória preenche o que os olhos não viram.

## Extraia os quadros, não confie na lembrança

Um vídeo de cinco segundos tem a coreografia inteira, mas passa rápido demais para ser lida. Fatie e monte uma folha de contato:

```bash
ffmpeg -i ref.mp4 -vf "fps=8,scale=240:-1" quadros/q%03d.png
ffmpeg -i quadros/q%03d.png -vf "tile=8x4:margin=6:padding=6" -frames:v 1 folha.png
```

Depois olhe a folha inteira de uma vez. Vinte quadros lado a lado mostram a ordem dos eventos, o que entra antes do quê, e quanto tempo cada fase dura — coisas invisíveis quando o vídeo roda.

Num caso real, eu tinha animado as letras de uma marca entrando da esquerda para a direita. A folha de contato mostrou o oposto: elas entravam **da direita**, uma a uma, a última primeiro. Adivinhar teria custado duas rodadas.

Para um detalhe específico, recorte a mesma região em vários quadros e empilhe:

```bash
# a barra inferior em cinco momentos, para ver como o indicador se move
python3 -c "from PIL import Image; …"
```

## O que perguntar aos quadros

Cinco perguntas que rendem quase tudo:

1. **O que é material e o que é conteúdo?** Onde o app deixa ver o que está atrás e onde não deixa. Repare no que aparece embaixo das superfícies flutuantes quando o conteúdo rola.
2. **Qual a ordem dos eventos?** O que se move primeiro, o que espera. Cascata quase sempre tem uma direção, e ela raramente é a que você suporia.
3. **O indicador de estado desliza ou pisca?** Se desliza, isso muda a estrutura de camadas que você precisa montar no Figma.
4. **Quanto dura?** Conte quadros. A 8 fps cada quadro é 125 ms — dá para cronometrar cada fase com precisão suficiente.
5. **O que eles NÃO fizeram?** Ausência é decisão. Barra sem rótulo, tela sem título, lista sem divisória.

## Copie o princípio, não a aparência

O pedido é "use como inspiração", e a diferença importa. Copiar a aparência produz um app que parece o outro e não parece o da pessoa. Copiar o princípio — como o material se comporta, como o estado é comunicado, qual o ritmo — produz algo que herda a qualidade sem herdar a identidade.

Na prática, três filtros:

**A cor da referência não vem junto.** Se o app de referência tinge o ícone ativo de verde-limão sobre vidro claro e a marca da pessoa é roxo escuro, a mesma receita reprova em contraste. Herde a *ideia* (o estado vive na cor do ícone, não numa área cheia) e resolva a cor com a paleta que existe.

**A densidade da referência pode não caber.** App de banco com quatro abas e nenhum rótulo assume usuário diário. App de coordenação de ONG usado uma vez por semana não tem esse luxo. Diga isso quando for o caso, faça o que foi pedido, e ofereça o meio-termo.

**O que a plataforma não faz, você não promete.** Vídeo institucional desenha a marca traço por traço ao longo de três segundos. O Prototype do Figma não anima path. A aproximação honesta é crescer com fade — e dizer que, para o traço literal, o caminho é Lottie tocado pelo dev.

## Devolva a leitura antes de executar

Antes de gastar uma rodada implementando, escreva em quatro linhas o que você leu nos quadros: fases, ordem, tempos, e o que não dá para reproduzir. É barato, e é onde a pessoa corrige o entendimento — que é muito mais rápido do que corrigir o resultado.
