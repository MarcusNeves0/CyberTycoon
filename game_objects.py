# game_objects.py

import pygame
import math
import os
import random

from settings import *
from helpers import formatar_numero


class UpgradeUnico:
    def __init__(self, nome, nivel_req, custo, descricao, imagem_path):
        self.nome = nome
        self.nivel_req = nivel_req
        self.custo = custo
        self.descricao = descricao
        self.imagem = pygame.image.load(imagem_path).convert_alpha()
        self.imagem = pygame.transform.scale(self.imagem, (50, 50))
        self.comprado = False
        self.rect = None


class Implante:
    def __init__(self, x, y, nome, custo_base, renda_base, image_path=None, bloqueado=False):
        self.nome = nome
        self.quantidade = 0
        self.custo_base = custo_base
        self.custo_atual = 0
        self.renda_base = renda_base
        self.renda_total = 0.0
        self.imagem = None
        self.bloqueado = bloqueado
        if image_path:
            caminho_completo = os.path.join("Implantes", image_path)
            try:
                self.imagem = pygame.image.load(caminho_completo).convert_alpha()
                self.imagem = pygame.transform.scale(self.imagem, (60, 80))
            except pygame.error as e:
                print(f"Erro ao carregar a imagem '{caminho_completo}': {e}")

        self.rect_principal = pygame.Rect(x, y, 250, 140)
        self.rect_botao_upgrades = pygame.Rect(15, 105, 220, 28)
        self.upgrades_unicos = []
        self._criar_upgrades_unicos()
        self._update_custo_proximo_nivel(None)
        self._recalculate_total_income()

    def _criar_upgrades_unicos(self):
        if self.nome == "Memory Boost":
            self.upgrades_unicos.append(UpgradeUnico("Nível Grátis", 10, 500,
                                                     "A cada nível comprado tem 4% de chance de evoluir um nível grátis",
                                                     os.path.join("Upgrades", "MemoryLevel.png")))
            self.upgrades_unicos.append(
                UpgradeUnico("Ganhos Dobrados", 50, 5000, "Os chips de memória dobram os edinhos gerados",
                             os.path.join("Upgrades", "MemoryV2.png")))
            self.upgrades_unicos.append(
                UpgradeUnico("Velocidade Duplicada", 100, 15000, "Velocidade de geração de edinhos duplicada",
                             os.path.join("Upgrades", "ImplanteMelhorado.png")))
            self.upgrades_unicos.append(UpgradeUnico("Backup em Nuvem", 200, 35000,
                                                     "Receba 10% da sua renda antiga instantaneamente ao comprar níveis",
                                                     os.path.join("Upgrades", "BackupNuvem.png")))

            # <<< MUDANÇA AQUI: O antigo upgrade foi substituído pelo novo >>>
            self.upgrades_unicos.append(UpgradeUnico("Memory Donate", 1000, 3e12,
                                                     "A cada nível comprado tem 2% de chance de ganhar um nível em outro implante aleatório (não inclui implantes dos contatos)",
                                                     os.path.join("Upgrades",
                                                                  "MemoryDiscount.png")))  # Reutilizando a imagem por enquanto

    def get_upgrade_unico(self, nome):
        for up in self.upgrades_unicos:
            if up.nome == nome:
                return up
        return None

    def _get_custo_para_nivel(self, nivel, lista_implantes_completa):
        multiplicador_custo = 1.05
        custo_base = 0
        if self.nome == "Memory Boost":
            if nivel == 1: return 0
            if nivel == 2: return 10
            custo_base = math.ceil(10 * (multiplicador_custo ** (nivel - 2)))
        else:
            custo_base = math.ceil(self.custo_base * (multiplicador_custo ** (nivel - 1)))

        # A lógica do Desconto Global foi removida pois o upgrade não existe mais
        return custo_base

    def _update_custo_proximo_nivel(self, lista_implantes_completa):
        self.custo_atual = self._get_custo_para_nivel(self.quantidade + 1, lista_implantes_completa)

    def _recalculate_total_income(self):
        bonus_renda_por_nivel = 1.05
        multiplicador_renda = 1.0
        up_ganhos = self.get_upgrade_unico("Ganhos Dobrados")
        if up_ganhos and up_ganhos.comprado:
            multiplicador_renda *= 2
        up_velocidade = self.get_upgrade_unico("Velocidade Duplicada")
        if up_velocidade and up_velocidade.comprado:
            multiplicador_renda *= 2

        total = 0.0
        for i in range(self.quantidade):
            total += self.renda_base * (bonus_renda_por_nivel ** i)
        self.renda_total = total * multiplicador_renda

    def calcular_custo_compra(self, modo_compra, dinheiro_jogador, lista_implantes_completa):
        if modo_compra == 'MAX':
            custo_total = 0;
            qtd_a_comprar = 0;
            dinheiro_restante = dinheiro_jogador;
            nivel_atual = self.quantidade + 1
            while True:
                custo_nivel = self._get_custo_para_nivel(nivel_atual, lista_implantes_completa)
                if dinheiro_restante >= custo_nivel:
                    dinheiro_restante -= custo_nivel;
                    custo_total += custo_nivel;
                    qtd_a_comprar += 1;
                    nivel_atual += 1
                else:
                    break
            return (qtd_a_comprar, custo_total)
        else:
            qtd_a_comprar = int(modo_compra.replace('x', ''))
            custo_total = 0
            for i in range(qtd_a_comprar):
                custo_total += self._get_custo_para_nivel(self.quantidade + 1 + i, lista_implantes_completa)
            return (qtd_a_comprar, custo_total)

    def comprar(self, dinheiro_jogador, modo_compra, lista_implantes_completa):
        if self.bloqueado: return (0, 0)
        qtd_a_comprar, custo_total = self.calcular_custo_compra(modo_compra, dinheiro_jogador, lista_implantes_completa)
        if dinheiro_jogador >= custo_total and qtd_a_comprar > 0:
            renda_antiga = self.renda_total
            self.quantidade += qtd_a_comprar

            
            up_nivel_gratis = self.get_upgrade_unico("Nível Grátis")
            if up_nivel_gratis and up_nivel_gratis.comprado:
                for _ in range(qtd_a_comprar):
                    if random.random() < 0.04:
                        self.quantidade += 1

           
            up_donate = self.get_upgrade_unico("Memory Donate")
            if up_donate and up_donate.comprado:
                
                implantes_elegiveis = [
                    imp for imp in lista_implantes_completa
                    if imp.nome != self.nome and not imp.bloqueado
                ]
                if implantes_elegiveis:
                    for _ in range(qtd_a_comprar):
                        if random.random() < 0.02:  
                            implante_sorteado = random.choice(implantes_elegiveis)
                            implante_sorteado.quantidade += 1
                            
                            implante_sorteado._recalculate_total_income()
                            implante_sorteado._update_custo_proximo_nivel(lista_implantes_completa)

            bonus_imediato = 0
            up_backup = self.get_upgrade_unico("Backup em Nuvem")
            if up_backup and up_backup.comprado:
                bonus_imediato = renda_antiga * 0.10 * qtd_a_comprar

            self._recalculate_total_income()
            self._update_custo_proximo_nivel(lista_implantes_completa)
            return (custo_total, bonus_imediato)
        return (0, 0)

    def draw(self, target_surface, fonte_nome, fonte_item, scroll_offset, dinheiro_jogador, modo_compra,
             lista_implantes_completa):
        if self.bloqueado:
            return

        final_y = self.rect_principal.y + scroll_offset
        if final_y > ALTURA or (final_y + self.rect_principal.height) < 0:
            return
        surface_upgrade = pygame.Surface((self.rect_principal.width, self.rect_principal.height), pygame.SRCALPHA)
        pygame.draw.rect(surface_upgrade, CINZA_UPGRADE, surface_upgrade.get_rect(), border_radius=5)
        texto_nome = fonte_nome.render(self.nome, True, CIANO_NEON)
        surface_upgrade.blit(texto_nome, (10, 10))
        if self.imagem:
            surface_upgrade.blit(self.imagem, (180, 25))
        else:
            pygame.draw.rect(surface_upgrade, (0, 255, 0, 150), pygame.Rect(180, 25, 60, 80))
        texto_qtd = fonte_item.render(f"Nível: {self.quantidade}", True, AZUL)
        surface_upgrade.blit(texto_qtd, (15, 45))
        texto_renda = fonte_item.render(f"Gera: {formatar_numero(self.renda_total)} E/s", True, AMARELO)
        surface_upgrade.blit(texto_renda, (15, 65))
        qtd_display, custo_display = self.calcular_custo_compra(modo_compra, dinheiro_jogador, lista_implantes_completa)
        cor_preco = VERDE if dinheiro_jogador >= custo_display and qtd_display > 0 else VERMELHO
        texto_str_preco = f"({qtd_display}x): {formatar_numero(custo_display)}"
        if modo_compra == 'MAX' and qtd_display == 0:
            texto_str_preco = f"Custo: {formatar_numero(self.custo_atual)}"
        texto_preco = fonte_item.render(texto_str_preco, True, cor_preco)
        surface_upgrade.blit(texto_preco, (15, 85))

        if self.upgrades_unicos:
            pygame.draw.rect(surface_upgrade, CINZA_BOTAO, self.rect_botao_upgrades, border_radius=5)
            texto_botao = fonte_item.render("Upgrades", True, BRANCO)
            surface_upgrade.blit(texto_botao, (self.rect_botao_upgrades.centerx - texto_botao.get_width() // 2,
                                               self.rect_botao_upgrades.centery - texto_botao.get_height() // 2))

        target_surface.blit(surface_upgrade, (self.rect_principal.x, final_y))


class BonusChip:
    def __init__(self):
        try:
            self.imagem = pygame.image.load(os.path.join("Implantes", "ArasakaLogo.png")).convert_alpha()
            self.imagem = pygame.transform.scale(self.imagem, (60, 60))
        except pygame.error:
            self.imagem = pygame.Surface((60, 60));
            self.imagem.fill(AMARELO)

        spawn_area_x = 300
        pos_x = random.randint(spawn_area_x, LARGURA - self.imagem.get_width() - 120)
        pos_y = random.randint(80, ALTURA - self.imagem.get_height())

        self.rect = self.imagem.get_rect(topleft=(pos_x, pos_y))
        self.tempo_de_vida = 10

    def update(self, dt):
        self.tempo_de_vida -= dt
        return self.tempo_de_vida > 0

    def draw(self, tela):
        tela.blit(self.imagem, self.rect)