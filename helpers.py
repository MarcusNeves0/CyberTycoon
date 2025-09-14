# helpers.py

import pygame
import math


def formatar_numero(num):
    num = float(num)
    if num < 1000:
        return str(int(num))

    magnitude = int(math.log10(num) // 3)
    valor_exibido = num / (10 ** (magnitude * 3))
    sufixos_padrao = ['K', 'M', 'B', 'T', 'P', 'E', 'Z', 'Y']
    sufixo_final = ''
    indice_sufixo = magnitude - 1

    if indice_sufixo < len(sufixos_padrao):
        sufixo_final = sufixos_padrao[indice_sufixo]
    else:
        indice_letras = indice_sufixo - len(sufixos_padrao)
        primeira_letra = chr(ord('A') + (indice_letras // 26))
        segunda_letra = chr(ord('A') + (indice_letras % 26))
        sufixo_final = primeira_letra + segunda_letra

    return f"{valor_exibido:.2f}".rstrip('0').rstrip('.') + sufixo_final


def draw_text_wrapped(surface, text, font, color, rect):
    words = text.split(' ')
    lines = []
    current_line = ''

    for word in words:
        test_line = current_line + word + ' '
        if font.size(test_line)[0] < rect.width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + ' '
    lines.append(current_line)

    y = rect.y
    for line in lines:
        line_surface = font.render(line, True, color)
        surface.blit(line_surface, (rect.x, y))
        y += font.get_linesize()

    return y - rect.y