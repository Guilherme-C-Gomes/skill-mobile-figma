# Design system enxuto

O objetivo é o menor conjunto de decisões que faz vinte telas parecerem do mesmo produto. Se a empresa já tem sistema, extraia o dela e use, não invente outro.

## Espaçamento

Escala base 4, porque fecha com as densidades de tela de iOS, Android e web sem valores quebrados.

```
space-1  = 4px    espaço entre ícone e rótulo
space-2  = 8px    dentro de componente compacto
space-3  = 12px   padding interno de campo
space-4  = 16px   padding padrão de tela e de card
space-6  = 24px   entre blocos relacionados
space-8  = 32px   entre seções
space-12 = 48px   respiro de topo de tela
space-16 = 64px   separação de seções em web
```

Nunca use um valor fora da escala. Se 18px parece necessário, o problema está no tamanho de outra coisa.

## Tipografia

Escala de razão 1.25 em mobile e 1.333 em desktop. Máximo de seis níveis, mais que isso vira ruído.

```
display   32/40   bold      número grande, valor destacado
h1        24/32   bold      título de tela
h2        20/28   semibold  título de seção
body      16/24   regular   texto padrão, nunca menos que isso em mobile
small     14/20   regular   apoio, metadados
caption   12/16   medium    rótulo, tag, timestamp
```

Notação `tamanho/altura de linha`. Altura de linha de texto corrido entre 1.4 e 1.6, de título entre 1.2 e 1.3.

Fontes seguras e gratuitas que já existem no Figma e no Google Fonts: Inter (interface neutra), DM Sans (mais amigável), Instrument Sans (mais atual), Source Serif (editorial). Escolha uma família e resolva o contraste com peso, não com uma segunda família, a não ser que haja razão editorial clara.

Atenção ao padrão da empresa: se o material vai virar documento ou proposta, a fonte institucional é Calibri, com títulos de seção em azul. Isso vale para os documentos, não obrigatoriamente para a interface do produto, mas vale confirmar antes de propor outra fonte em material de cliente.

## Cor com papel semântico

Nomeie por função, não por aparência. `primary` sobrevive a uma troca de marca, `azul-claro` não.

```
bg              fundo da tela
surface         fundo de card e de modal, um degrau acima do bg
border          divisórias e contornos, contraste mínimo 3:1 quando funcional
text            texto principal, contraste mínimo 4.5:1 sobre bg
text-muted      texto de apoio, ainda 4.5:1, sem exceção
primary         ação principal e identidade
primary-hover   variação de estado
on-primary      texto sobre o primary, quase sempre branco ou quase preto
success         confirmação
warning         atenção
danger          erro e ação destrutiva
```

Cada cor semântica precisa de par claro e escuro se houver dark mode. Não gere dark mode invertendo o claro, porque a hierarquia se perde. No escuro, superfícies mais altas ficam mais claras, e o preto puro é evitado em favor de um cinza muito escuro para reduzir o halo do texto.

## Raio e elevação

```
radius-sm  4px    tag, badge
radius-md  8px    botão, campo
radius-lg  12px   card
radius-xl  20px   modal, bottom sheet
radius-full        avatar, pill

shadow-sm  0 1px 2px rgba(0,0,0,.06)     card em repouso
shadow-md  0 4px 12px rgba(0,0,0,.08)    dropdown, popover
shadow-lg  0 12px 32px rgba(0,0,0,.12)   modal
```

Consistência de raio importa mais que o valor escolhido. Botão e campo com raios diferentes é o erro que mais denuncia design amador.

## Estados de componente

Todo elemento interativo precisa dos cinco. Desenhe pelo menos uma vez na folha de design system, mesmo que não repita em cada tela.

| Estado | Tratamento |
|---|---|
| Padrão | Base |
| Hover | Escurece ou clareia 8% (só desktop) |
| Foco | Anel de 2px com offset de 2px, cor distinta do padrão |
| Ativo | Escurece 12%, opcionalmente reduz escala para 0.98 |
| Desabilitado | Opacidade 40%, cursor bloqueado, sem hover |

Estado de foco é o mais esquecido e o mais importante para navegação por teclado.

## Anatomia dos componentes básicos

**Botão**: altura 48px em mobile e 40px em desktop, padding horizontal `space-4` a `space-6`, texto em `body` semibold, raio `radius-md`. Variantes: primário preenchido, secundário com contorno, terciário só texto.

**Campo de formulário**: rótulo em `small` acima, campo com altura 48px, padding `space-3`, borda 1px `border`, borda 2px `primary` no foco. Mensagem de erro em `small` abaixo, cor `danger`, com ícone. Nunca dependa só de placeholder.

**Card**: fundo `surface`, padding `space-4`, raio `radius-lg`, `shadow-sm`. Se for clicável, precisa de estado hover e de área de toque inteira clicável.

**Lista**: altura mínima de item 56px em mobile, divisória sutil ou espaçamento, nunca os dois. Ícone à esquerda, ação ou chevron à direita.

## Movimento também é token

Duração e easing entram no sistema pelo mesmo motivo que espaçamento: sem escala, cada transição sai com um valor inventado e o produto anima de dez jeitos diferentes. A escala está em `animacao.md` e o JSON abaixo já a inclui.

## Formato de saída dos tokens

Entregue os tokens de duas formas: visualmente em `00-design-system.svg`, e como JSON no README para o dev consumir direto.

```json
{
  "color": { "primary": "#2B59FF", "bg": "#FFFFFF", "text": "#101828" },
  "space": { "1": 4, "2": 8, "3": 12, "4": 16, "6": 24, "8": 32 },
  "radius": { "sm": 4, "md": 8, "lg": 12 },
  "type": { "body": { "size": 16, "line": 24, "weight": 400 } },
  "motion": {
    "duration": { "fast": 150, "base": 200, "medium": 300 },
    "easing": { "out": "cubic-bezier(0,0,.2,1)", "in": "cubic-bezier(.4,0,1,1)" }
  }
}
```

Esse JSON é o que permite gerar o CSS, o Tailwind config ou as variáveis do Figma depois, sem alguém ficar medindo pixel em print.

## Quando o conector do Figma estiver ativo

Tokens viram **variáveis de verdade no arquivo**, não valores digitados em cada camada. A diferença é prática: com variável, trocar a cor da marca é um clique; sem, é um mutirão de busca e substituição que sempre esquece uma tela.

Organize em coleções separadas — cor, espaçamento, tipografia, raio — e amarre os componentes às variáveis desde a primeira versão. Amarrar depois quase nunca acontece.

Antes de criar qualquer variável, veja o que já existe no arquivo. O sistema da pessoa, mesmo incompleto, vale mais que o seu, porque é o que a equipe dela já usa. Ordem de construção completa em `figma-mcp.md`.
