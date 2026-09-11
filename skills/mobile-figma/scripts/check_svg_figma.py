#!/usr/bin/env python3
"""
Valida arquivos SVG antes de importar no Figma.

Checa quatro coisas que so aparecem depois que a pessoa ja importou:
estrutura de camadas, contraste WCAG, alvo de toque e escala de espacamento.

Uso:
    python3 check_svg_figma.py telas/*.svg
    python3 check_svg_figma.py telas/
    python3 check_svg_figma.py telas/ --escala 8     # base de espacamento (padrao 4)

Saida: lista de ERRO (corrigir antes de entregar) e AVISO (usar julgamento).
Codigo de saida 1 se houver qualquer ERRO.
"""

import re
import sys
import glob
import os
import xml.etree.ElementTree as ET

NS = "{http://www.w3.org/2000/svg}"

ALVO_TOQUE_MIN = 44          # pt, WCAG 2.5.5 / diretrizes iOS e Android

# Limites da barra inferior em 390x844 com barra flutuante a partir de y=752.
# Entre 706 e 752 o veu ja apaga o texto; depois de 748 o elemento fica atras
# da barra e le como cortado, nao como conteudo rolando.
LIMITE_TEXTO = 706
LIMITE_CAIXA = 748
PALAVRAS_INTERATIVAS = (
    "botao", "button", "btn", "cta", "acao", "action", "tab", "chip",
    "toggle", "switch", "checkbox", "radio", "link", "menu_item", "nav_item",
    "icone_acao", "icon_button", "fab", "close", "fechar",
)

FONTES_SEGURAS = {
    "inter", "dm sans", "instrument sans", "roboto", "open sans", "lato",
    "montserrat", "poppins", "source sans pro", "source serif pro",
    "noto sans", "work sans", "nunito", "raleway", "ibm plex sans",
    "space grotesk", "manrope", "figtree", "outfit", "plus jakarta sans",
    "calibri", "arial", "helvetica", "sf pro", "roboto mono", "jetbrains mono",
}

# elementos que costumam sobreviver bem a importacao
SHAPES = {"rect", "circle", "ellipse", "line", "polyline", "polygon", "path", "text"}


def local(tag):
    return tag.split("}")[-1] if "}" in tag else tag


# --------------------------------------------------------------------------
# contraste WCAG
# --------------------------------------------------------------------------

def hex_para_rgb(valor):
    v = valor.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) == 8:
        v = v[:6]
    if len(v) != 6 or re.search(r"[^0-9a-fA-F]", v):
        return None
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


def luminancia(rgb):
    canais = []
    for c in rgb:
        c = c / 255
        canais.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * canais[0] + 0.7152 * canais[1] + 0.0722 * canais[2]


def razao_contraste(a, b):
    ra, rb = hex_para_rgb(a), hex_para_rgb(b)
    if not ra or not rb:
        return None
    la, lb = luminancia(ra), luminancia(rb)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def minimo_exigido(tamanho, peso):
    """Texto grande e 18pt normal ou 14pt bold. Em px, ~24 e ~18.66."""
    try:
        p = int(re.sub(r"[^\d]", "", str(peso))) if peso else 400
    except ValueError:
        p = 700 if str(peso).lower() in ("bold", "bolder") else 400
    grande = tamanho >= 24 or (tamanho >= 18.66 and p >= 700)
    return 3.0 if grande else 4.5


def num(valor):
    try:
        return float(re.sub(r"[^\d.\-]", "", str(valor)))
    except (ValueError, TypeError):
        return None


def coletar_fundos(raiz):
    """Retorna [(x, y, w, h, cor)] em ordem de pintura, so de <rect> com fill solido."""
    fundos = []
    for elem in raiz.iter():
        if local(elem.tag) != "rect":
            continue
        cor = (elem.get("fill") or "").strip()
        if not cor.startswith("#"):
            continue
        x, y = num(elem.get("x", 0)), num(elem.get("y", 0))
        w, h = num(elem.get("width")), num(elem.get("height"))
        if None in (x, y, w, h):
            continue
        op = num(elem.get("fill-opacity") or elem.get("opacity") or 1)
        if op is not None and op < 0.95:
            continue  # translucido, o fundo real nao da para deduzir
        fundos.append((x, y, w, h, cor))
    return fundos


