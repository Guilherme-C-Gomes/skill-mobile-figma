# Diagnóstico

Três momentos diferentes pedem perguntas diferentes: antes de desenhar (briefing), quando já existe algo (auditoria) e depois de entregar (refino). Este arquivo cobre os três.

## Como perguntar

Use `AskUserQuestion`, o seletor de opções clicável. Texto corrido com cinco perguntas numeradas produz resposta pela metade, porque exige que a pessoa escreva. Alternativa clicável ela responde inteira.

Regras que fazem a diferença:

- **No máximo quatro perguntas por rodada.** Mais que isso vira formulário e a pessoa abandona.
- **De 2 a 4 alternativas por pergunta**, concretas, com a recomendada em primeiro lugar marcada como "(Recomendado)".
- **Cada alternativa com consequência declarada**, não só o nome. "Mobile 390x844 — telas verticais, uma coluna, ação principal no rodapé ao alcance do polegar" ensina enquanto pergunta.
- **Não pergunte o que já foi dito.** Extraia da mensagem tudo que dá para inferir. Repetir pergunta respondida queima a confiança da pessoa no resto do trabalho.
- **Nunca pergunte o que você deveria decidir.** "Qual raio de borda?" é sua função, não dela. Pergunte o que só ela sabe: público, restrição, prioridade, marca.

Se a pessoa responder "sei lá, faz do seu jeito": não insista. Escolha o padrão mais defensável, declare a premissa em uma linha, e traga a alternativa de volta como pergunta de refino depois que ela tiver visto a tela. É muito mais fácil reagir a uma tela pronta do que responder no abstrato.

## O que você precisa saber, sempre

Independente do tipo de produto, cinco coisas decidem o desenho. Cubra estas e o resto você infere:

1. **Plataforma e tamanho** — define largura, densidade e alcance do polegar.
2. **Quem usa e o que essa pessoa está tentando fazer** — uma frase, não uma persona de dez slides.
3. **Os três jobs principais em ordem** — define o que é tela primária e o que é secundária.
4. **Marca existente** — cor, logo, fonte, referência, print de concorrente. Se não houver, você propõe.
5. **Escopo** — quantas telas. Se não souber, proponha o mínimo viável do fluxo principal.

## Baterias por tipo de produto

Depois de cobrir os cinco acima, o que realmente muda o desenho depende do tipo. Use a bateria que casa com o pedido.

### App mobile

- **Frequência de uso**: várias vezes por dia (velocidade e atalho mandam) / algumas vezes por semana / esporádico (precisa reensinar a cada visita).
- **Contexto de uso**: parado com atenção / em movimento, uma mão só / em campo com internet ruim.
- **Navegação**: tab bar de 3 a 5 seções paralelas / stack linear com voltar / híbrido.
- **Cadastro**: obrigatório antes de usar / opcional, deixa experimentar antes / sem conta.

### SaaS web

- **Densidade**: densa, o usuário é operador e passa o dia ali / arejada, uso ocasional.
- **Volume de dados por tela**: dezenas de registros / centenas com filtro e busca / milhares com paginação e ações em massa.
- **Perfis**: um só / vários com permissões diferentes (muda menu e ações visíveis).
- **Onde a pessoa passa 80% do tempo**: uma tela núcleo domina o design; sem isso o menu vira lista de desejos.

### E-commerce

- **Catálogo**: poucos produtos com muita explicação / muitos produtos com filtro forte.
- **Decisão de compra**: por impulso (checkout em um toque) / comparação e pesquisa (ficha rica, avaliação, comparativo).
- **Checkout**: convidado permitido ou conta obrigatória.
- **O que vende**: foto, preço, prova social ou prazo de entrega. Isso define o topo da ficha de produto.

### Dashboard e relatório

- **Decisão que a pessoa toma olhando**: se não houver decisão, é relatório, não dashboard, e o desenho muda.
- **Recorte de tempo**: tempo real / diário / mensal.
- **Hierarquia**: um número que manda e o resto é contexto / vários indicadores de peso igual.
- **Ação a partir do dado**: só olha / exporta / age direto dali.

Para o desenho dos gráficos em si, carregue também a skill de visualização de dados da sessão, se houver.

### Landing page e site institucional

