#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera um plugin local do Figma que importa um projeto inteiro sem gastar API.

Pega uma pasta de SVGs (um por tela) e cospe manifest.json, code.js, ui.html e
LEIA-ME.md. O code.js carrega os SVGs dentro de si, entao rodar o plugin escreve
tudo no arquivo aberto com ZERO chamada de conector. Ver references/plugin-figma.md.

    python3 gerar_plugin_figma.py telas/ --saida plugin-meuapp \\
        --projeto "Meu App" --tokens tokens.json --ligacoes ligacoes.json

  telas/          pasta com os .svg, importados na ordem alfabetica do nome
  --tokens        JSON opcional: {"cores": {"cor/bg": "#0A0A12"},
                                  "numeros": {"raio/card": 16},
                                  "tipo": {"App/H1": [24, "Bold"]}}
  --ligacoes      JSON opcional: lista de [tela, alvo|null, destino, gatilho,
                                 espera_s, transicao, ms]
  --vidro         regex de nomes que recebem BACKGROUND_BLUR (repetivel)
  --desfoque      raio do desfoque, padrao 28

O que ele NAO faz: inventar estados derivados nem o layout da secao para o seu
projeto especifico. Ele deixa os ganchos prontos (D.estados, D.ligacoes) para
voce preencher pelo seu gerador.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile


# --------------------------------------------------------------- minificacao
def poda(m):
    """Encurta um numero sem mudar o que ele significa.

    Arredondar por casa decimal fixa transforma -0.0130 em -0, e uma matriz com
    determinante zero deixa o elemento invisivel no Figma e faz qualquer
    animacao nele falhar com "transform is not invertible". Aqui o corte so
    acontece enquanto o erro relativo fica abaixo de 0,1%, e jamais devolve
    zero para um numero que nao era zero.
    """
    t = m.group(0)
    v = float(t)
    if v == int(v):
        return str(int(v))
    for casas in range(1, 7):
        c = round(v, casas)
        if c != 0 and abs(c - v) <= abs(v) * 0.001:
            return f"{c:.{casas}f}".rstrip("0").rstrip(".")
    return t


def minificar(s):
    s = re.sub(r'(?<=["\s(])-?\d+\.\d+(?=["\s,)])', poda, s)
    s = s.replace(' xmlns:xlink="http://www.w3.org/1999/xlink"', "")
    s = re.sub(r'\sxlink:href="[^"]*"', "", s)
    s = re.sub(r">\s+<", "><", s)
    s = re.sub(r"\s{2,}", " ", s)
    return s.strip()


def nome_da_tela(arquivo):
    """01-home-carregando.svg -> "01 Home carregando"."""
    base = os.path.splitext(os.path.basename(arquivo))[0]
    partes = base.replace("_", "-").split("-")
    if partes and partes[0].isdigit():
        num, resto = partes[0], partes[1:]
    else:
        num, resto = "", partes
    texto = " ".join(resto)
    texto = texto[:1].upper() + texto[1:] if texto else base
    return (num + " " + texto).strip()