def fundo_sob(fundos, px, py):
    """Ultimo retangulo pintado que cobre o ponto: aproximacao do algoritmo do pintor."""
    achado = None
    for x, y, w, h, cor in fundos:
        if x <= px <= x + w and y <= py <= y + h:
            achado = cor
    return achado


def checar(caminho, base_escala=4, mobile=False):
    erros, avisos = [], []
    try:
        bruto = open(caminho, "r", encoding="utf-8").read()
    except Exception as e:
        return [f"nao foi possivel ler o arquivo: {e}"], []

    try:
        raiz = ET.fromstring(bruto)
    except ET.ParseError as e:
        return [f"XML invalido: {e}"], []

    # --- raiz -------------------------------------------------------------
    if local(raiz.tag) != "svg":
        erros.append("o elemento raiz nao e <svg>")

    if not raiz.get("viewBox"):
        erros.append("falta viewBox no <svg> raiz, o Figma pode importar em escala errada")

    if not (raiz.get("width") and raiz.get("height")):
        avisos.append("sem width/height explicitos no <svg> raiz")

    # --- var() css --------------------------------------------------------
    if "var(" in bruto:
        n = bruto.count("var(")
        erros.append(
            f"{n} uso(s) de var() em cor ou tamanho, "
            "o Figma nao resolve variaveis CSS, troque por valor literal"
        )

    # --- elementos que quebram -------------------------------------------
    quebra = {
        "foreignObject": "ignorado pelo Figma na importacao",
        "use": "referencia a simbolo costuma se perder",
        "filter": "filtros complexos somem ou rasterizam",
        "animate": "animacao SMIL nao e suportada",
        "animateTransform": "animacao SMIL nao e suportada",
        "script": "nao deve existir em arquivo de tela",
    }
    for elem in raiz.iter():
        nome = local(elem.tag)
        if nome in quebra:
            erros.append(f"<{nome}> encontrado: {quebra[nome]}")

    if raiz.find(f".//{NS}style") is not None or "<style" in bruto:
        avisos.append(
            "bloco <style> presente, prefira atributos inline "
            "porque seletores CSS nao aplicam de forma confiavel na importacao"
        )

    # --- texto ------------------------------------------------------------
    textos = list(raiz.iter(f"{NS}text"))
    if not textos:
        avisos.append("nenhum elemento <text>, verifique se o texto virou path (perde a edicao)")

    for t in textos:
        conteudo = "".join(t.itertext()).strip()
        if not t.get("font-family"):
            erros.append(f'<text> sem font-family: "{conteudo[:40]}"')
        else:
            familia = t.get("font-family").split(",")[0].strip().strip("'\"").lower()
            if familia not in FONTES_SEGURAS:
                avisos.append(
                    f'fonte "{t.get("font-family")}" pode nao existir no Figma da pessoa, '
                    "o layout desloca se for substituida"
                )
        if not t.get("font-size"):
            erros.append(f'<text> sem font-size: "{conteudo[:40]}"')
        else:
            try:
                tam = float(re.sub(r"[^\d.]", "", t.get("font-size")))
                if tam < 12:
                    avisos.append(f'texto com {tam:g}px, abaixo do minimo legivel: "{conteudo[:30]}"')
            except ValueError:
                pass
        if conteudo.lower().startswith("lorem ipsum"):
            avisos.append("placeholder lorem ipsum na tela, use conteudo realista antes de aprovar")

    # --- grupos sem nome --------------------------------------------------
    grupos = list(raiz.iter(f"{NS}g"))
    sem_id = [g for g in grupos if not g.get("id")]
    # <g transform> com um filho so e tecnica legitima de escala/posicao, nao
    # camada de conteudo. O que estraga o arquivo e grupo de conteudo anonimo.
    anonimos = [g for g in sem_id if len(list(g)) > 1 or g.find(f"{NS}text") is not None]
    envoltorios = [g for g in sem_id if g not in anonimos]
    if anonimos:
        erros.append(
            f"{len(anonimos)} de {len(grupos)} grupo(s) <g> de conteudo sem id, "
            "viram 'Group 1' no Figma e o arquivo fica impossivel de manter"
        )
    if envoltorios:
        avisos.append(
            f"{len(envoltorios)} grupo(s) <g> sem id servindo so de envoltorio de "
            "transform: ok, mas nomeie se a camada tiver de casar no Smart Animate"
        )

    for g in grupos:
        gid = g.get("id")
        if gid and (" " in gid or re.search(r"[áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ]", gid)):
            avisos.append(f'id "{gid}" tem espaco ou acento, prefira underscore e ASCII')

    # --- fundo do frame ---------------------------------------------------
    filhos = [c for c in raiz if local(c.tag) not in ("defs", "title", "desc", "metadata")]
    if filhos:
        primeiro = filhos[0]
        if local(primeiro.tag) != "rect":
            avisos.append(
                "o primeiro elemento nao e um <rect> de fundo, "
                "o frame fica sem limite claro no Figma"
            )

    # --- conteudo fora do viewBox ----------------------------------------
    vb = raiz.get("viewBox")
    if vb:
        try:
            _, _, vw, vh = [float(v) for v in re.split(r"[ ,]+", vb.strip())]
            for elem in raiz.iter():
                if local(elem.tag) not in SHAPES:
                    continue
                x, y = elem.get("x"), elem.get("y")
                w, h = elem.get("width"), elem.get("height")
                if x and w:
                    try:
                        if float(x) + float(w) > vw + 1:
                            avisos.append(
                                f"<{local(elem.tag)}> ultrapassa a largura do viewBox "
                                f"({float(x) + float(w):g} > {vw:g})"
                            )
                    except ValueError:
                        pass
                if y and h:
                    try:
                        if float(y) + float(h) > vh + 1:
                            avisos.append(
                                f"<{local(elem.tag)}> ultrapassa a altura do viewBox "
                                f"({float(y) + float(h):g} > {vh:g})"
                            )
                    except ValueError:
                        pass
        except (ValueError, TypeError):
            pass

    # --- contraste WCAG ---------------------------------------------------
    # Pular a checagem inteira so porque existe um transform no arquivo e
    # jogar fora a checagem mais importante: telas geradas quase sempre tem um
    # <g transform> na marca. Aqui so os nos DENTRO de um ancestral
    # transformado sao pulados, porque so as coordenadas deles se deslocam.
    deslocados = set()
    for pai in raiz.iter():
        if pai.get("transform"):
            for filho in pai.iter():
                deslocados.add(id(filho))
    fundos = coletar_fundos(raiz)
    tem_transform = bool(deslocados)
    if deslocados:
        avisos.append(
            f"{len(deslocados)} no(s) dentro de um transform: contraste e alvo de "
            "toque foram checados so nos demais, porque as coordenadas se deslocam"
        )
    if fundos:
        for t in textos:
            if id(t) in deslocados:
                continue
            cor = (t.get("fill") or "").strip()
            tx, ty = num(t.get("x")), num(t.get("y"))
            if not cor.startswith("#") or tx is None or ty is None:
                continue
            tam = num(t.get("font-size")) or 16
            # y do <text> e a linha de base; sobe ~30% da altura para pegar o miolo
            fundo = fundo_sob(fundos, tx, ty - tam * 0.3)
            if not fundo:
                continue
            r = razao_contraste(cor, fundo)
            if r is None:
                continue
            minimo = minimo_exigido(tam, t.get("font-weight"))
            if r < minimo:
                conteudo = "".join(t.itertext()).strip()[:30]
                erros.append(
                    f'contraste {r:.2f}:1 reprova (minimo {minimo}:1) em "{conteudo}", '
                    f"texto {cor} sobre {fundo}"
                )

    # --- alvo de toque ----------------------------------------------------
    if True:
        for elem in raiz.iter():
            if local(elem.tag) not in ("rect", "g") or id(elem) in deslocados:
                continue
            ident = (elem.get("id") or "").lower()
            if not any(p in ident for p in PALAVRAS_INTERATIVAS):
                continue
            if local(elem.tag) == "rect":
                w, h = num(elem.get("width")), num(elem.get("height"))
            else:
                filhos_rect = [c for c in elem.iter() if local(c.tag) == "rect"]
                if not filhos_rect:
                    continue
                w = max((num(c.get("width")) or 0) for c in filhos_rect)
                h = max((num(c.get("height")) or 0) for c in filhos_rect)
            if not w or not h:
                continue
            if h < ALVO_TOQUE_MIN or w < ALVO_TOQUE_MIN:
                avisos.append(
                    f'"{elem.get("id")}" mede {w:g}x{h:g}, abaixo do alvo de toque '
                    f"de {ALVO_TOQUE_MIN}x{ALVO_TOQUE_MIN} (ok se for desktop com espacamento)"
                )

    # --- escala de espacamento -------------------------------------------
    # Checa so o que e decisao de espacamento: posicao, altura e raio.
    # Largura costuma ser derivada das margens (390 - 2*16 = 358) e nao e erro.
    fora_escala = set()
    for elem in raiz.iter():
        if local(elem.tag) not in SHAPES:
            continue
        # texto centralizado tem x no meio do container, nao e decisao de escala
        centralizado = elem.get("text-anchor") in ("middle", "end")
        eh_texto = local(elem.tag) == "text"
        for atrib in ("x", "y", "height", "rx"):
            if centralizado and atrib == "x":
                continue
            # y de <text> e linha de base, calculada a partir do centro optico
            if eh_texto and atrib == "y":
                continue
            v = num(elem.get(atrib))
            if v is None or v == 0:
                continue
            if abs(v - round(v)) > 0.01 or int(v) % base_escala != 0:
                fora_escala.add(f"{elem.get('id') or local(elem.tag)} {atrib}={v:g}")
    if fora_escala:
        amostra = "; ".join(sorted(fora_escala)[:5])
        avisos.append(
            f"{len(fora_escala)} valor(es) fora da escala de {base_escala}px "
            f"({amostra}). Valor avulso e o que faz a tela parecer costurada"
        )

    # --- matriz degenerada -----------------------------------------------
    # Arredondamento agressivo em minificacao transforma -0.0130 em -0, e uma
    # matriz com determinante zero deixa o elemento invisivel no Figma e faz
    # qualquer animacao nele falhar com "transform is not invertible".
    for m in re.finditer(r'matrix\(\s*([-\d.eE]+)[ ,]+([-\d.eE]+)[ ,]+([-\d.eE]+)[ ,]+([-\d.eE]+)',
                         bruto):
        try:
            a, b, c, d = (float(m.group(i)) for i in range(1, 5))
        except ValueError:
            continue
        if abs(a * d - b * c) < 1e-9:
            erros.append(
                f"matrix({m.group(1)} {m.group(2)} {m.group(3)} {m.group(4)} ...) tem "
                "determinante zero: o elemento fica invisivel no Figma. "
                "Provavel arredondamento agressivo na minificacao"
            )

    # --- series repetidas descentralizadas --------------------------------
    # Tres ou mais elementos de mesma largura em fila precisam de margens
    # iguais dentro do container. Um deslocamento de poucos pixels e o
    # suficiente para a pessoa dizer "esta descentralizado".
    por_largura = {}
    for elem in raiz.iter():
        if local(elem.tag) != "rect":
            continue
        x, w = num(elem.get("x")), num(elem.get("width"))
        y, h = num(elem.get("y")), num(elem.get("height"))
        if None in (x, w, y, h) or w <= 0:
            continue
        chave = (round(w, 1), round(y, 1), round(h, 1))
        por_largura.setdefault(chave, []).append((x, elem.get("id") or "rect"))
    for (w, y, _h), itens in por_largura.items():
        if len(itens) < 3:
            continue
        xs = sorted(p[0] for p in itens)
        passos = [round(xs[i + 1] - xs[i], 1) for i in range(len(xs) - 1)]
        if max(passos) - min(passos) > 1.0:
            avisos.append(
                f"serie de {len(itens)} elementos de largura {w:g} em y={y:g} tem "
                f"passos desiguais {passos}: distribua pelo vao, nao por divisao simples"
            )

    # --- barra inferior (mobile) ------------------------------------------
    if mobile:
        IGNORAR_BARRA = re.compile(
            r"^(Scrim|Nav_|Frame_|Fundo|Hero_Fundo|Hero_Brilho|Brilho|Progresso"
            r"|Rodape|Marca|Reflexo|\w*_Reflexo)"
        )
        for elem in raiz.iter():
            ident = elem.get("id") or ""
            if IGNORAR_BARRA.match(ident):
                continue
            if local(elem.tag) in ("rect", "circle", "g"):
                y, h = num(elem.get("y")), num(elem.get("height"))
                if y is not None and h is not None and y + h > LIMITE_CAIXA:
                    erros.append(
                        f'"{ident or local(elem.tag)}" termina em {y + h:g}, atras da barra '
                        f"(limite {LIMITE_CAIXA}). Le como elemento cortado, nao como rolagem"
                    )
            if local(elem.tag) == "text":
                y = num(elem.get("y"))
                if y is not None and y > LIMITE_TEXTO:
                    erros.append(
                        f'texto "{ident or "".join(elem.itertext())[:24]}" com linha de base em '
                        f"{y:g}, abaixo de {LIMITE_TEXTO}: o veu da barra ja apaga"
                    )

    # --- distribuicao da barra de abas (mobile) ---------------------------
    if mobile:
        alvos = [(num(e.get("x")), num(e.get("width")))
                 for e in raiz.iter()
                 if local(e.tag) == "rect" and re.match(r"^Nav_\w+_Alvo$", e.get("id") or "")]
        alvos = [a for a in alvos if None not in a]
        if len(alvos) >= 3:
            centros = sorted(x + w / 2 for x, w in alvos)
            passos = [round(centros[i + 1] - centros[i], 1) for i in range(len(centros) - 1)]
            if max(passos) - min(passos) > 1.0:
                avisos.append(
                    f"abas com centros desiguais {passos}: com rotulos de larguras "
                    "diferentes, distribua pelo vao entre os rotulos, nao por fatias iguais"
                )
            if passos:
                excesso = round(max(w for _x, w in alvos) - min(passos), 1)
                if excesso > 1.0:
                    avisos.append(
                        f"alvos de toque se sobrepoem em {excesso:g}px: o toque na "
                        "borda cai na aba errada"
                    )

    # --- estados da tela --------------------------------------------------
    nome = os.path.basename(caminho).lower()
    if any(p in nome for p in ("lista", "list", "home", "feed", "dashboard", "pedidos")):
        texto_todo = " ".join("".join(t.itertext()) for t in textos).lower()
        if not any(p in texto_todo for p in ("nenhum", "vazio", "ainda nao", "comece", "sem ")):
            avisos.append(
                "tela de lista sem sinal de estado vazio no conjunto entregue, "
                "confirme que existe um arquivo para o estado vazio"
            )

    # dedup preservando ordem
    return list(dict.fromkeys(erros)), list(dict.fromkeys(avisos))


