# Caminho C: plugin local que escreve no Figma

Um plugin de desenvolvimento que carrega o projeto inteiro dentro de si e escreve tudo no arquivo aberto **sem gastar nenhuma chamada de API**.

## Por que este caminho existe

O conector do Figma tem cota. No plano Starter são 20 chamadas por mês — não cobre nem uma rodada de dez telas, e depois cada ajuste queima mais. Importar SVG à mão funciona para três telas e vira suplício em vinte. O plugin resolve os dois problemas de uma vez e transforma a entrega num ciclo curto:

1. Você inspeciona o arquivo atual pela web ou por print.
2. Diagnostica e produz o protótipo HTML para aprovação.
3. Aprovado, regenera os arquivos do plugin.
4. Grava direto na pasta do plugin, se ela estiver conectada.
5. A pessoa dá **hot reload** e roda. Nada de importar, arrastar, renomear.

O custo é uma instalação única de três minutos. A partir daí, cada rodada de correção custa um clique para a pessoa.

## Instalação, uma vez só

Diga isso no README do plugin, porque é a única parte manual:

1. Figma **desktop** (plugin de desenvolvimento não aparece na web).
2. Menu → Plugins → Development → **Import plugin from manifest…**
3. Escolher o `manifest.json` da pasta.

Depois disso, atualizar é botão direito no canvas → Plugins → Development → **Hot reload plugin**.

Se a pasta do plugin estiver conectada à sessão, grave os arquivos nela direto e peça só o hot reload. Se não estiver, entregue a pasta zipada e sugira conectá-la — o ciclo fica muito mais curto depois.

## Anatomia

```
plugin-<projeto>/
  manifest.json   registro do plugin
  code.js         lógica + o projeto inteiro embutido (SVGs minificados)
  ui.html         a janelinha com os botões e o relatório
  LEIA-ME.md      instalação e uso
```

`manifest.json`:

```json
{
  "name": "<Projeto> — importar",
  "id": "projeto-importar",
  "api": "1.0.0",
  "main": "code.js",
  "ui": "ui.html",
  "editorType": ["figma"],
  "documentAccess": "dynamic-page",
  "networkAccess": { "allowedDomains": ["none"] }
}
```

`code.js` é **gerado**, nunca editado à mão: ele carrega os SVGs de todas as telas como strings. Use `scripts/gerar_plugin_figma.py` como ponto de partida — ele já monta manifest, code.js, ui.html e LEIA-ME a partir de uma pasta de SVGs.

## O que o plugin faz que o SVG sozinho não faz

Esta é a razão de peso para o caminho C, além da cota. Três coisas só existem como API de plugin:

**Efeitos de camada.** Desfoque de fundo não cabe em SVG e `createNodeFromSvg` também não carrega. O plugin aplica depois:

```js
no.effects = [{ type: 'BACKGROUND_BLUR', radius: 28, visible: true }];
```

É o que separa "cinza claro com um brilho" de vidro que realmente deixa ver o que está atrás.

**Variáveis e estilos de verdade.** `figma.variables.createVariableCollection` e `createTextStyle` produzem tokens que a equipe usa, não valores soltos. Faça upsert por nome para não duplicar a cada rodada.

**Ligações de protótipo.** `setReactionsAsync` monta o Prototype inteiro programaticamente, incluindo `AFTER_TIMEOUT` e `SMART_ANIMATE`. Ligar quarenta hotspots à mão é onde a paciência acaba.

Também vale: `clipsContent = true` nos frames importados, senão elementos que descansam fora da tela de propósito (um reflexo que varre, por exemplo) ficam à vista.

## Estrutura do code.js

Cinco funções e uma tabela de dados. O esqueleto:

```js
const D = { /* telas, estados, tokens, ligações — gerado */ };
const SECAO = '<Projeto> — telas';

figma.showUI(__html__, { width: 400, height: 640, themeColors: true });

// 1. importar telas: cria a seção, remove só o que este plugin criou antes
//    (pelo nome exato) e recria. Nada fora da seção é tocado.
async function importarTelas() { … }

// 2. estados derivados: clone da tela base + retoque declarativo
async function aplicarEstado(clone, receita) { … }

// 3. tokens: coleção de variáveis e estilos de texto, com upsert por nome
async function criarTokens() { … }

// 4. protótipo: setReactionsAsync em cada nó, mais o ponto de entrada
async function ligarPrototipo() { … }

// 5. relatório: o que foi criado e o que falhou, nomeado
function relatorio(acao) { … }
```

### Substituir sem duplicar

Rodar de novo tem de **substituir**, não empilhar. Guarde a lista de nomes que o plugin cria e remova por nome exato antes de recriar:

```js
const meus = D.telas.map(t => t.nome).concat(D.estados.map(e => e.nome));
for (const filho of sec.children.slice()) {
  if (meus.indexOf(filho.name) !== -1) filho.remove();
}
```

