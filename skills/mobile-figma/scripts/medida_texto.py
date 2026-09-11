#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Largura real de um texto, para dimensionar pilula, selo, botao e chip.

Toda reclamacao de "o nome esta vazando do botao" nasce de largura chutada.
A largura de um container que abraca texto tem de sair de medicao.

Uso na linha de comando:
    python3 medida_texto.py "Sincronizar agora" 16 600
    python3 medida_texto.py "Sincronizar agora" 16 600 --pad 40   # + padding

Uso dentro do gerador:
    from medida_texto import larg, larg_pilula
    w = larg_pilula("Baixa freq.", tamanho=14, peso=500, pad=26)

Por que uma fonte um pouco MAIS larga que a do design: medindo com DejaVu Sans
no lugar de Inter, o erro sempre sobra espaco em vez de faltar. Texto com folga
e invisivel; texto estourando a borda e a primeira coisa que a pessoa aponta.
"""
import os
import sys

# fontes candidatas, da mais parecida com Inter para a mais generica
_CANDIDATAS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "C:/Windows/Fonts/arial.ttf",
]
_NEGRITO = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]

# tabela de emergencia: largura media por caractere em fracao do tamanho da
# fonte, quando nao ha TTF disponivel. Menos precisa, mas melhor que chutar.
_LARGURA_MEDIA = 0.54
_ESTREITOS = set(" iljt.,:;'!|()[]{}/\\-")
_LARGOS = set("MWmw@%")


def _carregar(caminho, tamanho):
    from PIL import ImageFont
    return ImageFont.truetype(caminho, tamanho)


def larg(texto, tamanho=16, peso=400):
    """Largura em px de `texto` renderizado em `tamanho` px com `peso`."""
    if not texto:
        return 0.0
    lista = (_NEGRITO + _CANDIDATAS) if peso >= 600 else _CANDIDATAS
    for caminho in lista:
        if not os.path.exists(caminho):
            continue
        try:
            fonte = _carregar(caminho, int(round(tamanho)))
            w = fonte.getlength(texto)
            # peso medio pesa um pouco mais que o regular
            if 500 <= peso < 600:
                w *= 1.02
            return round(float(w), 1)
        except Exception:
            continue
    return round(_estimar(texto, tamanho, peso), 1)


def _estimar(texto, tamanho, peso):
    total = 0.0
    for ch in texto:
        if ch in _ESTREITOS:
            total += 0.30
        elif ch in _LARGOS:
            total += 0.86
        elif ch.isupper():
            total += 0.66
        else:
            total += _LARGURA_MEDIA
    if peso >= 600:
        total *= 1.05
    elif peso >= 500:
        total *= 1.02
    return total * tamanho


def larg_pilula(texto, tamanho=14, peso=500, pad=26):
    """Largura de uma pilula/chip que abraca o texto, arredondada para inteiro."""
    return int(round(larg(texto, tamanho, peso) + pad))


def larg_selo(texto, tamanho=12, peso=600, pad=24, icone=False):
    """Largura de um selo. `icone` reserva 22px para o simbolo a esquerda."""
    return int(round(larg(texto, tamanho, peso) + pad + (22 if icone else 0)))


def cabe(texto, largura_disponivel, tamanho=16, peso=400, folga=8):
    """True se o texto cabe com folga. Use antes de fixar largura de container."""
    return larg(texto, tamanho, peso) + folga <= largura_disponivel


def distribuir_por_vao(rotulos, largura_total, tamanho=12, peso=500):
    """Centros de uma fila em que os VAOS ficam iguais, nao os centros.

    Quando os rotulos tem larguras muito diferentes ("Inicio" 30px,
    "Participantes" 76px), dividir em fatias iguais deixa os centros certos e
    os vaos tortos, e o olho le torto. Devolve (centros, larguras, vao).
    """
    larguras = [larg(r, tamanho, peso) for r in rotulos]
    vao = (largura_total - sum(larguras)) / (len(rotulos) + 1)
    centros, x = [], vao
    for w in larguras:
        centros.append(round(x + w / 2, 1))
        x += w + vao
    return centros, [round(w, 1) for w in larguras], round(vao, 1)


def main():
    args = [a for a in sys.argv[1:]]
    pad = 0
    if "--pad" in args:
        i = args.index("--pad")
        pad = float(args[i + 1])
        args = args[:i] + args[i + 2:]
    if not args:
        print(__doc__)
        sys.exit(2)
    texto = args[0]
    tamanho = float(args[1]) if len(args) > 1 else 16
    peso = int(args[2]) if len(args) > 2 else 400
    w = larg(texto, tamanho, peso)
    print(f'"{texto}"  {tamanho:g}px peso {peso}')
    print(f"  largura do texto     {w:g}px")
    if pad:
        print(f"  com padding {pad:g}      {w + pad:g}px  (container: {int(round(w + pad))})")


if __name__ == "__main__":
    main()