def coletar(args):
    arquivos = []
    for a in args:
        if os.path.isdir(a):
            arquivos += sorted(glob.glob(os.path.join(a, "**", "*.svg"), recursive=True))
        else:
            arquivos += sorted(glob.glob(a))
    return arquivos


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)

    mobile = "--mobile" in args
    if mobile:
        args = [a for a in args if a != "--mobile"]

    base_escala = 4
    if "--escala" in args:
        i = args.index("--escala")
        try:
            base_escala = int(args[i + 1])
        except (IndexError, ValueError):
            print("--escala precisa de um numero, ex: --escala 8")
            sys.exit(2)
        args = args[:i] + args[i + 2:]

    arquivos = coletar(args)
    if not arquivos:
        print("nenhum arquivo .svg encontrado")
        sys.exit(2)

    total_erros = 0
    for caminho in arquivos:
        erros, avisos = checar(caminho, base_escala, mobile)
        total_erros += len(erros)
        marca = "FALHOU" if erros else ("ok, com avisos" if avisos else "ok")
        print(f"\n{os.path.basename(caminho)}  [{marca}]")
        for e in erros:
            print(f"  ERRO   {e}")
        for a in avisos:
            print(f"  AVISO  {a}")

    print(f"\n{len(arquivos)} arquivo(s) verificado(s), {total_erros} erro(s).")
    sys.exit(1 if total_erros else 0)


if __name__ == "__main__":
    main()
