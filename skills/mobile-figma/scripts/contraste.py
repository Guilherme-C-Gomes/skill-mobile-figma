#!/usr/bin/env python3
"""
Calcula contraste WCAG entre cores. Estimativa a olho erra justamente
na faixa de 3:1 a 5:1, que e onde fica o limite de aprovacao.

Uso:
    python3 contraste.py "#667085" "#FFFFFF"
    python3 contraste.py --paleta tokens.json
    python3 contraste.py --paleta tokens.json --fundo bg

Com --paleta, testa toda cor do bloco "color" contra o fundo indicado
(padrao: a chave "bg", ou branco se ela nao existir).

    contraste.py "#D06CF5" --sobre "#FFFFFF@0.16" "#0A0A12"
        Texto sobre superficie translucida: o fundo real e a mistura das
        camadas, nao o token nominal. Calcular contra o token da aprovacao
        falsa. Camadas de cima para baixo.
"""

import json
import sys


def hex_para_rgb(valor):
    v = valor.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) == 8:  # #RRGGBBAA, ignora alfa
        v = v[:6]
    if len(v) != 6:
        raise ValueError(f"cor invalida: {valor}")
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


def luminancia(rgb):
    canais = []
    for c in rgb:
        c = c / 255
        canais.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = canais
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def razao(cor_a, cor_b):
    la, lb = luminancia(hex_para_rgb(cor_a)), luminancia(hex_para_rgb(cor_b))
    claro, escuro = max(la, lb), min(la, lb)
    return (claro + 0.05) / (escuro + 0.05)


def veredito(r):
    """Retorna (rotulo, aprova_texto_normal)."""
    if r >= 7:
        return "AAA texto normal", True
    if r >= 4.5:
        return "AA texto normal", True
    if r >= 3:
        return "AA texto grande e elemento de interface, REPROVA texto normal", False
    return "REPROVA em tudo", False


def par(a, b, rotulo=""):
    r = razao(a, b)
    nota, ok = veredito(r)
    marca = "ok  " if ok else "FALHA"
    prefixo = f"{rotulo:<16}" if rotulo else ""
    print(f"{marca} {prefixo}{a} sobre {b}  =  {r:.2f}:1   {nota}")
    return ok


def sobrepor(frente, alpha, fundo):
    """Cor resultante de `frente` com opacidade `alpha` sobre `fundo`."""
    f = hex_para_rgb(frente)
    b = hex_para_rgb(fundo)
    return "#" + "".join(f"{round(f[i] * alpha + b[i] * (1 - alpha)):02X}" for i in range(3))


def compor(camadas):
    """Empilha camadas de baixo para cima e devolve a cor final.

    Cada camada e "#RRGGBB" (opaca) ou "#RRGGBB@0.16" (com alpha). A ordem na
    linha de comando e de cima para baixo, como a pessoa ve, entao inverta:

        --sobre "#FFFFFF@0.16" "#0A0A12"
        = branco a 16% por cima de #0A0A12
    """
    cor = None
    for camada in reversed(camadas):
        if "@" in camada:
            base, a = camada.split("@")
            alpha = float(a)
        else:
            base, alpha = camada, 1.0
        cor = base if cor is None else sobrepor(base, alpha, cor)
    return cor


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)

    # texto sobre superficie translucida: o fundo real e a MISTURA, nao o token.
    # Calcular contra o token nominal da aprovacao falsa — foi assim que um icone
    # roxo sobre lente de vidro clara passou no papel e reprovou com 2.22:1.
    if "--sobre" in args:
        i = args.index("--sobre")
        frente, camadas = args[0], args[i + 1:]
        if not camadas:
            print('--sobre precisa das camadas, ex: --sobre "#FFFFFF@0.16" "#0A0A12"')
            sys.exit(2)
        fundo = compor(camadas)
        print("camadas: " + "  sobre  ".join(camadas) + f"   =  {fundo}")
        sys.exit(0 if par(frente, fundo) else 1)

    if args[0] == "--paleta":
        if len(args) < 2:
            print("informe o arquivo JSON de tokens")
            sys.exit(2)
        dados = json.load(open(args[1], encoding="utf-8"))
        cores = dados.get("color", dados)
        chave_fundo = args[3] if len(args) > 3 and args[2] == "--fundo" else "bg"
        fundo = cores.get(chave_fundo, "#FFFFFF")

        falhas = 0
        print(f"contraste sobre {chave_fundo} ({fundo})\n")
        for nome, valor in cores.items():
            if nome == chave_fundo or not isinstance(valor, str):
                continue
            if not par(valor, fundo, nome):
                falhas += 1
        print(f"\n{falhas} cor(es) reprovando para texto normal.")
        sys.exit(1 if falhas else 0)

    if len(args) < 2:
        print("informe duas cores, ex: contraste.py '#667085' '#FFFFFF'")
        sys.exit(2)

    sys.exit(0 if par(args[0], args[1]) else 1)


if __name__ == "__main__":
    main()
