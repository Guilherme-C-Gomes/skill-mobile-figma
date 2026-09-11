# Auditoria e handoff

Para quando já existe design pronto: criticar, verificar acessibilidade e passar para desenvolvimento.

## Crítica de design

O formato de devolutiva com nota por critério, e as perguntas a fazer antes de criticar, estão em `diagnostico.md`. Aqui fica a ordem de análise e o que olhar em cada ponto.

Ordem importa. Comece pelo que é caro de mudar depois, termine no que é barato.

1. **Fluxo**: a tela serve ao job do usuário? Sobra passo? Falta passo? Existe beco sem saída?
2. **Hierarquia**: em meio segundo, o olho vai para a coisa certa? Existe uma única ação primária?
3. **Layout**: alinhamento, grid, espaçamento na escala, densidade constante. Checklist em `layout.md`.
4. **Consistência**: o mesmo componente aparece com tratamentos diferentes em telas diferentes?
5. **Estados**: vazio, erro e carregando existem?
6. **Acessibilidade**: contraste medido, alvo de toque, foco.
7. **Texto**: rótulos dizem o que acontece? Erro orienta?
8. **Movimento**: transição definida, ou cada tela anima de um jeito? Ver `animacao.md`.
9. **Refino visual**: alinhamento ótico, raio consistente, famílias de ícone.

Formato de devolutiva que funciona: para cada ponto, diga **o que está acontecendo**, **por que custa caro**, e **o que fazer**. Crítica sem a terceira parte é reclamação.

Separe o que é problema objetivo (contraste 2.1:1 reprova em WCAG) do que é preferência sua (esse azul é frio demais). Misturar os dois faz a pessoa descartar os dois.

Feche com as três correções de maior retorno pelo esforço. Lista de vinte itens não é acionável e a pessoa não sabe por onde começar.

## Contraste

Fórmula da luminância relativa, para calcular em vez de chutar. Para cada canal `c` em `{R,G,B}` normalizado de 0 a 1:

```
c_lin = c/12.92                      se c <= 0.03928
c_lin = ((c + 0.055)/1.055) ^ 2.4    caso contrário

L = 0.2126*R_lin + 0.7152*G_lin + 0.0722*B_lin

razao = (L_claro + 0.05) / (L_escuro + 0.05)
```

Mínimos WCAG 2.1 nível AA:

| Elemento | Razão mínima |
|---|---|
| Texto normal, abaixo de 18pt | 4.5:1 |
| Texto grande, 18pt ou 14pt bold | 3:1 |
| Ícone e borda funcional | 3:1 |
| Texto decorativo ou desabilitado | isento, mas evite depender dele |

Nível AAA pede 7:1 para texto normal. Use quando o público inclui pessoas idosas ou de baixa visão, o que é mais comum do que se assume.

Não estime. A skill traz o cálculo pronto:

```bash
python3 scripts/contraste.py "#667085" "#FFFFFF"          # um par
python3 scripts/contraste.py --paleta tokens.json          # a paleta inteira
```

Estimativa a olho erra com frequência justamente na faixa entre 3:1 e 5:1, que é onde está o limite. O validador de SVG (`check_svg_figma.py`) já roda essa checagem em cada texto contra o fundo real.

## Checklist de acessibilidade

- [ ] Todo texto passa no mínimo de contraste sobre seu fundo real
- [ ] Alvo de toque de 44x44pt em mobile, 24x24 com espaçamento em desktop
- [ ] Estado de foco visível e distinto do hover
- [ ] Nenhuma informação transmitida só por cor
- [ ] Ordem das camadas corresponde à ordem lógica de leitura
- [ ] Campos de formulário têm rótulo persistente, não só placeholder
- [ ] Mensagem de erro associada ao campo, com texto e ícone
- [ ] Texto redimensiona até 200% sem perder conteúdo
- [ ] Imagem que carrega significado tem descrição prevista no handoff
- [ ] Nada depende exclusivamente de hover para ser descoberto
- [ ] Animação essencial respeita `prefers-reduced-motion`

## Handoff para desenvolvimento

O que o dev precisa e quase nunca recebe:

**Tokens em JSON**, não em print. Cor, espaçamento, tipografia e raio no formato descrito em `design-system.md`.

**Specs por componente**, no formato:

```
Componente: Botao_Primario
Altura: 48px (mobile) / 40px (desktop)
Padding: 0 24px
Raio: 8px
Fundo: primary #2B59FF
Texto: 16/24 semibold, on-primary #FFFFFF
Estados:
  hover     fundo #2449D9
  foco      anel 2px #2B59FF, offset 2px
  ativo     fundo #1D3BB5
  desabilit opacidade 40%, sem hover
Comportamento: largura total em mobile, largura do conteúdo em desktop
```

**Comportamento responsivo** descrito em texto, com os pontos de quebra e o que muda em cada um. Design entregue só em uma largura força o dev a inventar, e ele vai inventar diferente do que você imaginou.

**Regras de conteúdo**: o que acontece com nome de 60 caracteres, lista com zero item, número de 8 dígitos. Sem isso, o layout quebra em produção.

**Estados de erro e carregamento** por tela, mesmo que só descritos.

**Spec de motion** por interação, no formato de `animacao.md`, com duração, easing, propriedade animada e o comportamento em movimento reduzido. Sem isso o dev inventa, e cada tela anima diferente.

## Se houver conector do Figma na sessão

Leia o arquivo real antes de opinar; recomendação genérica sobre design que você não viu queima a credibilidade do resto. A sequência de leitura, as skills obrigatórias do conector e o que fazer quando algo falha estão em `figma-mcp.md`.

Ao gerar código a partir do design, respeite os tokens do arquivo em vez de escrever valores literais, porque valor literal em código é a forma mais rápida de o design system morrer.

## Dados de cliente

Transcrições, exports de CRM e planilhas que apareçam nesse trabalho são confidenciais. Use o necessário para a tarefa e não reproduza trechos sensíveis nas telas nem nos exemplos. Em tela de demonstração, use dados fictícios realistas, nunca dados reais de cliente.
