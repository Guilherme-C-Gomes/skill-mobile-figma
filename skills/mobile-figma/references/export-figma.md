# Caminho B: arquivos para importar no Figma

Use quando o conector do Figma não estiver na sessão, ou quando a pessoa preferir importar ela mesma em vez de deixar você escrever no arquivo dela.

Regras práticas do que sobrevive à importação e do que quebra.

## SVG ou HTML: qual escolher

| Escolha | Quando | O que ganha | O que perde |
|---|---|---|---|
| **SVG por tela** | Tela visual, layout definido, o que importa é a estrutura de camadas | Camadas nomeadas, texto editável, importação sem plugin | Sem auto layout, sem interação |
| **HTML único** | A pessoa quer clicar e navegar antes de aprovar, ou o layout é denso em texto | Auto layout em boa parte dos casos via `html.to.design`, transições reais rodando | Depende de plugin, e a conversão nem sempre é fiel |

Quando houver dúvida, entregue os dois: o SVG é o que entra no Figma limpo, o HTML é o que a pessoa clica para aprovar o fluxo e o movimento.

## Como o Figma lê um SVG

Ao colar ou arrastar um SVG, o Figma converte cada elemento em nó nativo. `<g>` vira grupo, `<rect>` vira retângulo, `<text>` vira texto editável, `<path>` vira vetor. O atributo `id` de cada elemento vira o nome da camada. Isso é o que separa uma entrega útil de uma sopa de "Group 47".

## O que funciona bem

| Recurso SVG | Resultado no Figma |
|---|---|
| `<rect>` com `rx` | Retângulo com raio, editável |
| `<circle>`, `<ellipse>`, `<line>` | Formas nativas |
| `<text>` com `font-family`, `font-size` | Texto editável, se a fonte existir |
| `<g id="Nome">` | Grupo nomeado |
| `fill`, `stroke`, `stroke-width` | Preenchimento e contorno |
| `linearGradient` simples | Gradiente linear |
| `opacity`, `fill-opacity` | Opacidade de camada |
| `<path>` | Vetor editável |

## O que quebra ou degrada

| Recurso | O que acontece |
|---|---|
| `var(--cor)` | Não resolve, vira preto ou some. Use hex literal |
| `<foreignObject>` | Ignorado por completo |
| `filter` com `feGaussianBlur` complexo | Some ou rasteriza |
| `<use>` referenciando símbolo | Frequentemente perde a referência |
| CSS externo ou `<style>` com seletor complexo | Não aplica de forma confiável. Prefira atributo inline |
| Texto convertido em path | Vira vetor, deixa de ser editável. Nunca faça isso |
| `clipPath` aninhado em vários níveis | Comportamento imprevisível |
| Fonte não instalada | Substituída, o layout desloca |
| Auto Layout | Não existe em SVG, aplique manualmente depois |

## Convenção de nomes de camada

Underscore, sem acento, hierarquia refletindo a estrutura real do componente. Isso vira a árvore de camadas e depois a estrutura do componente React.

```xml
<g id="Tela_Home">
  <g id="Header">
    <g id="Header_Avatar">...</g>
    <g id="Header_Titulo">...</g>
  </g>
  <g id="Lista_Pedidos">
    <g id="Card_Pedido_1">
      <g id="Card_Pedido_1_Status">...</g>
    </g>
  </g>
  <g id="Nav_Bottom">...</g>
</g>
```

## Template de tela (mobile 390x844)

Comentado para servir de base. Substitua os valores pelos tokens definidos.

```xml
<svg width="390" height="844" viewBox="0 0 390 844"
     xmlns="http://www.w3.org/2000/svg" fill="none">

  <!-- fundo do frame, sempre o primeiro elemento -->
  <rect id="Frame_Home" width="390" height="844" fill="#FFFFFF"/>

  <g id="Header">
    <text id="Header_Titulo" x="16" y="80"
          font-family="Inter" font-size="24" font-weight="700" fill="#101828">
      Bom dia, Ana
    </text>
    <text id="Header_Subtitulo" x="16" y="106"
          font-family="Inter" font-size="14" font-weight="400" fill="#667085">
      Você tem 3 pedidos em aberto
    </text>
  </g>

  <g id="Card_Pedido">
    <rect x="16" y="132" width="358" height="96" rx="12" fill="#FFFFFF"
          stroke="#EAECF0" stroke-width="1"/>
    <text x="32" y="164" font-family="Inter" font-size="16"
          font-weight="600" fill="#101828">Pedido #1042</text>
    <rect id="Card_Pedido_Status" x="32" y="180" width="72" height="24"
          rx="12" fill="#ECFDF3"/>
    <text x="44" y="196" font-family="Inter" font-size="12"
          font-weight="500" fill="#027A48">Em rota</text>
  </g>

  <g id="Botao_Primario">
    <rect x="16" y="760" width="358" height="48" rx="8" fill="#2B59FF"/>
    <text x="195" y="790" text-anchor="middle" font-family="Inter"
          font-size="16" font-weight="600" fill="#FFFFFF">Novo pedido</text>
  </g>
</svg>
```