# ------------------------------------------------------------------ code.js
# Marcadores em vez de %-formatacao: o proprio JS usa % (i % COLUNAS, 100%),
# e formatar com % aqui quebraria em cima do operador de resto.
CODE = r"""// @@PROJETO@@ — importar projeto
// Gerado automaticamente. Nao editar a mao: o conteudo e substituido a cada
// atualizacao do design. Versao carregada: @@VERSAO@@
const D = @@DADOS@@;

const SECAO = @@SECAO@@;
const LARG = 450, LINHA = 1000, COLUNAS = 7;

figma.showUI(__html__, { width: 400, height: 640, themeColors: true });
figma.ui.postMessage({ tipo: 'pronto', versao: D.versao, telas: D.telas.length });

function log(t, nivel) {
  figma.ui.postMessage({ tipo: 'log', texto: t, nivel: nivel || 'ok' });
}

// ---------------------------------------------------- coletor do relatorio
// Nada pode derrubar a rodada inteira: cada operacao roda isolada e o que
// falhar vira uma linha nomeada no relatorio do fim.
const REL = { contas: {}, problemas: [] };
function zerar() {
  REL.contas = { telas: 0, estados: 0, variaveis: 0, estilos: 0,
                 ligacoes: 0, ignoradas: 0, vidro: 0 };
  REL.problemas = [];
}
zerar();
const msgDe = e => (e && e.message ? e.message : String(e));
function problema(fase, alvo, motivo) {
  REL.problemas.push({ fase: fase, alvo: alvo, motivo: String(motivo) });
}
function seguro(fase, rotulo, fn) {
  try { return fn(); } catch (err) { problema(fase, rotulo, msgDe(err)); }
}

const rgb = h => ({
  r: parseInt(h.slice(1, 3), 16) / 255,
  g: parseInt(h.slice(3, 5), 16) / 255,
  b: parseInt(h.slice(5, 7), 16) / 255,
});

async function fontes() {
  for (const st of ['Regular', 'Medium', 'Semi Bold', 'Bold']) {
    try { await figma.loadFontAsync({ family: D.fonte, style: st }); } catch (e) {}
  }
}

const achar = (raiz, nome) => raiz.findOne(n => n.name === nome);
const acharSecao = pg => pg.children.find(n => n.type === 'SECTION' && n.name === SECAO) || null;

function criarSecao(pg) {
  const limite = pg.children.length
    ? Math.max.apply(null, pg.children.map(n => n.x + n.width)) : 0;
  const s = figma.createSection();
  pg.appendChild(s);
  s.name = SECAO;
  s.x = limite + 400; s.y = 0;
  s.resizeWithoutConstraints(LARG * COLUNAS + 80, 1200);
  return s;
}

// ------------------------------------------------- retoque de um clone
function pintar(no, receita) {
  if (!no || !receita) return;
  no.fills = [{ type: 'SOLID', color: rgb(receita.fill), opacity: receita.fo }];
  no.strokes = receita.stroke
    ? [{ type: 'SOLID', color: rgb(receita.stroke), opacity: receita.so }] : [];
  if (receita.stroke) no.strokeWeight = 1;
}

async function escrever(no, valor) {
  if (!no || no.type !== 'TEXT') return;
  const f = no.fontName;
  if (f && f !== figma.mixed) { try { await figma.loadFontAsync(f); } catch (e) {} }
  no.characters = valor;
}

function redimensionar(no, w, h) {
  if (!no) return;
  const lw = Math.max(0.01, w === null || w === undefined ? no.width : w);
  const lh = Math.max(0.01, h === null || h === undefined ? no.height : h);
  if (no.resizeWithoutConstraints) no.resizeWithoutConstraints(lw, lh);
  else if (no.resize) no.resize(lw, lh);
}

// Escala em torno do proprio centro. Sem giro de proposito: grupos vindos de
// SVG costumam ter matriz espelhada, e pedir rotacao nela deixa a transformada
// nao invertivel — o Figma recusa e a importacao para.
function transformar(no, escala) {
  if (!no || !escala || escala === 1 || !no.rescale) return;
  const a = no.absoluteBoundingBox; if (!a) return;
  const cx = a.x + a.width / 2, cy = a.y + a.height / 2;
  no.rescale(escala);
  const b = no.absoluteBoundingBox; if (!b) return;
  no.x += cx - (b.x + b.width / 2);
  no.y += cy - (b.y + b.height / 2);
}

async function aplicarEstado(clone, e) {
  if (e.chips) {
    const lista = e.chips[0], ativo = e.chips[1];
    for (const c of lista) {
      seguro('retoque', 'chip ' + c, () => pintar(achar(clone, c + '_Fundo'),
        c === ativo ? D.chipAtivo : D.chipInativo));
    }
  }
  for (const nome in (e.textos || {})) {
    try { await escrever(achar(clone, nome), e.textos[nome]); }
    catch (err) { problema('retoque', 'texto ' + nome, msgDe(err)); }
  }
  for (const nome of (e.esconder || [])) {
    seguro('retoque', 'esconder ' + nome, () => {
      const n = achar(clone, nome); if (n) n.visible = false; });
  }
  for (const nome in (e.opacidade || {})) {
    seguro('retoque', 'opacidade ' + nome, () => {
      const n = achar(clone, nome); if (n) n.opacity = e.opacidade[nome]; });
  }
  // delta, nunca coordenada absoluta: dentro de um grupo o x/y e relativo ao pai
  for (const nome in (e.mover || {})) {
    seguro('retoque', 'mover ' + nome, () => {
      const n = achar(clone, nome); if (!n) return;
      const v = e.mover[nome];
      if (typeof v === 'number') n.y += v;
      else { if (v.dx) n.x += v.dx; if (v.dy) n.y += v.dy; }
    });
  }
  for (const nome in (e.larguras || {})) {
    seguro('retoque', 'largura ' + nome,
           () => redimensionar(achar(clone, nome), e.larguras[nome], null));
  }
  for (const nome in (e.retangulos || {})) {
    seguro('retoque', 'retangulo ' + nome, () => {
      const n = achar(clone, nome); if (!n) return;
      const r = e.retangulos[nome];
      redimensionar(n, r.dw ? n.width + r.dw : null, r.dh ? n.height + r.dh : null);
      if (r.dy) n.y += r.dy;
    });
  }
  for (const nome in (e.transformar || {})) {
    seguro('retoque', 'escala ' + nome,
           () => transformar(achar(clone, nome), e.transformar[nome].escala));
  }
}

// ------------------------------------------------------------------ vidro
// Desfoque de fundo nao cabe em SVG nem em createNodeFromSvg. O material so
// fica completo aqui, como efeito de camada.
function aplicarVidro(sec) {
  if (!D.vidro || !D.vidro.padroes.length) return;
  const regras = D.vidro.padroes.map(p => new RegExp(p));
  let n = 0;
  for (const f of sec.children) {
    for (const no of f.findAll(x => regras.some(r => r.test(x.name)))) {
      seguro('vidro', f.name + ' / ' + no.name, () => {
        no.effects = [{ type: 'BACKGROUND_BLUR', radius: D.vidro.desfoque, visible: true }];
        n++;
      });
    }
  }
  REL.contas.vidro = n;
  if (n) log(n + ' superfícies com desfoque de fundo', 'destaque');
}

// ------------------------------------------------------------------ telas
function posicionar(sec) {
  const porNome = {};
  for (const f of sec.children) porNome[f.name] = f;
  const ordem = D.ordem.length ? D.ordem
    : D.telas.map(t => t.nome).concat(D.estados.map(e => e.nome));
  let i = 0, maxCol = 0;
  for (const nome of ordem) {
    const f = porNome[nome]; if (!f) continue;
    const c = i % COLUNAS, l = Math.floor(i / COLUNAS);
    f.x = sec.x + 40 + c * LARG;
    f.y = sec.y + 120 + l * LINHA;
    maxCol = Math.max(maxCol, c + 1); i++;
  }
  const linhas = Math.ceil(i / COLUNAS);
  sec.resizeWithoutConstraints(maxCol * LARG + 80, 120 + linhas * LINHA);
}

async function importarTelas() {
  await fontes();
  const pg = figma.currentPage;
  let sec = acharSecao(pg);
  if (!sec) { sec = criarSecao(pg); log('Seção criada'); }
  else log('Seção encontrada — substituindo as telas');

  // remove so o que este plugin criou antes, pelo nome exato
  const meus = D.telas.map(t => t.nome).concat(D.estados.map(e => e.nome));
  for (const filho of sec.children.slice()) {
    if (meus.indexOf(filho.name) !== -1) filho.remove();
  }

  const base = {};
  for (const t of D.telas) {
    const n = figma.createNodeFromSvg(t.svg);
    n.name = t.nome;
    // sem recorte, elemento que descansa fora da tela de proposito fica a vista
    seguro('recorte', t.nome, () => { n.clipsContent = true; });
    sec.appendChild(n);
    base[t.nome] = n;
    REL.contas.telas++;
    log('· ' + t.nome);
  }
  // estados derivados: clone da tela base + retoque. Clone garante nome de
  // camada identico peca por peca, que e do que o Smart Animate vive.
  for (const e of D.estados) {
    const b = base[e.base];
    if (!b) { problema('estado', e.nome, 'tela base "' + e.base + '" ausente'); continue; }
    let c = null;
    try {
      c = b.clone(); c.name = e.nome; sec.appendChild(c);
      await aplicarEstado(c, e);
      base[e.nome] = c; REL.contas.estados++;
      log('· ' + e.nome);
    } catch (err) {
      problema('estado', e.nome, msgDe(err));
      if (c) base[e.nome] = c;
    }
  }
  posicionar(sec);
  aplicarVidro(sec);
  figma.currentPage.selection = [sec];
  figma.viewport.scrollAndZoomIntoView([sec]);
  return sec;
}

// ----------------------------------------------------------------- tokens
async function criarTokens() {
  await fontes();
  const cols = await figma.variables.getLocalVariableCollectionsAsync();
  let col = cols.find(c => c.name === D.colecao);
  if (!col) { col = figma.variables.createVariableCollection(D.colecao);
              log('Coleção ' + D.colecao + ' criada'); }
  else log('Coleção ' + D.colecao + ' encontrada — atualizando');
  const modo = col.modes[0].modeId;
  const existentes = {};
  for (const id of col.variableIds) {
    const v = await figma.variables.getVariableByIdAsync(id);
    if (v) existentes[v.name] = v;
  }
  for (const nome in D.cores) {
    seguro('token', nome, () => {
      let v = existentes[nome];
      if (!v) { v = figma.variables.createVariable(nome, col, 'COLOR');
                v.scopes = ['FRAME_FILL', 'SHAPE_FILL', 'TEXT_FILL', 'STROKE_COLOR']; }
      v.setValueForMode(modo, rgb(D.cores[nome])); REL.contas.variaveis++;
    });
  }
  for (const nome in D.numeros) {
    seguro('token', nome, () => {
      let v = existentes[nome];
      if (!v) { v = figma.variables.createVariable(nome, col, 'FLOAT');
                v.scopes = nome.indexOf('raio') === 0 ? ['CORNER_RADIUS'] : ['GAP', 'WIDTH_HEIGHT']; }
      v.setValueForMode(modo, D.numeros[nome]); REL.contas.variaveis++;
    });
  }
  const estilos = await figma.getLocalTextStylesAsync();
  for (const nome in D.tipo) {
    seguro('estilo', nome, () => {
      let s = estilos.find(x => x.name === nome);
      if (!s) { s = figma.createTextStyle(); s.name = nome; }
      s.fontName = { family: D.fonte, style: D.tipo[nome][1] };
      s.fontSize = D.tipo[nome][0];
      REL.contas.estilos++;
    });
  }
}

// -------------------------------------------------------------- prototipo
async function ligarPrototipo() {
  const sec = acharSecao(figma.currentPage);
  if (!sec) { problema('ligação', 'seção', 'importe as telas primeiro'); return; }
  const T = {};
  for (const f of sec.children) T[f.name] = f;
  const trans = (tipo, ms) => ({ type: tipo, easing: { type: 'EASE_OUT' }, duration: ms / 1000 });
  const rotulo = (t, a) => t + (a ? ' / ' + a : ' (a própria tela)');

  // `esperado` marca as ausencias que fazem parte do desenho — aba de navegacao
  // numa tela sem barra, pilula que ja e a ativa. Se elas entrarem na conta de
  // erros, o relatorio vira ruido e ninguem le.
  async function liga(telaNome, alvoNome, destino, gatilho, espera, tipo, ms, esperado) {
    const tela = T[telaNome], dest = T[destino];
    if (!tela) { problema('ligação', rotulo(telaNome, alvoNome), 'tela de origem não existe'); return; }
    if (!dest) { problema('ligação', rotulo(telaNome, alvoNome),
                          'tela de destino "' + destino + '" não existe'); return; }
    if (tela === dest) { REL.contas.ignoradas++; return; }
    const no = alvoNome ? tela.findOne(x => x.name === alvoNome) : tela;
    if (!no) {
      if (esperado) REL.contas.ignoradas++;
      else problema('ligação', rotulo(telaNome, alvoNome), 'elemento não encontrado na tela');
      return;
    }
    try {
      await no.setReactionsAsync([{
        trigger: gatilho === 'TIMEOUT'
          ? { type: 'AFTER_TIMEOUT', timeout: espera }
          : { type: 'ON_CLICK' },
        actions: [{ type: 'NODE', destinationId: dest.id, navigation: 'NAVIGATE',
                    transition: trans(tipo, ms), preserveScrollPosition: false }],
      }]);
      REL.contas.ligacoes++;
    } catch (err) {
      problema('ligação', rotulo(telaNome, alvoNome), 'o Figma recusou — ' + msgDe(err));
    }
  }

  for (const l of D.ligacoes) await liga(l[0], l[1], l[2], l[3], l[4], l[5], l[6], false);
  const entrada = T[(D.ordem[0] || (D.telas[0] || {}).nome)];
  if (entrada) figma.currentPage.flowStartingPoints = [{ nodeId: entrada.id, name: D.fluxo }];
}

// ---------------------------------------------------------------- relatorio
function relatorio(acao) {
  const c = REL.contas;
  log('');
  log('──────────  relatório  ──────────', 'destaque');
  if (acao === 'telas' || acao === 'tudo') {
    log('telas do app     ' + c.telas + ' de ' + D.telas.length);
    if (D.estados.length) log('estados          ' + c.estados + ' de ' + D.estados.length);
    if (c.vidro) log('vidro            ' + c.vidro + ' superfícies com desfoque');
  }
  if (acao === 'tokens' || acao === 'tudo') {
    log('variáveis        ' + c.variaveis);
    log('estilos de texto ' + c.estilos);
  }
  if (acao === 'prototipo' || acao === 'tudo') {
    log('ligações         ' + c.ligacoes + ' criadas');
    log('                 ' + c.ignoradas + ' ignoradas de propósito');
  }
  if (!REL.problemas.length) {
    log('erros            nenhum', 'destaque');
    figma.ui.postMessage({ tipo: 'relatorio', erros: 0 });
    return;
  }
  log('erros            ' + REL.problemas.length, 'erro');
  const porFase = {};
  for (const p of REL.problemas) (porFase[p.fase] = porFase[p.fase] || []).push(p);
  for (const f in porFase) {
    log('· ' + f + ' (' + porFase[f].length + ')', 'erro');
    porFase[f].slice(0, 40).forEach(p => log('    ' + p.alvo + ' — ' + p.motivo, 'erro'));
    if (porFase[f].length > 40) log('    … e mais ' + (porFase[f].length - 40), 'erro');
  }
  figma.ui.postMessage({ tipo: 'relatorio', erros: REL.problemas.length });
}

figma.ui.onmessage = async msg => {
  zerar();
  try {
    if (msg.acao === 'telas') await importarTelas();
    if (msg.acao === 'tokens') await criarTokens();
    if (msg.acao === 'prototipo') await ligarPrototipo();
    if (msg.acao === 'tudo') {
      await importarTelas(); await criarTokens(); await ligarPrototipo();
    }
  } catch (err) {
    problema('execução', msg.acao, msgDe(err));
  }
  try { relatorio(msg.acao); } catch (err) { log('relatório: ' + msgDe(err), 'erro'); }
  figma.ui.postMessage({ tipo: 'fim' });
};
"""


