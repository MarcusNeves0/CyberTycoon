# main.py

import pygame
import os
import random

from settings import *
from helpers import *
from game_objects import Implante, BonusChip
from upgrades import UpgradesPopup
from contacts import Contato, ContatosPopup

# --- Bloco Principal do Jogo ---
pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Cyberpunk Tycoon")

# --- Fontes ---
try:
    caminho_fonte_rajdhani = os.path.join('Fonts', 'Rajdhani-Bold.ttf')
    fonte_dinheiro = pygame.font.Font(caminho_fonte_rajdhani, 42)
except FileNotFoundError:
    print(f"Aviso: Fonte 'Rajdhani-Bold.ttf' não encontrada. Usando fonte padrão.")
    fonte_dinheiro = pygame.font.SysFont('Consolas', 40, bold=True)


try:
    caminho_fonte_cyberpunk = os.path.join('Fonts', 'Rajdhani.ttf')
    fonte_nome_implante = pygame.font.Font(caminho_fonte_cyberpunk, 20) # Tamanho para os nomes
    fonte_item_implante = pygame.font.Font(caminho_fonte_cyberpunk, 18) # Tamanho para os detalhes
except FileNotFoundError:
    print(f"Aviso: Fonte 'CyberwayRiders.ttf' não encontrada. Usando fonte padrão.")
    fonte_nome_implante = pygame.font.SysFont('Consolas', 18, bold=True)
    fonte_item_implante = pygame.font.SysFont('Consolas', 16)


fonte_botoes = pygame.font.SysFont('Consolas', 20, bold=True)



try:
    background_imagem = pygame.image.load('Background.png').convert()
    background_imagem = pygame.transform.scale(background_imagem, (LARGURA, ALTURA))
except pygame.error:
    background_imagem = None


dinheiro: float = 0.0
modo_compra = '1x'

popup_upgrades = UpgradesPopup()
lista_contatos_obj = [
    Contato("Jackie Welles", 1e12, "A cada 60 segundos, te dá um nível grátis em um implante aleatório.", "Jackie.png"),
    Contato("Goro Takemura", 1e12, "Envia um chip da Arasaka para a tela em tempos aleatórios. Clique para ganhar 3% dos seus Edinhos totais.", "Takemura.png"),
    Contato("Johnny Silverhand", 100e12, "Desbloqueia o implante 'Relic'.", "Johnny.png"),
    Contato("Rogue Amendiares", 100e15, "Desbloqueia o implante 'Pride'.", "Rogue.png"),
    Contato("Panam Palmer", 100e18, "Desbloqueia o implante 'Thorton Mackinaw'.", "Panam.png")
]
popup_contatos = ContatosPopup(lista_contatos_obj)


jackie_timer = 0.0
takemura_timer = 0.0
tempo_proximo_chip = random.randint(60, 180)
chip_ativo = None


PAINEL_ESQUERDO_X = 20
rect_quadro_preto = pygame.Rect(PAINEL_ESQUERDO_X - 10, 70, 270, 55)
rect_area_scroll_principal = pygame.Rect(PAINEL_ESQUERDO_X, rect_quadro_preto.bottom + 5, 260, ALTURA - rect_quadro_preto.bottom - 25)
surface_principal = pygame.Surface(rect_area_scroll_principal.size, pygame.SRCALPHA)
scroll_offset_principal = 0

PAINEL_DIREITO_X = PAINEL_ESQUERDO_X + rect_area_scroll_principal.width + 20
rect_area_scroll_contato = pygame.Rect(PAINEL_DIREITO_X, rect_area_scroll_principal.y, 260, rect_area_scroll_principal.height)
surface_contato = pygame.Surface(rect_area_scroll_contato.size, pygame.SRCALPHA)
scroll_offset_contato = 0
painel_contato_visivel = False

botoes_texto = ['1x', '5x', '10x', '50x', 'MAX']
botoes_modo_compra = {}
for i, texto in enumerate(botoes_texto):
    botoes_modo_compra[texto] = pygame.Rect(rect_quadro_preto.x + 5 + i * 52, rect_quadro_preto.y + 10, 50, 35)

try:
    TAMANHO_BOTAO_JACKIE = (100, 80)
    imagem_botao_jackie = pygame.image.load("Jackie.png").convert_alpha()
    imagem_botao_jackie = pygame.transform.scale(imagem_botao_jackie, TAMANHO_BOTAO_JACKIE)
    rect_botao_jackie = imagem_botao_jackie.get_rect(bottomright=(LARGURA - 20, ALTURA - 20))
except pygame.error as e:
    print(f"Erro ao carregar imagem do botão Jackie: {e}")
    imagem_botao_jackie = None
    rect_botao_jackie = pygame.Rect(LARGURA - 200, ALTURA - 60, 180, 40)