Isso é o que permite iterar dez vezes sem sujar o arquivo da pessoa. E confina tudo numa `figma.createSection()` própria, para que o conteúdo antigo dela nunca seja tocado.

### Estados por clone e retoque

Filtro que filtra, esqueleto que brilha, aba selecionada — tudo isso são **estados da mesma tela**, e o jeito certo de produzi-los é clonar o frame base e retocar:

```js
const c = base['04 Home'].clone();
c.name = '04b Home · Atibaia';
await aplicarEstado(c, receita);
```

Duas razões. Primeiro, clone garante **nome de camada idêntico** peça por peça, que é do que o Smart Animate vive. Segundo, a receita é declarativa e mora no gerador — quando um número do design muda, nenhuma variante precisa ser redesenhada.

Vocabulário de receita que cobre quase tudo:

```
chips       [[lista de nomes], nome do ativo]   repinta o grupo de pílulas
textos      { nome: novo texto }
opacidade   { nome: 0..1 }
esconder    [nomes]
mover       { nome: dy }  ou  { nome: {dx, dy} }
larguras    { nome: largura absoluta }
retangulos  { nome: {dw, dh, dy} }              deltas, nunca absoluto
transformar { nome: {escala} }
```

**Use delta, não coordenada absoluta, para o que está dentro de um grupo.** `node.x` é relativo ao pai, e o pai de um nó importado nem sempre é o frame — somar um delta sempre funciona, atribuir um absoluto às vezes não.

### Nada pode derrubar a rodada

Um retoque que falha não pode abortar a importação inteira e deixar o arquivo pela metade. Isole cada operação e junte os problemas no fim:

```js
function seguro(fase, rotulo, fn) {
  try { return fn(); }
  catch (err) { problema(fase, rotulo, err.message); }
}
```

E termine sempre com um relatório nomeado — quantos, de que tipo, e exatamente qual falhou:

```
──────────  relatório  ──────────
telas do app     10 de 10
estados          11 de 11
vidro            68 superfícies com desfoque
variáveis        35
ligações         139 criadas
                 28 ignoradas de propósito
erros            nenhum
```

Distinguir "ignorado de propósito" de "erro" importa: aba de navegação numa tela que não tem barra, ou pílula cujo destino é a própria tela, são ausências previstas. Se elas entrarem na conta de erros, o relatório vira ruído e ninguém lê.

Um botão **Copiar relatório** na `ui.html` fecha o ciclo: quando algo falha, a pessoa cola o texto de volta e você sabe exatamente onde olhar.

## Valide o que você gera, antes de entregar

Plugin quebrado é caro: a pessoa instala, roda, e nada acontece. Duas travas baratas evitam a maior parte:

```bash
node --check code.js
python3 -c "import re,subprocess,tempfile; ..."   # o <script> do ui.html também
```

O erro clássico é escape a mais na geração: um `\n` escrito dentro de uma string Python vira quebra de linha de verdade no arquivo JavaScript, o script inteiro deixa de compilar, e o sintoma é "a janela abre e os botões não fazem nada". `node --check` pega isso em um segundo. Quando houver `jsdom` disponível, vale um ensaio da janela também: carregar o `ui.html`, clicar cada botão e conferir que a mensagem certa sai.

## Limites

- Plugin de desenvolvimento só aparece no Figma **desktop**.
- `documentAccess: "dynamic-page"` exige as variantes `Async` de várias APIs (`getLocalTextStylesAsync`, `getVariableByIdAsync`, `setReactionsAsync`).
- O plugin não sabe ler o que já existe no arquivo da pessoa a não ser que você programe isso. Para inspecionar o estado atual, use o conector ou peça print.
- `code.js` com todas as telas embutidas passa fácil de 150 KB. Isso é normal e não é problema para o Figma, mas minifique os SVGs — com cuidado, ver a próxima seção.

## Minificação de SVG: a armadilha do arredondamento

Encurtar número em SVG parece inofensivo e não é. Arredondar por casa decimal fixa transforma `-0.0130` em `-0`, e uma matriz `matrix(0.013 0 0 -0 20 58)` tem determinante zero: o elemento colapsa, some da tela, e qualquer tentativa de mexer nele responde `Invalid relative transform: rotation is not invertible`.

A regra segura é limitar o **erro relativo** e nunca deixar um número diferente de zero virar zero:

```python
def poda(t):
    v = float(t)
    if v == int(v):
        return str(int(v))
    for casas in range(1, 7):
        c = round(v, casas)
        if c != 0 and abs(c - v) <= abs(v) * 0.001:
            return f"{c:.{casas}f}".rstrip("0").rstrip(".")
    return t
```

Sintomas de que isso aconteceu: logo ou ícone invisível no Figma mas visível no navegador, e erro de transformada não invertível ao animar. `scripts/check_svg_figma.py` checa determinante de matriz justamente por causa disso.