# ------------------------------------------------------------------ ui.html
UI = """<!doctype html>
<meta charset="utf-8">
<title>__PROJETO__</title>
<style>
  :root { color-scheme: light dark; }
  body { margin:0; padding:16px; font:13px/1.5 Inter,-apple-system,"Segoe UI",sans-serif;
         background:#0A0A12; color:#FFF; }
  h1 { font-size:14px; margin:0 0 2px; font-weight:600; }
  .sub { color:#8A8AA0; font-size:11.5px; margin:0 0 14px; }
  button { width:100%; margin-bottom:8px; padding:11px 12px; border-radius:12px;
           border:1px solid #2E2E42; background:#1E1E2B; color:#FFF;
           font:500 13px Inter,sans-serif; cursor:pointer; text-align:left; }
  button:hover { background:#26263a; }
  button.principal { background:#9E05D2; border-color:transparent; font-weight:600; }
  button:disabled { opacity:.5; cursor:default; }
  button.mini { width:auto; margin:0; padding:5px 10px; font-size:11.5px; border-radius:8px; }
  .dica { color:#8A8AA0; font-size:11px; margin:2px 0 14px; }
  .cabeca { display:flex; align-items:center; justify-content:space-between; margin-bottom:6px; }
  #placar { font-size:11.5px; color:#8A8AA0; }
  #placar.ok { color:#3DD68C; } #placar.falha { color:#FF7A85; }
  #log { background:#15151F; border:1px solid #2E2E42; border-radius:12px; padding:10px 12px;
         height:240px; overflow:auto; font:11.5px/1.6 ui-monospace,Menlo,monospace; color:#9A9AAD; }
  #log div.destaque { color:#3DD68C; } #log div.erro { color:#FF7A85; }
  .rodape { color:#6C6C80; font-size:10.5px; margin-top:10px; }
</style>
<h1>__PROJETO__</h1>
<p class="sub">Cria as telas numa seção própria da página atual. Nada fora dela é tocado.</p>

<button class="principal" data-acao="tudo">Importar tudo<br>
  <span style="font-weight:400;opacity:.8">telas + variáveis + estilos + protótipo</span></button>
<button data-acao="telas">Só as telas</button>
<button data-acao="tokens">Só variáveis e estilos de texto</button>
<button data-acao="prototipo">Só ligar o protótipo</button>
<p class="dica">Rodar de novo substitui as telas pela versão nova — não duplica.</p>

<div class="cabeca">
  <span id="placar">nenhuma execução ainda</span>
  <button id="copiar" class="mini" disabled>Copiar relatório</button>
</div>
<div id="log"><div>Pronto.</div></div>
<p class="rodape" id="rodape"></p>

<script>
  const log = document.getElementById('log');
  const placar = document.getElementById('placar');
  const btCopiar = document.getElementById('copiar');
  let texto = [];

  function linha(t, n) {
    texto.push(t);
    const d = document.createElement('div');
    d.textContent = t; if (n && n !== 'ok') d.className = n;
    log.appendChild(d); log.scrollTop = log.scrollHeight;
  }

  document.querySelectorAll('button[data-acao]').forEach(b => {
    b.onclick = () => {
      document.querySelectorAll('button').forEach(x => x.disabled = true);
      log.innerHTML = ''; texto = [];
      placar.className = ''; placar.textContent = 'rodando…';
      linha('— ' + b.dataset.acao + ' —');
      parent.postMessage({ pluginMessage: { acao: b.dataset.acao } }, '*');
    };
  });

  btCopiar.onclick = () => {
    const t = document.createElement('textarea');
    t.value = texto.join(String.fromCharCode(10));
    document.body.appendChild(t); t.select();
    document.execCommand('copy'); t.remove();
    btCopiar.textContent = 'copiado';
    setTimeout(() => { btCopiar.textContent = 'Copiar relatório'; }, 1400);
  };

  onmessage = e => {
    const m = e.data.pluginMessage; if (!m) return;
    if (m.tipo === 'log') linha(m.texto, m.nivel);
    if (m.tipo === 'pronto')
      document.getElementById('rodape').textContent =
        'versão ' + m.versao + ' · ' + m.telas + ' telas carregadas no plugin';
    if (m.tipo === 'relatorio') {
      placar.className = m.erros ? 'falha' : 'ok';
      placar.textContent = m.erros
        ? m.erros + (m.erros === 1 ? ' erro — veja abaixo' : ' erros — veja abaixo')
        : 'concluído sem erros';
    }
    if (m.tipo === 'fim') {
      document.querySelectorAll('button').forEach(x => x.disabled = false);
      btCopiar.disabled = false;
    }
  };
</script>
"""