# --- Lista de Implantes ---
lista_implantes_principais = [
    Implante(5, 10, "Memory Boost", 0, 1, image_path="MemoryBoost.png"),
    Implante(5, 160, "Kiroshi Optics", 100, 15, image_path="Kiroshi.png"),
    Implante(5, 310, "RAM Upgrader", 500, 75, image_path="RamUpgrade.png"),
    Implante(5, 460, "Biomonitor", 1000, 150, image_path="Biomonitor.png"),
    Implante(5, 610, "AdrenalineBooster", 50000, 2500, image_path="AdrenalineBooster.png"),
    Implante(5, 760, "Zetatech Sandevistan", 250000, 15000, image_path="ZetatechSandevistan.png"),
    Implante(5, 910, "Gorilla Arms", 500000, 45000, image_path="GorillaArms.png"),
    Implante(5, 1060, "Atomic Sensors", 1000000, 70000, image_path="AtomicSensors.png"),
    Implante(5, 1210, "Tattoo: Together Forever", 100e6, 8.5e6, image_path="TogetherForever.png"),
    Implante(5, 1360, "Malorian Arms 3516", 1e9, 45e6, image_path="Malorian.png"),
    Implante(5, 1510, "Zetatech Berserk", 10e9, 300e6, image_path="ZetatechBerserk.png"),
    Implante(5, 1660, "Monowire", 100e9, 2e9, image_path="Monowire.png"),
    Implante(5, 1810, "Scar Coalescer", 1e12, 9e9, image_path="ScarCoalescer.png"),
    Implante(5, 1960, "Jenkins Tendons", 100e12, 14e9, image_path="JenkinsTendons.png"),
    Implante(5, 2110, "The Oracle Optics", 500e12, 10e12, image_path="TheOracle.png"),
    Implante(5, 2260, "Mantis Blades", 1e15, 150e12, image_path="MantisBlade.png"),
]
lista_implantes_contato = [
    Implante(5, 10, "Relic", 10e12, 100e6, image_path="relic.png", bloqueado=True),
    Implante(5, 160, "Pride", 10e15, 1e12, image_path="pride.png", bloqueado=True),
    Implante(5, 310, "Thorton Mackinaw", 10e18, 1e15, image_path="ThortonMackinaw.jpg", bloqueado=True),
]
lista_implantes_completa = lista_implantes_principais + lista_implantes_contato