- **Objetivo único da página**: cadastro, agendamento, venda direta ou download. Página com dois objetivos converte menos que página com um.
- **Temperatura do tráfego**: já conhece a marca / veio de anúncio e não conhece nada.
- **Prova disponível**: número, depoimento, logo de cliente, caso. Sem prova a página vira só adjetivo.
- **Tamanho**: uma dobra direta ao ponto / página longa que vence objeção por objeção.

## Diagnóstico de algo que já existe

Quando a pessoa cola link, print ou conecta o arquivo, **leia antes de opinar**. Recomendação genérica sobre design que você não viu é o jeito mais rápido de perder credibilidade. Com o conector: extraia páginas, frames, componentes e variáveis publicadas. Sem conector: peça print das três telas de maior tráfego.

Antes de listar problema, pergunte **o que incomoda a pessoa** e **o que não pode mudar**. Sem isso você vai propor redesenho de algo que é restrição de negócio ou decisão já brigada internamente.

Entregue nota por critério, porque nota isolada não orienta e lista solta de problemas não prioriza:

| Critério | O que olhar | Peso |
|---|---|---|
| Fluxo | Passos até o valor, becos sem saída, volta obrigatória | Alto |
| Hierarquia | Em meio segundo o olho vai ao lugar certo? Uma única ação primária? | Alto |
| Layout | Alinhamento, grid, ritmo, densidade, espaçamento fora de escala | Médio |
| Consistência | Mesmo componente com tratamentos diferentes entre telas | Médio |
| Estados | Vazio, carregando e erro existem ou só o estado feliz? | Alto |
| Acessibilidade | Contraste medido, alvo de toque, foco visível | Alto |
| Texto | Rótulo diz o que acontece? Erro orienta? | Médio |
| Movimento | Transição definida ou cada tela anima diferente? | Baixo |

Nota de 1 a 5 por critério, com **uma frase de evidência concreta** em cada, citando a tela. "Hierarquia 2/5: na Home há três botões azuis do mesmo tamanho competindo" vale mais que "hierarquia fraca".

Para cada problema, três partes: **o que está acontecendo**, **por que custa caro**, **o que fazer**. Crítica sem a terceira parte é reclamação.

Separe problema objetivo de preferência sua. "Contraste 2.1:1 reprova em WCAG AA" é fato; "esse azul é frio demais" é gosto. Misturar os dois faz a pessoa descartar os dois.

Feche com as três correções de maior retorno pelo esforço, nessa ordem. Lista de vinte itens não é acionável.

## Perguntas de refino, depois de entregar

Entregar e calar desperdiça a melhor chance de acertar. A pessoa acabou de ver a tela e é aí que ela consegue reagir, mas quase nunca sabe nomear o que incomodou. Sua função é oferecer os eixos.

Pergunte sobre decisões que **você tomou e que teriam alternativa defensável**, não sobre coisa óbvia. No máximo três, com `AskUserQuestion`. Ofereça o eixo, não o pedido de aprovação: "está bom?" não gera informação, "mais denso ou mais arejado?" gera.

Eixos que costumam render:

- **Densidade**: mais informação por tela, ou mais respiro e rolagem.
- **Peso da marca**: cor da marca só na ação principal, ou presente em superfícies e cabeçalhos.
- **Hierarquia da ação**: ação principal fixa no rodapé sempre visível, ou dentro do conteúdo.
- **Tom do texto**: direto e funcional, ou próximo e conversado.
- **Profundidade visual**: plano com borda, ou elevado com sombra.
- **Nível de detalhe do card**: só o essencial com o resto no toque, ou tudo à vista.
- **Movimento**: sóbrio e rápido, ou expressivo com transições visíveis.

Uma pergunta de refino boa cita o que você fez e por quê, e oferece o contrário com a consequência: "Deixei o card mostrando só nome, status e valor para a lista respirar. Posso trazer prazo e responsável para dentro do card, o que ajuda quem confere sem abrir, ao custo de uma lista mais pesada. Qual serve melhor?"

Também vale perguntar **o que expandir**: quais telas seguintes, quais estados adicionais, se quer as variações de dark mode. Isso transforma uma entrega em um próximo passo em vez de um ponto final.
