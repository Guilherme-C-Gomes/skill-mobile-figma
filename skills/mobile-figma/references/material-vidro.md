# Vidro líquido

Material translúcido para a camada de controles flutuantes. Popularizado pelo Liquid Glass da Apple e adotado por boa parte dos apps que a pessoa vai mostrar como referência.

## Onde aplica e onde estraga

**Vidro é para a camada que flutua**: barra de navegação inferior, pílulas de filtro, campo de busca, botão flutuante, bottom sheet, cabeçalho que fica sobre o conteúdo rolando.

**Não estenda para os cards.** Card sobre fundo chapado não tem nada atrás para refratar — fica leitoso, perde hierarquia, e o app inteiro vira uma névoa cinza. A graça do vidro é justamente separar o que flutua do que é conteúdo; se tudo for vidro, nada flutua.

O teste é simples: se atrás do elemento há conteúdo que rola, vidro faz sentido. Se atrás há só o fundo da tela, o vidro só está clareando um retângulo.

## A receita

Três camadas, sempre nessa ordem:

**1. Fundo translúcido com brilho especular no topo.** Não é uma opacidade única: é um gradiente vertical de branco, mais forte em cima, que imita a luz batendo na quina superior.

```xml
<linearGradient id="grad_vidro" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0"    stop-color="#FFFFFF" stop-opacity="0.16"/>
  <stop offset="0.55" stop-color="#FFFFFF" stop-opacity="0.056"/>
  <stop offset="1"    stop-color="#FFFFFF" stop-opacity="0.091"/>
</linearGradient>
```

A subida no último stop não é engano. Luz que bate no fundo sobe e ilumina a borda inferior por dentro; sem isso o material parece um retângulo com opacidade, não vidro.

**2. Fio de luz na borda**, também em gradiente — 30% em cima, 8% no meio, 16% embaixo:

```xml
<linearGradient id="grad_borda_vidro" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0"    stop-color="#FFFFFF" stop-opacity="0.30"/>
  <stop offset="0.55" stop-color="#FFFFFF" stop-opacity="0.08"/>
  <stop offset="1"    stop-color="#FFFFFF" stop-opacity="0.16"/>
</linearGradient>
```

**3. Desfoque de fundo**, que é o que falta em SVG. No Figma entra pelo plugin como efeito de camada; no app, o dev usa o material nativo da plataforma:

```js
no.effects = [{ type: 'BACKGROUND_BLUR', radius: 28, visible: true }];
```

```css
backdrop-filter: blur(28px) saturate(1.4);
```

A saturação importa: o desfoque lava a cor do que está atrás, e devolver 40% traz o material de volta à vida.

## O véu atrás da barra precisa afinar

Se havia um degradê escuro quase opaco atrás da barra — o padrão para esconder conteúdo que passa por baixo —, ele precisa **afinar muito** quando a barra vira vidro. Vidro sobre preto chapado não tem o que refratar e parece só um retângulo cinza claro.

Troque por um véu leve mais um brilho difuso sob a barra, para o material ter profundidade:

```
antes:  0 → 0.72 → 0.97   (parede)
depois: 0 → 0.30 → 0.55   (véu) + brilho radial sob a barra
```

## Contraste sobre vidro

Sempre calcule sobre a **cor composta**, nunca sobre o token. Dois casos que reprovam com facilidade:

**Ícone colorido sobre vidro claro.** Roxo `#D06CF5` sobre uma lente de branco 30% dá 2,22:1. Cor escura não sobrevive em superfície clara — se a referência usa ícone tingido, repare que a cor dela é clara (verde-limão, ciano) e a sua provavelmente não é.

**Ícone branco sobre superfície colorida com brilho especular.** O brilho clareia o roxo exatamente onde o ícone fica e o contraste desaba de 6,17:1 para 2,84:1. A saída é limitar o especular aos primeiros 30% da altura, acima da área do ícone:

```xml
<stop offset="0"    stop-color="#FFFFFF" stop-opacity="0.22"/>
<stop offset="0.30" stop-color="#FFFFFF" stop-opacity="0.06"/>
<stop offset="0.55" stop-color="#FFFFFF" stop-opacity="0"/>
```

## O movimento que faz o material parecer líquido

Vidro parado é só um retângulo translúcido. O que vende o material é a deformação em movimento.

**A lente que viaja.** O indicador da aba ativa não pisca de lugar: ele parte da posição anterior e escorrega, esticando no caminho. Quanto mais longe, mais estica.

```js
const estica = 1 + Math.min(Math.abs(dx) / 260, 0.34);
// translateX(dx) scaleX(estica)  →  translateX(0) scaleX(1)
// 620ms, cubic-bezier(0.22, 1.4, 0.36, 1)
```

No Figma isso exige que a lente tenha nome fixo e mesmo pai em todas as telas — ver `references/animacao.md`.

**Duas curvas novas** ao lado das do sistema:

```
liquido   cubic-bezier(0.22, 1.4, 0.36, 1)   o que tem massa: passa do alvo e volta
lente     cubic-bezier(0.16, 1, 0.3, 1)      o material: entra rápido, assenta seco
```

**Entrada com desfoque.** Conteúdo que aparece com `blur 5px → 0` junto do deslocamento materializa em vez de só deslizar. Combina com o material e custa uma propriedade.

**Toque.** Encolhe para 0.96 e o vidro acende — `brightness(1.25)` enquanto pressionado. O acender é o que diz "isto é uma superfície", não um retângulo pintado.

## O que não dá para fazer, e como dizer isso

Em protótipo HTML cujas telas são SVG inline, `backdrop-filter` não funciona em forma de SVG. Ali o vidro é o brilho e a borda, sem desfoque ao vivo. Isso é aceitável e precisa ser dito: no Figma o desfoque é real, e para o dev está na spec.

Não tente contornar com filtro SVG — `feGaussianBlur` sobre `BackgroundImage` é recurso morto e não é suportado em navegador nenhum.
