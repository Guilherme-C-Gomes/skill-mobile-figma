# Caminho A: escrever direto no Figma

Quando as ferramentas `mcp__Figma__*` estão na sessão, a entrega deixa de ser um pacote de arquivos e passa a ser trabalho feito dentro do arquivo da pessoa. Muda o que você promete e muda a ordem de trabalho.

## Confirme antes de anunciar

Não diga que vai criar no Figma antes de uma chamada ter respondido. Chame `whoami`: ele devolve conta, times e plano. Se falhar, o conector não está de pé e você segue pelo caminho B sem drama.

Vale a pena olhar o plano na resposta. Em conta Starter, variáveis têm limite de coleções e modos, e recursos de biblioteca compartilhada são restritos. Se o plano não comportar o que você ia propor, diga antes de construir, não depois.

## As skills do conector são obrigatórias

O servidor do Figma publica skills próprias que são pré-requisito das ferramentas de escrita. Elas não são leitura opcional: pular gera falha difícil de diagnosticar, e você perde mais tempo depurando do que teria gasto lendo.

| Vai fazer | Carregue antes |
|---|---|
| Qualquer escrita via `use_figma` | `figma-use` |
| Montar página, tela ou view composta | `figma-use` + `figma-generate-design` |
| Criar variáveis, componentes, variantes, biblioteca | `figma-use` + `figma-generate-library` |
| Animar nós, keyframes, timeline | `figma-use` + `figma-use-motion` |
| Arquivo novo em branco | `figma-create-new-file` |
| Diagrama e fluxo em FigJam | `figma-generate-diagram` |
| Transformar design em código | `figma-design-to-code` |

Se a sessão tiver as skills como comandos (`/figma-use`), use por ali. Se não, leia pelo recurso do servidor: `skill://figma/<nome>/SKILL.md`.

## Onde escrever

Pergunte antes de escrever em arquivo que já existe. Um arquivo do Figma costuma ter trabalho de outras pessoas, e página nova aparecendo sem aviso é intrusão.

Três destinos possíveis, em ordem de preferência:

1. **Arquivo novo**, quando é exploração ou produto novo. Nada a quebrar.
2. **Página nova dentro do arquivo existente**, quando precisa conviver com o sistema já publicado. Nomeie a página com data e propósito.
3. **Editar frames existentes**, só quando a pessoa pedir isso explicitamente.

## Ordem de construção

A ordem importa porque cada camada depende da anterior. Construir tela antes de variável produz valor literal espalhado que ninguém troca depois.

1. **Levante o que já existe.** Componentes publicados, variáveis, estilos, telas anteriores. Reaproveitar o sistema da pessoa vale mais que qualquer sistema seu.
2. **Variáveis primeiro.** Cor semântica, espaçamento, raio e tipografia como variáveis de verdade, com modo claro e escuro se houver. É o que faz a troca de marca ser um clique em vez de um mutirão.
3. **Componentes com variantes**, com os estados amarrados às variáveis. Botão, campo, card, item de lista. Estado de foco incluído, que é o mais esquecido.
4. **Telas montadas a partir dos componentes**, seção por seção, com auto layout desde o começo.
5. **Prototype** ligando os frames, com a volta e os estados incluídos, como em `animacao.md`.
6. **Motion**, se a conta tiver o recurso liberado.

## Trabalhe incremental e mostre

Construa uma tela, tire captura, olhe, e só então siga. Montar oito telas de uma vez e descobrir que o espaçamento base estava errado significa refazer oito.

Depois de cada bloco relevante, use captura de tela para conferir o que de fato ficou no arquivo. O que você mandou criar e o que apareceu nem sempre coincidem, e checar cedo é barato.

Nomeie tudo enquanto cria, nunca depois. Camada renomeada em lote no fim é o momento em que os nomes deixam de bater e o Smart Animate para de funcionar.

## Ler antes de opinar

Para auditoria e handoff, leia o arquivo real antes de recomendar. Sequência útil:

1. Metadados e estrutura para entender o escopo, sem puxar o arquivo inteiro de uma vez.
2. Variáveis e estilos publicados, que revelam o sistema existente.
3. Contexto das telas de maior tráfego.
4. Captura de tela quando a questão for visual, porque descrição de estrutura não mostra hierarquia.

Divergência grande entre o que está desenhado e o que está publicado como componente indica sistema abandonado, e essa é uma constatação mais útil que qualquer crítica de cor.

Ao gerar código a partir do design, use os tokens do arquivo em vez de valores literais. Valor literal em código é a forma mais rápida de matar um design system.

## Quando algo falhar

- **Erro de permissão ou limite de requisição**: chame `whoami` para ver conta e plano antes de tentar outra coisa. Muito erro de "arquivo não encontrado" é, na verdade, arquivo de um time onde a conta não tem assento.
- **API não suportada**: o recurso não está liberado para essa conta. Não repita a chamada. Diga o que não deu, entregue o equivalente pelo caminho B, e siga.
- **Conector cai no meio**: o que já foi escrito no arquivo permanece. Diga o que ficou pronto e o que faltou, e ofereça terminar pelo caminho B.

## Dados de cliente

Transcrições, exports de CRM e planilhas que apareçam nesse trabalho são confidenciais. Em tela de demonstração, use dados fictícios realistas, nunca dados reais de cliente — inclusive porque arquivo do Figma costuma ser compartilhado com mais gente do que se imagina.

## Quando a cota não fecha a conta

O plano Starter dá **20 chamadas por mês**. Uma rodada de dez telas não cabe, e cada correção depois queima mais. Antes de começar um app inteiro por aqui, faça a conta: se o projeto tem mais de cinco telas, ou se você já sabe que vai haver rodadas de ajuste, o **caminho C** entrega mais e não gasta nada. Ver `references/plugin-figma.md`.

O conector continua útil mesmo assim, para o que o plugin não faz: inspecionar o que já existe no arquivo (`get_metadata`, `get_screenshot`) antes de decidir o que mudar. Duas ou três chamadas de leitura no começo do projeto valem mais que vinte de escrita.