LEIA = """# Plugin "@@PROJETO@@"

Plugin local de desenvolvimento. Carrega dentro de si a versão mais recente das
telas, dos tokens e das ligações de protótipo, e escreve tudo no arquivo do Figma
**sem gastar nenhuma chamada de API**.

**Versão nesta pasta: @@VERSAO@@** — @@N@@ tela(s).

## Instalar (uma vez só)

1. Figma **desktop** (plugin de desenvolvimento não aparece na web).
2. Menu → Plugins → Development → **Import plugin from manifest…**
3. Escolha o `manifest.json` desta pasta.

## Usar

Abra o arquivo, deixe a página certa selecionada e rode o plugin.

| Botão | O que faz |
|---|---|
| Importar tudo | Telas + variáveis + estilos + protótipo |
| Só as telas | As telas, sem tokens |
| Só variáveis e estilos | A coleção de tokens e a escala tipográfica |
| Só ligar o protótipo | Refaz as ligações entre as telas |

Tudo é criado dentro de uma seção chamada **"@@SECAO@@"**. Nada fora dela é tocado,
e rodar de novo **substitui** as telas em vez de duplicar.

Toda execução termina com um relatório: quantas telas, quantas ligações, e
exatamente o que falhou. O botão **Copiar relatório** copia o log inteiro.

## Atualizar

Quando o design mudar, os arquivos desta pasta são substituídos. Você não precisa
reinstalar: botão direito no canvas → Plugins → Development → **Hot reload plugin**.

`code.js` é gerado automaticamente e não deve ser editado à mão.
"""