clock = pygame.time.Clock()
rodando = True
while rodando:
    dt = clock.tick(60) / 1000.0
    dinheiro_por_segundo = sum(implante.renda_total for implante in lista_implantes_completa if not implante.bloqueado)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False
        
        if chip_ativo and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if chip_ativo.rect.collidepoint(event.pos):
                recompensa = dinheiro * 0.03; dinheiro += recompensa; chip_ativo = None; continue

        if popup_upgrades.visivel:
            objeto_comprado = popup_upgrades.handle_event(event, dinheiro, lista_implantes_completa)
            if objeto_comprado:
                dinheiro -= objeto_comprado.custo
        elif popup_contatos.visivel:
            contato_comprado = popup_contatos.handle_event(event, dinheiro)
            if contato_comprado:
                dinheiro -= contato_comprado.custo
                painel_contato_visivel = True
                if contato_comprado.nome == "Johnny Silverhand":
                    lista_implantes_contato[0].bloqueado = False
                elif contato_comprado.nome == "Rogue Amendiares":
                    lista_implantes_contato[1].bloqueado = False
                elif contato_comprado.nome == "Panam Palmer":
                    lista_implantes_contato[2].bloqueado = False
        else:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rect_botao_jackie.collidepoint(event.pos):
                    popup_contatos.abrir()
                for texto, rect in botoes_modo_compra.items():
                    if rect.collidepoint(event.pos):
                        modo_compra = texto
                
                if rect_area_scroll_principal.collidepoint(event.pos):
                    mouse_pos_relativa = (event.pos[0] - rect_area_scroll_principal.x, event.pos[1] - rect_area_scroll_principal.y)
                    for implante in lista_implantes_principais:
                        rect_no_scroll = implante.rect_principal.move(0, scroll_offset_principal)
                        if rect_no_scroll.collidepoint(mouse_pos_relativa):
                            click_no_card_x = mouse_pos_relativa[0] - rect_no_scroll.x
                            click_no_card_y = mouse_pos_relativa[1] - rect_no_scroll.y
                            if implante.upgrades_unicos and implante.rect_botao_upgrades.collidepoint((click_no_card_x, click_no_card_y)):
                                popup_upgrades.abrir(implante)
                            else:
                                custo, bonus = implante.comprar(dinheiro, modo_compra, lista_implantes_completa)
                                if custo > 0:
                                    dinheiro -= custo
                                    dinheiro += bonus
                
                if painel_contato_visivel and rect_area_scroll_contato.collidepoint(event.pos):
                    mouse_pos_relativa = (event.pos[0] - rect_area_scroll_contato.x, event.pos[1] - rect_area_scroll_contato.y)
                    for implante in lista_implantes_contato:
                        if not implante.bloqueado:
                            rect_no_scroll = implante.rect_principal.move(0, scroll_offset_contato)
                            if rect_no_scroll.collidepoint(mouse_pos_relativa):
                                custo, bonus = implante.comprar(dinheiro, modo_compra, lista_implantes_completa)
                                if custo > 0:
                                    dinheiro -= custo
                                    dinheiro += bonus

            if event.type == pygame.MOUSEWHEEL:
                mouse_pos = pygame.mouse.get_pos()
                if rect_area_scroll_principal.collidepoint(mouse_pos):
                    scroll_offset_principal += event.y * 30
                    scroll_offset_principal = min(scroll_offset_principal, 0)
                    altura_total_conteudo = lista_implantes_principais[-1].rect_principal.bottom if lista_implantes_principais else 0
                    if altura_total_conteudo > rect_area_scroll_principal.height:
                        limite_scroll = rect_area_scroll_principal.height - altura_total_conteudo - 10
                        scroll_offset_principal = max(scroll_offset_principal, limite_scroll)
                    else:
                        scroll_offset_principal = 0
                elif painel_contato_visivel and rect_area_scroll_contato.collidepoint(mouse_pos):
                    scroll_offset_contato += event.y * 30
                    scroll_offset_contato = min(scroll_offset_contato, 0)
                    altura_total_conteudo = lista_implantes_contato[-1].rect_principal.bottom if lista_implantes_contato else 0
                    if altura_total_conteudo > rect_area_scroll_contato.height:
                        limite_scroll = rect_area_scroll_contato.height - altura_total_conteudo - 10
                        scroll_offset_contato = max(scroll_offset_contato, limite_scroll)
                    else:
                        scroll_offset_contato = 0

    dinheiro += dinheiro_por_segundo * dt
    
    contato_jackie = lista_contatos_obj[0]
    if contato_jackie.comprado:
        jackie_timer += dt
        if jackie_timer >= 60:
            jackie_timer = 0
            implantes_visiveis = [imp for imp in lista_implantes_principais if not imp.bloqueado]
            if implantes_visiveis:
                implante_sorteado = random.choice(implantes_visiveis)
                implante_sorteado.quantidade += 1
                implante_sorteado._recalculate_total_income()
                implante_sorteado._update_custo_proximo_nivel(lista_implantes_completa)

    contato_takemura = lista_contatos_obj[1]
    if contato_takemura.comprado and not chip_ativo:
        takemura_timer += dt
        if takemura_timer >= tempo_proximo_chip:
            takemura_timer = 0
            chip_ativo = BonusChip()
            tempo_proximo_chip = random.randint(60, 180)
    
    if chip_ativo and not chip_ativo.update(dt):
        chip_ativo = None

    if background_imagem:
        tela.blit(background_imagem, (0, 0))
    else:
        tela.fill(FUNDO_ESCURO)
    
    rect_display_dinheiro = pygame.Rect(LARGURA - 420, 20, 400, 60)
    surface_dinheiro = pygame.Surface(rect_display_dinheiro.size, pygame.SRCALPHA)
    pygame.draw.rect(surface_dinheiro, (30, 30, 30, 200), surface_dinheiro.get_rect(), border_radius=5)
    texto_dinheiro = fonte_dinheiro.render(f"Edinhos: {formatar_numero(dinheiro)}", True, CIANO_NEON)
    surface_dinheiro.blit(texto_dinheiro, (15, 10))
    tela.blit(surface_dinheiro, rect_display_dinheiro.topleft)
    
    surface_principal.fill((0, 0, 0, 0))
    for implante in lista_implantes_principais:
        implante.draw(surface_principal, fonte_nome_implante, fonte_item_implante, scroll_offset_principal, dinheiro, modo_compra, lista_implantes_completa)
    pygame.draw.rect(tela, PRETO, rect_quadro_preto, border_radius=5)
    tela.blit(surface_principal, rect_area_scroll_principal.topleft)
    for texto, rect in botoes_modo_compra.items():
        cor = CIANO_NEON if modo_compra == texto else CINZA_BOTAO
        pygame.draw.rect(tela, cor, rect, border_radius=5)
        texto_surface = fonte_botoes.render(texto, True, PRETO)
        tela.blit(texto_surface, (rect.centerx - texto_surface.get_width() // 2, rect.centery - texto_surface.get_height() // 2))

    if painel_contato_visivel:
        surface_contato.fill((0,0,0,0))
        for implante in lista_implantes_contato:
            implante.draw(surface_contato, fonte_nome_implante, fonte_item_implante, scroll_offset_contato, dinheiro, modo_compra, lista_implantes_completa)
        tela.blit(surface_contato, rect_area_scroll_contato.topleft)

    if imagem_botao_jackie:
        tela.blit(imagem_botao_jackie, rect_botao_jackie)
    else:
        pygame.draw.rect(tela, CINZA_BOTAO, rect_botao_jackie, border_radius=5)
        texto_jackie = fonte_botoes.render("JACKIE", True, PRETO)
        tela.blit(texto_jackie, (rect_botao_jackie.centerx - texto_jackie.get_width()//2, rect_botao_jackie.centery - texto_jackie.get_height()//2))
    
    popup_upgrades.draw(tela, dinheiro)
    popup_contatos.draw(tela, dinheiro)
    if chip_ativo:
        chip_ativo.draw(tela)

    pygame.display.flip()
pygame.quit()