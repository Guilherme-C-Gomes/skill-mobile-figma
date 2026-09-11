# Validadores: medir antes de entregar

Cada checagem aqui é um defeito que chegou ao usuário pelo menos uma vez. Essa é a regra que faz a lista crescer bem: **quando a pessoa apontar um erro que passou, transforme em checagem antes de responder.** Custa dez minutos e impede a classe inteira de voltar.

Rodar:

```bash
python3 scripts/check_svg_figma.py telas/ --mobile
```

`--mobile` liga as checagens que só fazem sentido em app: barra inferior, distribuição de abas e alvo de toque de 44.

## Por que medir em vez de olhar

O olho falha justamente na faixa em que o erro importa. Contraste entre 3:1 e 5:1 parece igual. Diferença de 4px numa margem parece proposital. Vão de 25px e vão de 42px na mesma barra parecem "quase iguais" até a pessoa apontar. E o pior: você olha a tela que acabou de desenhar, não as outras nove.

## O que cada checagem procura

### Estrutura e importação

O básico do que sobrevive ao Figma: `viewBox` presente, sem `var()`, sem `<foreignObject>`, grupo com `id`, texto como `<text>` e não path, fonte declarada, retângulo de fundo primeiro. Sem isso a importação sai como sopa de "Group 47".

### Contraste WCAG, sobre a cor composta

4.5:1 para texto normal, 3:1 para texto grande e elemento de interface. O detalhe que engana: quando o texto está sobre uma superfície translúcida — vidro, sobreposição, selo com opacidade —, o fundo real é a **mistura**, não o token nominal. Calcular contra o token dá aprovação falsa.

```bash
python3 scripts/contraste.py "#D06CF5" --sobre "#FFFFFF@0.16" "#0A0A12"
```

Um caso real: ícone roxo `#D06CF5` sobre uma lente de vidro clara dava 2,22:1 — reprovado — enquanto contra o fundo nominal aparentava passar. O brilho especular no topo de uma superfície colorida também precisa de conta: se o gradiente clareia o roxo onde o ícone fica, o ícone branco perde contraste ali e só ali.

### Vazamento de texto

Texto que passa da margem do frame **ou do próprio container**. É a origem de "o nome está indo para fora do botão". Checar contra a margem do frame não basta: o caso comum é o rótulo estourando a pílula que o abriga, no meio da tela.

A correção definitiva não é encolher a fonte, é derivar a largura do container da medida do texto (`references/gerador.md`).

### Séries descentralizadas

Três ou mais elementos de mesma largura em fila — barras de semana, colunas de gráfico, pontos de indicador — precisam de margens esquerda e direita iguais dentro do container. Distribuir por divisão simples e esquecer o gap acumulado desloca a série uns poucos pixels, o suficiente para a pessoa dizer "está descentralizado" sem saber apontar por quê.

### Conteúdo atrás da barra inferior (`--mobile`)

Duas linhas: **nenhuma linha de base de texto abaixo de 706** e **nenhuma caixa terminando depois de 748**. Entre o começo do véu e a barra o texto já sai apagado; depois da barra, lê como elemento cortado.

Esta foi a checagem que pegou cinco telas de uma vez num projeto em que o defeito tinha sido apontado em uma só. É o argumento inteiro a favor de validar em lote em vez de corrigir onde a seta aponta.

### Distribuição da barra de abas (`--mobile`)

Com rótulo, mede o vão entre os rótulos e as duas margens, e exige que fiquem dentro de 2px uns dos outros. Sem rótulo, mede os centros dos alvos. Centros iguais com rótulos de larguras diferentes produzem vãos desiguais, e a última aba parece empurrada contra a borda.

### Alvo de toque (`--mobile`)

44×44pt mínimo, e alvos vizinhos que não se sobrepõem. Alvo grande demais também é defeito: dois alvos de 86px em fatias de 87,5px se encostam com sobra e o toque na borda cai na aba errada.

### Matriz degenerada

Determinante de qualquer `transform="matrix(...)"` perto de zero. É o rastro do arredondamento agressivo em minificação (`references/plugin-figma.md`): o elemento fica invisível no Figma e qualquer animação nele falha com "transform is not invertible".

### Escala de espaçamento

Valores de posição, altura e raio fora do múltiplo da escala. Aviso, não erro — largura derivada de margem legitimamente cai fora. Mas número avulso repetido é o que faz a tela parecer costurada.

### Coerência numérica entre telas

Não é script, é leitura, e vale a passada: card dizendo "6 participantes em queda" com a lista mostrando 4 destrói a confiança na entrega inteira. Sempre que um número aparecer em duas telas, confira se conta a mesma história.

## O validador não sobrevive ao Figma

Todas essas checagens rodam nos arquivos que você gera. Nenhuma roda depois, quando alguém abre o Figma e edita. Para o defeito não voltar ali, a correção precisa vir acompanhada do **Auto Layout** que a torna automática — ver `references/gerador.md`. Validador protege a entrega; Auto Layout protege a manutenção.

## Como acrescentar a próxima

Uma checagem boa tem três partes: o que mede, o limite, e **a frase de por que aquilo incomoda**. O porquê é o que faz a checagem sobreviver — sem ele, alguém a afrouxa na primeira vez que ela reclama.

```python
def checar_x(alvo, limite=706):
    """Uma frase dizendo qual reclamação isso impede."""
    fora = [...]
    print(f"{len(fora)} elemento(s) …")
    return fora
```

Rode as checagens **no conjunto**, nunca num arquivo só, e faça o gerador chamá-las no fim do build. Checagem que precisa ser lembrada não é rodada.