Detalhes que evitam retrabalho:

- `y` de `<text>` é a linha de base, não o topo. Para centralizar verticalmente em um bloco de altura `h` começando em `y0`, use aproximadamente `y0 + h/2 + fontSize*0.35`.
- Centralização horizontal com `text-anchor="middle"` e `x` no centro do container.
- `fill="none"` no `<svg>` raiz evita preenchimento preto herdado em elementos sem fill.
- Um SVG por tela. Vários frames num arquivo só complica a importação.

## Minificar sem quebrar

Encurtar número em SVG parece inofensivo e não é. Arredondar por casa decimal fixa transforma `-0.0130` em `-0`, e `matrix(0.013 0 0 -0 20 58)` tem determinante zero: o elemento colapsa, some no Figma — mas continua aparecendo no navegador, o que atrasa o diagnóstico — e qualquer tentativa de animá-lo responde `Invalid relative transform: rotation is not invertible`.

Limite o **erro relativo**, não o número de casas, e nunca deixe um valor diferente de zero virar zero. A função está em `scripts/gerar_plugin_figma.py` (`poda`), e `scripts/check_svg_figma.py` checa determinante de matriz por causa disso.

## Matriz espelhada e rotação

Vetor traçado a partir de imagem (potrace e semelhantes) sai com o eixo Y invertido: `matrix(a 0 0 -a e f)`. Isso importa em dois momentos.

Na importação, funciona normalmente. Mas **pedir rotação a um grupo com matriz espelhada deixa a transformada não invertível** e o Figma recusa — e, se isso acontecer no meio de um script de plugin, a execução para ali. Se precisar de rotação num elemento desses, ou aplique-a a um envoltório de transformada limpa, ou troque por escala e deslocamento, que não têm esse problema.

## Recorte do frame

Elemento posicionado fora da tela de propósito — um reflexo que descansa à esquerda esperando a vez de varrer — só fica invisível se o frame recortar. Em SVG isso é natural; no Figma, garanta `clipsContent = true` (o plugin faz isso na importação). Sem recorte, o elemento fica à vista ao lado da tela e parece lixo esquecido.

## Dimensões padrão

```
iPhone 14/15         390 x 844
iPhone Pro Max       430 x 932
Android médio        360 x 800
Tablet retrato       834 x 1194
Web desktop          1440 x 1024
Web conteúdo         largura máxima 1200, colunas de 12
```

## Caminho HTML

Um único arquivo `.html` com CSS embutido, sem framework e sem build.

Para importar: plugin `html.to.design` no Figma, aba de colar código ou URL. Ele preserva texto, cor e espaçamento, e converte a maior parte do flexbox em Auto Layout, o que o SVG não faz.

Como escrever para a conversão sair boa:

- **Flexbox e gap** em vez de margem e posicionamento absoluto. `display:flex` com `gap` vira auto layout com espaçamento; margem vira posição solta.
- **Um bloco semântico por seção**, com `class` descritiva. O nome da classe vira o nome do frame.
- **Sem grid CSS complexo**, que converte de forma imprevisível. Colunas com flex e largura percentual convertem melhor.
- **Sem imagem externa por URL**, que não carrega na conversão. Use `data:` URI ou bloco de cor sólida como marcação de lugar.
- **Fonte do Google Fonts** declarada, mas com a família também presente no Figma da pessoa.

O HTML é também onde o movimento fica clicável antes de existir código. Use `transition` em `opacity` e `transform` com as durações e curvas definidas em `animacao.md`, e inclua o bloco de movimento reduzido — assim a spec entregue ao dev já está demonstrada:

```css
.sheet { transform: translateY(100%); transition: transform 300ms cubic-bezier(0,0,.2,1); }
.sheet.aberto { transform: translateY(0); }

@media (prefers-reduced-motion: reduce) {
  .sheet { transition: opacity 100ms linear; transform: none; }
}
```

Restrição: nada de `localStorage` nem `sessionStorage` em artefato exibido no Claude, porque não funciona ali. Estado em variável de memória resolve para um protótipo.

## Depois de importar, o que a pessoa faz no Figma

Diga isso no README, porque economiza a pergunta seguinte:

1. Selecionar o frame e aplicar Auto Layout nos grupos verticais, com o espaçamento da escala de tokens.
2. Transformar os grupos repetidos em componente com Ctrl+Alt+K.
3. Criar as variáveis de cor a partir do JSON de tokens.
4. Ligar as telas no modo Prototype para navegar, seguindo a tabela de transições que você entregou.