def conferir(caminho, rotulo, extrai=None):
    """Recusa entregar arquivo que nao compila.

    Um escape a mais na geracao ja transformou um \\n em quebra de linha de
    verdade dentro de uma string JS e matou o script inteiro: a janela abria e
    os botoes nao faziam nada. `node --check` pega isso em um segundo.
    """
    fonte = open(caminho, encoding="utf-8").read()
    if extrai:
        m = re.search(extrai, fonte, re.S)
        if not m:
            return f"{rotulo}: não achei o bloco de script"
        fonte = m.group(1)
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(fonte)
        tmp = fh.name
    try:
        r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    except FileNotFoundError:
        return f"{rotulo}: node não encontrado, checagem pulada"
    return f"{rotulo}: ok" if r.returncode == 0 else f"{rotulo} NÃO COMPILA:\n{r.stderr}"


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("telas", help="pasta com os .svg")
    p.add_argument("--saida", default="plugin-figma")
    p.add_argument("--projeto", default="Projeto")
    p.add_argument("--secao", default=None, help='nome da seção no Figma')
    p.add_argument("--fonte", default="Inter")
    p.add_argument("--colecao", default=None, help="nome da coleção de variáveis")
    p.add_argument("--tokens", default=None, help="JSON com cores/numeros/tipo")
    p.add_argument("--ligacoes", default=None, help="JSON com a lista de ligações")
    p.add_argument("--estados", default=None, help="JSON com as receitas de estado")
    p.add_argument("--vidro", action="append", default=[],
                   help="regex de nomes que recebem BACKGROUND_BLUR")
    p.add_argument("--desfoque", type=int, default=28)
    a = p.parse_args()

    import datetime
    versao = datetime.date.today().isoformat()
    secao = a.secao or f"{a.projeto} — telas"
    colecao = a.colecao or a.projeto

    arquivos = sorted(f for f in os.listdir(a.telas) if f.lower().endswith(".svg"))
    if not arquivos:
        print(f"nenhum .svg em {a.telas}")
        sys.exit(2)
    telas = [{"nome": nome_da_tela(f),
              "svg": minificar(open(os.path.join(a.telas, f), encoding="utf-8").read())}
             for f in arquivos]

    tok = json.load(open(a.tokens, encoding="utf-8")) if a.tokens else {}
    dados = {
        "versao": versao, "fonte": a.fonte, "colecao": colecao,
        "fluxo": f"Fluxo {a.projeto}",
        "telas": telas,
        "estados": json.load(open(a.estados, encoding="utf-8")) if a.estados else [],
        "ordem": [t["nome"] for t in telas],
        "cores": tok.get("cores", {}),
        "numeros": tok.get("numeros", {}),
        "tipo": tok.get("tipo", {}),
        "ligacoes": json.load(open(a.ligacoes, encoding="utf-8")) if a.ligacoes else [],
        "chipAtivo": tok.get("chipAtivo", {"fill": "#9E05D2", "fo": 1, "stroke": None, "so": 0}),
        "chipInativo": tok.get("chipInativo",
                               {"fill": "#FFFFFF", "fo": 0.07, "stroke": "#FFFFFF", "so": 0.28}),
        "vidro": {"padroes": a.vidro, "desfoque": a.desfoque},
    }

    os.makedirs(a.saida, exist_ok=True)
    open(f"{a.saida}/manifest.json", "w", encoding="utf-8").write(json.dumps({
        "name": f"{a.projeto} — importar",
        "id": re.sub(r"[^a-z0-9]+", "-", a.projeto.lower()).strip("-") + "-importar",
        "api": "1.0.0", "main": "code.js", "ui": "ui.html",
        "editorType": ["figma"], "documentAccess": "dynamic-page",
        "networkAccess": {"allowedDomains": ["none"]},
    }, indent=2, ensure_ascii=False))

    codigo = (CODE.replace("@@PROJETO@@", a.projeto)
                  .replace("@@VERSAO@@", versao)
                  .replace("@@SECAO@@", json.dumps(secao, ensure_ascii=False))
                  .replace("@@DADOS@@", json.dumps(dados, ensure_ascii=False)))
    open(f"{a.saida}/code.js", "w", encoding="utf-8").write(codigo)
    open(f"{a.saida}/ui.html", "w", encoding="utf-8").write(UI.replace("__PROJETO__", a.projeto))
    open(f"{a.saida}/LEIA-ME.md", "w", encoding="utf-8").write(
        LEIA.replace("@@PROJETO@@", a.projeto).replace("@@VERSAO@@", versao)
            .replace("@@N@@", str(len(telas))).replace("@@SECAO@@", secao))

    checagens = [conferir(f"{a.saida}/code.js", "code.js"),
                 conferir(f"{a.saida}/ui.html", "ui.html", r"<script>(.*?)</script>")]
    tamanhos = {f: os.path.getsize(f"{a.saida}/{f}") for f in sorted(os.listdir(a.saida))}
    print(json.dumps({"pasta": a.saida, "versao": versao, "telas": len(telas),
                      "arquivos": tamanhos, "conferencia": checagens},
                     indent=2, ensure_ascii=False))
    if any("NÃO COMPILA" in c for c in checagens):
        sys.exit(1)


if __name__ == "__main__":
    main()
