# Gerar as telas por código

A partir de três ou quatro telas, escrever um gerador em Python vence desenhar SVG tela por tela. Não é preferência de engenharia: é o que decide se a segunda rodada de correção custa dez minutos ou duas horas.

## Por que

A pessoa olha **uma** tela e diz "esse chip está muito oval". A correção precisa valer nas dez, no design system e no protótipo. Com SVGs escritos à mão você edita dez arquivos, esquece um, e ele reaparece três rodadas depois. Com gerador, você muda `R["chip"] = 16` e roda de novo.

Isso vale ainda mais quando a mesma tela precisa de variantes — filtro aplicado, aba selecionada, estado de erro. Escrever cada variante à mão multiplica a superfície de erro por quatro.

O sinal de que chegou a hora: você está prestes a copiar e colar um bloco de SVG pela segunda vez.

## Estrutura que funciona

Seis arquivos, com responsabilidade separada. O que importa é a separação, não os nomes.

```
gen/
  tokens.py     paleta, escala tipográfica, espaçamento, raio, movimento, layout
  medida.py     largura real de texto por fonte, tamanho e peso
  svgkit.py     primitivas: rect, text, circle, path, ícones, avatar, pílula, selo
  shared.py     blocos compostos: hero, barra de navegação, campo de busca, card
  build.py      as telas, uma função por tela
  validar.py    as checagens que rodam a cada build
```

`tokens.py` é a única fonte de números. Nenhuma cor literal e nenhum espaçamento solto em `build.py` — se aparecer, é sinal de que falta um token.

```python
C = {"bg":"#0A0A12", "surface":"#15151F", "text":"#FFFFFF",
     "muted":"#9A9AAD", "primary":"#9E05D2", "danger":"#FF7A85"}
W, H = 390, 844          # viewport
M, CW = 20, 350          # margem e largura de conteúdo
NAV_Y, NAV_H = 752, 60   # barra inferior
R = {"campo":12, "botao":16, "card":16, "chip":16, "nav":24}
MOTION = {"instant":100, "fast":150, "base":200, "medium":300, "slow":400}
```

`build.py` fica declarativo e legível:

```python
s_home = doc("Frame_Home",
    hero("Bom dia, Chico", "Sábado, 5 de setembro"),
    linha_chips(M, 170, 44, [("Filtro_Todos","Todos",True),
                             ("Filtro_Atibaia","Atibaia",False)]),
    campo_busca(228, "Buscar participante"),
    card(M, 316, CW, 140, …, cid="Card_Ativos"),
    scrim(), tabbar(0),
    defs=DEFS)
save("04-home.svg", s_home)
```

## Medir texto, não chutar

Toda reclamação de "o nome está vazando do botão" nasce de largura estimada. Pílula, selo, botão e chip têm de sair da medida real do rótulo:

```python
from medida import larg
w = larg("Sincronizar agora", 16, 600) + padding * 2
```

Use uma métrica de fonte de verdade (PIL com uma TTF, ou tabela de larguras), e escolha uma fonte **um pouco mais larga** que a do design — DejaVu Sans no lugar de Inter, por exemplo. Assim o erro sempre sobra espaço em vez de faltar. `scripts/medida_texto.py` faz isso e serve tanto para o gerador quanto para checagem avulsa.

O mesmo vale para o inverso: elemento cuja largura vem do texto precisa se **mover** quando o texto muda. Selo alinhado à direita que cresce de "+7 pp" para "+11 pp" tem de deslocar para a esquerda pela diferença, senão estoura a borda do card.

## Distribuir por vão, não por centro

Quando uma fila tem itens de larguras muito diferentes — rótulos de navegação, chips de filtro —, dividir o espaço em fatias iguais deixa os centros certos e os **vãos** tortos, e o olho lê torto:

```
centros iguais:  Início ▁▁▁▁ Participantes ▁▁ Métricas ▁▁▁▁▁▁ Ajustes
vãos iguais:     Início ▁▁▁ Participantes ▁▁▁ Métricas ▁▁▁ Ajustes
```

Meça cada rótulo, some, divida o que sobra em (n+1) partes iguais, e posicione. Quando os itens têm a mesma largura — barra só de ícone, por exemplo — a divisão simples em fatias volta a ser a certa.

## Variantes por receita, não por cópia

Estados da mesma tela (filtro aplicado, aba ativa, período trocado) não devem ser telas separadas no gerador. Descreva a diferença:

```python
_home("04b Home · Atibaia", chip="Filtro_Atibaia",
      textos={"Card_Ativos_Valor": "58", "Card_Presenca_Valor": "34"},
      larguras={"Card_Ativos_Barra_Preenchimento": 318})
```

O plugin aplica a receita sobre um clone da tela base (`references/plugin-figma.md`). Ganha duas coisas: nomes de camada idênticos, que é do que o Smart Animate vive, e um único lugar para mudar quando o número mudar.

Quando esconder itens de uma lista, **recoloque os que sobram** para não deixar buraco. Calcule as posições a partir do passo, não a partir de constantes copiadas.

## O que o gerador não protege: a edição no Figma

O gerador garante o arquivo que você entrega. Não garante o que acontece depois, quando alguém abre o Figma e troca um rótulo — e aí a fila distribuída à mão volta a torcer.

Por isso, toda entrega de fila, grade ou pilha vem com a instrução de **Auto Layout** correspondente: direção, espaçamento, alinhamento e o que é fixo versus preenchimento. Numa barra de abas, por exemplo: Auto Layout horizontal, espaçamento "space between", padding lateral igual, cada aba com largura fixa e o container preenchendo. Assim o Figma refaz a conta sozinho quando o texto mudar.

Vale a mesma lógica para os cards de uma lista (vertical, gap da escala, itens preenchendo a largura) e para o conteúdo interno de um card. É a diferença entre entregar um arquivo certo e entregar um arquivo que continua certo.

## Escala de gráfico sai da linha de meta

Barra de gráfico com altura chutada mente. Se existe uma linha de referência desenhada — meta de 70%, média —, derive a escala **dela**:

```python
GBASE, GTOP = 450, 360          # base das barras e a linha de meta
GESC = (GBASE - GTOP) / 0.70    # escala que faz 70% cair exatamente na linha
altura = GESC * valor
```

Assim a linha de meta e as barras contam a mesma história. Rótulo de valor dentro da barra, não acima: acima, ele cruza a linha de meta sempre que o valor chega perto dela.

## Validar a cada build

O gerador termina rodando as checagens. É isso que impede um defeito corrigido de voltar. Ver `references/validadores.md`.

```bash
python3 build.py && python3 validar.py telas/
```

## Do gerador para os três destinos

O mesmo gerador alimenta tudo, e é por isso que os três destinos nunca divergem:

| Destino | Como |
|---|---|
| Arquivos para importar | os `.svg` direto |
| Protótipo clicável | um HTML que embute os mesmos SVGs, com CSS de transição |
| Plugin do Figma | os SVGs minificados dentro do `code.js` |

Gere o protótipo HTML a partir dos mesmos SVGs, não redesenhando em HTML. Quando o protótipo e o Figma divergem, é quase sempre porque alguém redesenhou.
