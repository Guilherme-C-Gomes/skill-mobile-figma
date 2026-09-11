# mobile-figma

Skill do Claude que desenha o app mobile inteiro, do fluxo ao movimento, e entrega dentro do Figma por conector, por plugin local ou por arquivos prontos para importar.

Cobre diagnóstico, fluxo, design system, layout, telas desenhadas, estados, animação, auditoria e handoff. Referência de tela: 390x844, dedo como ponteiro, barra inferior, safe area.

Três princípios organizam a skill: decisão errada barata vem antes de decisão cara, gere em vez de desenhar tela por tela, e meça em vez de estimar.

## Conteúdo

```
skills/mobile-figma/
  SKILL.md
  references/
    fluxo-e-arquitetura.md
    design-system.md
    layout.md
    material-vidro.md
    referencia-visual.md
    animacao.md
    gerador.md
    validadores.md
    diagnostico.md
    auditoria-e-handoff.md
    figma-mcp.md
    plugin-figma.md
    export-figma.md
  scripts/
    gerar_plugin_figma.py
    medida_texto.py
    contraste.py
    check_svg_figma.py
```

## Como instalar

```bash
git clone https://github.com/Guilherme-C-Gomes/skill-mobile-figma.git
cp -r skill-mobile-figma/skills/mobile-figma ~/.claude/skills/
```

Depois é só chamar `/mobile-figma` numa sessão do Claude.

## Dependências

Os validadores e o gerador rodam em Python. A entrega dentro do Figma usa o conector MCP do Figma quando disponível; sem ele, a skill gera plugin local ou arquivos para importar.
