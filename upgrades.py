# upgrades.py

import pygame
from settings import *
from helpers import formatar_numero, draw_text_wrapped


class UpgradesPopup:
    def __init__(self):
        self.visivel = False
        self.implante_selecionado = None
        self.rect_popup = pygame.Rect(LARGURA // 2 - 250, ALTURA // 2 - 225, 500, 450)
        self.botao_fechar_popup = pygame.Rect(self.rect_popup.right - 35, self.rect_popup.top + 5, 30, 30)
        self.fonte_titulo = pygame.font.SysFont('Consolas', 30, bold=True)
        self.fonte_item = pygame.font.SysFont('Consolas', 16)
        self.fonte_botoes = pygame.font.SysFont('Consolas', 20, bold=True)

    def abrir(self, implante):
        self.implante_selecionado = implante
        self.visivel = True

    def fechar(self):
        self.visivel = False
        self.implante_selecionado = None

    def handle_event(self, event, dinheiro, lista_implantes):
        # <<< CORREÇÃO AQUI: A função agora retorna o objeto do upgrade, não o custo >>>
        objeto_comprado = None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.botao_fechar_popup.collidepoint(event.pos):
                self.fechar()

            if self.implante_selecionado:
                for up in self.implante_selecionado.upgrades_unicos:
                    if up.rect and up.rect.collidepoint(
                            event.pos) and not up.comprado and dinheiro >= up.custo and self.implante_selecionado.quantidade >= up.nivel_req:
                        up.comprado = True
                        objeto_comprado = up  # Armazena o objeto do upgrade
                        # Recalcula tudo que pode ter sido afetado pelo upgrade
                        self.implante_selecionado._recalculate_total_income()
                        self.implante_selecionado._update_custo_proximo_nivel(lista_implantes)
                        break  # Sai do loop após uma compra

        return objeto_comprado

    def draw(self, tela, dinheiro):
        if not self.visivel or not self.implante_selecionado:
            return

        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        tela.blit(overlay, (0, 0))

        pygame.draw.rect(tela, CINZA_UPGRADE, self.rect_popup, border_radius=10)
        pygame.draw.rect(tela, CIANO_NEON, self.rect_popup, width=2, border_radius=10)

        titulo_popup = self.fonte_titulo.render(f"Upgrades de {self.implante_selecionado.nome}", True, CIANO_NEON)
        tela.blit(titulo_popup, (self.rect_popup.centerx - titulo_popup.get_width() // 2, self.rect_popup.top + 20))

        y_pos_up = self.rect_popup.top + 80
        for up in self.implante_selecionado.upgrades_unicos:
            if self.implante_selecionado.quantidade >= up.nivel_req:
                tela.blit(up.imagem, (self.rect_popup.left + 15, y_pos_up))
                desc_rect = pygame.Rect(self.rect_popup.left + 75, y_pos_up + 5, 275, 100)
                altura_texto = draw_text_wrapped(tela, up.descricao, self.fonte_item, BRANCO, desc_rect)
                rect_compra = pygame.Rect(self.rect_popup.left + 360, y_pos_up, 120, 50)
                up.rect = rect_compra
                if up.comprado:
                    pygame.draw.rect(tela, VERDE, rect_compra, border_radius=5)
                    texto_botao = self.fonte_botoes.render("COMPRADO", True, PRETO)
                elif dinheiro >= up.custo:
                    pygame.draw.rect(tela, CIANO_NEON, rect_compra, border_radius=5)
                    texto_botao = self.fonte_botoes.render(f"{formatar_numero(up.custo)}", True, PRETO)
                else:
                    pygame.draw.rect(tela, VERMELHO, rect_compra, border_radius=5)
                    texto_botao = self.fonte_botoes.render(f"{formatar_numero(up.custo)}", True, PRETO)
                tela.blit(texto_botao, (rect_compra.centerx - texto_botao.get_width() // 2,
                                        rect_compra.centery - texto_botao.get_height() // 2))
                y_pos_up += max(50, altura_texto) + 15

        pygame.draw.rect(tela, VERMELHO, self.botao_fechar_popup, border_radius=5)
        texto_fechar = self.fonte_botoes.render("X", True, BRANCO)
        tela.blit(texto_fechar, (self.botao_fechar_popup.centerx - texto_fechar.get_width() // 2,
                                 self.botao_fechar_popup.centery - texto_fechar.get_height() // 2))