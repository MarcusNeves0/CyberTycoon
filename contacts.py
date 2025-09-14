# contacts.py

import pygame
import os
from settings import *
from helpers import formatar_numero, draw_text_wrapped


class Contato:
    def __init__(self, nome, custo, descricao, imagem_path):
        self.nome = nome
        self.custo = custo
        self.descricao = descricao
        try:
            self.imagem = pygame.image.load(os.path.join("Contatos", imagem_path)).convert_alpha()
            self.imagem = pygame.transform.scale(self.imagem, (60, 60))
        except pygame.error as e:
            print(f"Erro ao carregar imagem do contato '{imagem_path}': {e}")
            self.imagem = pygame.Surface((60, 60));
            self.imagem.fill(VERMELHO)
        self.comprado = False
        self.rect = None


class ContatosPopup:
    def __init__(self, lista_contatos):
        self.visivel = False
        self.lista_contatos = lista_contatos
        self.rect_popup = pygame.Rect(LARGURA // 2 - 300, ALTURA // 2 - 250, 600, 500)
        self.botao_fechar_popup = pygame.Rect(self.rect_popup.right - 35, self.rect_popup.top + 5, 30, 30)
        self.fonte_titulo = pygame.font.SysFont('Consolas', 30, bold=True)
        self.fonte_item = pygame.font.SysFont('Consolas', 16)
        self.fonte_botoes = pygame.font.SysFont('Consolas', 20, bold=True)

    def abrir(self):
        self.visivel = True

    def fechar(self):
        self.visivel = False

    def handle_event(self, event, dinheiro):
        contato_comprado = None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.botao_fechar_popup.collidepoint(event.pos):
                self.fechar()

            for contato in self.lista_contatos:
                if contato.rect and contato.rect.collidepoint(
                        event.pos) and not contato.comprado and dinheiro >= contato.custo:
                    contato.comprado = True
                    contato_comprado = contato
                    break
        return contato_comprado

    def draw(self, tela, dinheiro):
        if not self.visivel:
            return

        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        tela.blit(overlay, (0, 0))

        pygame.draw.rect(tela, CINZA_UPGRADE, self.rect_popup, border_radius=10)
        pygame.draw.rect(tela, CIANO_NEON, self.rect_popup, width=2, border_radius=10)

        titulo_popup = self.fonte_titulo.render("Contatos", True, CIANO_NEON)
        tela.blit(titulo_popup, (self.rect_popup.centerx - titulo_popup.get_width() // 2, self.rect_popup.top + 20))

        y_pos_contato = self.rect_popup.top + 80
        for contato in self.lista_contatos:
            tela.blit(contato.imagem, (self.rect_popup.left + 15, y_pos_contato))
            desc_rect = pygame.Rect(self.rect_popup.left + 90, y_pos_contato + 5, 320, 100)
            altura_texto = draw_text_wrapped(tela, contato.descricao, self.fonte_item, BRANCO, desc_rect)
            rect_compra = pygame.Rect(self.rect_popup.left + 420, y_pos_contato, 160, 60)
            contato.rect = rect_compra

            if contato.comprado:
                pygame.draw.rect(tela, VERDE, rect_compra, border_radius=5)
                texto_botao = self.fonte_botoes.render("CONTRATADO", True, PRETO)
            elif dinheiro >= contato.custo:
                pygame.draw.rect(tela, CIANO_NEON, rect_compra, border_radius=5)
                texto_botao = self.fonte_botoes.render(f"Contratar: {formatar_numero(contato.custo)}", True, PRETO)
            else:
                pygame.draw.rect(tela, VERMELHO, rect_compra, border_radius=5)
                texto_botao = self.fonte_botoes.render(f"Custo: {formatar_numero(contato.custo)}", True, PRETO)

            tela.blit(texto_botao, (rect_compra.centerx - texto_botao.get_width() // 2,
                                    rect_compra.centery - texto_botao.get_height() // 2))
            y_pos_contato += max(60, altura_texto) + 15

        pygame.draw.rect(tela, VERMELHO, self.botao_fechar_popup, border_radius=5)
        texto_fechar = self.fonte_botoes.render("X", True, BRANCO)
        tela.blit(texto_fechar, (self.botao_fechar_popup.centerx - texto_fechar.get_width() // 2,
                                 self.botao_fechar_popup.centery - texto_fechar.get_height() // 2))