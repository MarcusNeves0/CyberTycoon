import pygame
import math
import os
import random


# <<< SUBSTITUÍDA A FUNÇÃO ANTIGA POR ESTA VERSÃO DEFINITIVA >>>
def formatar_numero(num):
    """Formata um número para o padrão K, M, B, T e além, gerando novos sufixos (AA, AB...) para números gigantescos."""
    num = float(num)
    if num < 1000:
        return str(int(num))

    # Usamos o logaritmo para descobrir a "magnitude" do número (quantos grupos de 3 zeros ele tem)
    # math.log10(num) nos dá o expoente (ex: para 1,000,000 é ~6). Dividindo por 3, sabemos o grupo.
    magnitude = int(math.log10(num) // 3)

    # O valor que será exibido (ex: 1.23)
    valor_exibido = num / (10 ** (magnitude * 3))

    # Lista dos primeiros sufixos, que são padrão
    sufixos_padrao = ['K', 'M', 'B', 'T', 'P', 'E', 'Z', 'Y']

    sufixo_final = ''
    # O índice na lista é a magnitude - 1 (K é o 1º grupo, índice 0)
    indice_sufixo = magnitude - 1

    if indice_sufixo < len(sufixos_padrao):
        # Se o índice está dentro da nossa lista padrão, pegue o sufixo de lá
        sufixo_final = sufixos_padrao[indice_sufixo]
    else:
        # Se o número é maior que 'Yotta', vamos gerar um sufixo de 2 letras
        # O índice para as letras começa depois da lista padrão
        indice_letras = indice_sufixo - len(sufixos_padrao)
        # Lógica para encontrar a primeira e a segunda letra (A=0, B=1, etc.)
        primeira_letra = chr(ord('A') + (indice_letras // 26))
        segunda_letra = chr(ord('A') + (indice_letras % 26))
        sufixo_final = primeira_letra + segunda_letra

    # .rstrip('0').rstrip('.') remove zeros desnecessários (ex: 1.20M -> 1.2M, 1.00M -> 1M)
    return f"{valor_exibido:.2f}".rstrip('0').rstrip('.') + sufixo_final


def draw_text_wrapped(surface, text, font, color, rect):
    # ... (função sem alterações)
    words = text.split(' ');
    lines = [];
    current_line = ''
    for word in words:
        test_line = current_line + word + ' '
        if font.size(test_line)[0] < rect.width:
            current_line = test_line
        else:
            lines.append(current_line); current_line = word + ' '
    lines.append(current_line)
    y = rect.y
    for line in lines:
        line_surface = font.render(line, True, color);
        surface.blit(line_surface, (rect.x, y));
        y += font.get_linesize()
    return y - rect.y


class UpgradeUnico:
    # ... (classe sem alterações)
    def __init__(self, nome, nivel_req, custo, descricao, imagem_path):
        self.nome = nome;
        self.nivel_req = nivel_req;
        self.custo = custo;
        self.descricao = descricao
        self.imagem = pygame.image.load(imagem_path).convert_alpha();
        self.imagem = pygame.transform.scale(self.imagem, (50, 50))
        self.comprado = False;
        self.rect = None


class Implante:
    # ... (classe sem alterações)
    def __init__(self, x, y, nome, custo_base, renda_base, image_path=None):
        self.nome = nome;
        self.quantidade = 0;
        self.custo_base = custo_base;
        self.custo_atual = 0;
        self.renda_base = renda_base;
        self.renda_total = 0.0;
        self.imagem = None
        if image_path:
            try:
                self.imagem = pygame.image.load(os.path.join("Implantes", image_path)).convert_alpha()
                self.imagem = pygame.transform.scale(self.imagem, (60, 80))
            except pygame.error as e:
                print(f"Erro ao carregar a imagem '{image_path}': {e}")
        self.rect_principal = pygame.Rect(x, y, 250, 140);
        self.rect_botao_upgrades = pygame.Rect(15, 105, 220, 28);
        self.upgrades_unicos = []
        self._criar_upgrades_unicos();
        self._update_custo_proximo_nivel(None);
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
            self.upgrades_unicos.append(UpgradeUnico("Desconto Global", 1000, 50000,
                                                     "Custo das memórias -1% por cada nível de upgrade que você já tem nos outros implantes",
                                                     os.path.join("Upgrades", "MemoryDiscount.png")))

    def get_upgrade_unico(self, nome):
        for up in self.upgrades_unicos:
            if up.nome == nome: return up
        return None

    def _get_custo_para_nivel(self, nivel, lista_implantes_completa):
        multiplicador_custo = 1.05;
        custo_base = 0
        if self.nome == "Memory Boost":
            if nivel == 1: return 0
            if nivel == 2: return 10
            custo_base = math.ceil(10 * (multiplicador_custo ** (nivel - 2)))
        else:
            custo_base = math.ceil(self.custo_base * (multiplicador_custo ** (nivel - 1)))
        up_desconto = self.get_upgrade_unico("Desconto Global")
        if up_desconto and up_desconto.comprado and lista_implantes_completa:
            total_niveis_outros = sum(
                implante.quantidade for implante in lista_implantes_completa if implante.nome != self.nome)
            desconto = min(total_niveis_outros * 0.01, 0.9)
            return math.ceil(custo_base * (1.0 - desconto))
        return custo_base

    def _update_custo_proximo_nivel(self, lista_implantes_completa):
        self.custo_atual = self._get_custo_para_nivel(self.quantidade + 1, lista_implantes_completa)

    def _recalculate_total_income(self):
        bonus_renda_por_nivel = 1.05;
        multiplicador_renda = 1.0
        if self.get_upgrade_unico("Ganhos Dobrados") and self.get_upgrade_unico(
            "Ganhos Dobrados").comprado: multiplicador_renda *= 2
        if self.get_upgrade_unico("Velocidade Duplicada") and self.get_upgrade_unico(
            "Velocidade Duplicada").comprado: multiplicador_renda *= 2
        total = 0.0
        for i in range(self.quantidade): total += self.renda_base * (bonus_renda_por_nivel ** i)
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
            qtd_a_comprar = int(modo_compra.replace('x', ''));
            custo_total = 0
            for i in range(qtd_a_comprar): custo_total += self._get_custo_para_nivel(self.quantidade + 1 + i,
                                                                                     lista_implantes_completa)
            return (qtd_a_comprar, custo_total)

    def comprar(self, dinheiro_jogador, modo_compra, lista_implantes_completa):
        qtd_a_comprar, custo_total = self.calcular_custo_compra(modo_compra, dinheiro_jogador, lista_implantes_completa)
        if dinheiro_jogador >= custo_total and qtd_a_comprar > 0:
            renda_antiga = self.renda_total;
            self.quantidade += qtd_a_comprar
            if self.get_upgrade_unico("Nível Grátis") and self.get_upgrade_unico("Nível Grátis").comprado:
                for _ in range(qtd_a_comprar):
                    if random.random() < 0.04: self.quantidade += 1
            bonus_imediato = 0
            if self.get_upgrade_unico("Backup em Nuvem") and self.get_upgrade_unico(
                "Backup em Nuvem").comprado: bonus_imediato = renda_antiga * 0.10 * qtd_a_comprar
            self._recalculate_total_income();
            self._update_custo_proximo_nivel(lista_implantes_completa)
            return (custo_total, bonus_imediato)
        return (None, None)

    def draw(self, target_surface, fonte_nome, fonte_item, scroll_offset, dinheiro_jogador, modo_compra,
             lista_implantes_completa):
        final_y = self.rect_principal.y + scroll_offset
        if final_y > ALTURA or (final_y + self.rect_principal.height) < 0: return
        surface_upgrade = pygame.Surface((self.rect_principal.width, self.rect_principal.height), pygame.SRCALPHA)
        pygame.draw.rect(surface_upgrade, CINZA_UPGRADE, surface_upgrade.get_rect(), border_radius=5)
        texto_nome = fonte_nome.render(self.nome, True, CIANO_NEON);
        surface_upgrade.blit(texto_nome, (10, 10))
        if self.imagem:
            surface_upgrade.blit(self.imagem, (180, 25))
        else:
            pygame.draw.rect(surface_upgrade, (0, 255, 0, 150), pygame.Rect(180, 25, 60, 80))
        texto_qtd = fonte_item.render(f"Nível: {self.quantidade}", True, AZUL);
        surface_upgrade.blit(texto_qtd, (15, 45))
        texto_renda = fonte_item.render(f"Gera: {formatar_numero(self.renda_total)} E/s", True, AMARELO);
        surface_upgrade.blit(texto_renda, (15, 65))
        qtd_display, custo_display = self.calcular_custo_compra(modo_compra, dinheiro_jogador, lista_implantes_completa)
        cor_preco = VERDE if dinheiro_jogador >= custo_display and qtd_display > 0 else VERMELHO
        texto_str_preco = f"Custo ({qtd_display}x): {formatar_numero(custo_display)}"
        if modo_compra == 'MAX' and qtd_display == 0: texto_str_preco = f"Custo: {formatar_numero(self.custo_atual)}"
        texto_preco = fonte_item.render(texto_str_preco, True, cor_preco)
        surface_upgrade.blit(texto_preco, (15, 85))
        pygame.draw.rect(surface_upgrade, CINZA_BOTAO, self.rect_botao_upgrades, border_radius=5)
        texto_botao = fonte_item.render("Upgrades", True, BRANCO)
        surface_upgrade.blit(texto_botao, (self.rect_botao_upgrades.centerx - texto_botao.get_width() // 2,
                                           self.rect_botao_upgrades.centery - texto_botao.get_height() // 2))
        target_surface.blit(surface_upgrade, (self.rect_principal.x, final_y))


# --- Bloco Principal do Jogo ---
pygame.init()
LARGURA, ALTURA = 800, 600;
tela = pygame.display.set_mode((LARGURA, ALTURA));
pygame.display.set_caption("Cyberpunk Tycoon")
FUNDO_ESCURO = (20, 20, 30);
CINZA_UPGRADE = (80, 80, 80, 220);
BRANCO = (255, 255, 255);
PRETO = (0, 0, 0);
CIANO_NEON = (0, 255, 255);
AZUL = (100, 140, 255);
AMARELO = (255, 255, 100);
VERDE = (100, 255, 100);
VERMELHO = (255, 100, 100);
CINZA_BOTAO = (100, 100, 100)
fonte_dinheiro = pygame.font.SysFont('Consolas', 40, bold=True);
fonte_nome_upgrade = pygame.font.SysFont('Consolas', 18, bold=True);
fonte_item = pygame.font.SysFont('Consolas', 16);
fonte_botoes = pygame.font.SysFont('Consolas', 20, bold=True);
fonte_popup_titulo = pygame.font.SysFont('Consolas', 30, bold=True)
try:
    background_imagem = pygame.image.load('Background.png').convert()
    background_imagem = pygame.transform.scale(background_imagem, (LARGURA, ALTURA))
except pygame.error:
    background_imagem = None
dinheiro = 0.0;
scroll_offset_y = 0;
modo_compra = '1x';
popup_visivel = False;
implante_selecionado_popup = None
PAINEL_ESQUERDO_X = 20;
rect_quadro_preto = pygame.Rect(PAINEL_ESQUERDO_X - 10, 70, 270, 55);
rect_area_scroll = pygame.Rect(PAINEL_ESQUERDO_X, rect_quadro_preto.bottom + 5, 260,
                               ALTURA - rect_quadro_preto.bottom - 25);
upgrades_surface = pygame.Surface(rect_area_scroll.size, pygame.SRCALPHA)
botoes_texto = ['1x', '5x', '10x', '50x', 'MAX'];
botoes_modo_compra = {}
for i, texto in enumerate(botoes_texto): botoes_modo_compra[texto] = pygame.Rect(rect_quadro_preto.x + 5 + i * 52,
                                                                                 rect_quadro_preto.y + 10, 50, 35)
try:
    TAMANHO_BOTAO_JACKIE = (100, 80)
    imagem_botao_jackie = pygame.image.load("Jackie.png").convert_alpha()
    imagem_botao_jackie = pygame.transform.scale(imagem_botao_jackie, TAMANHO_BOTAO_JACKIE)
    rect_botao_jackie = imagem_botao_jackie.get_rect(bottomright=(LARGURA - 20, ALTURA - 20))
except pygame.error as e:
    print(f"Erro ao carregar imagem do botão Jackie: {e}")
    imagem_botao_jackie = None
    rect_botao_jackie = pygame.Rect(LARGURA - 200, ALTURA - 60, 180, 40)
rect_popup = pygame.Rect(LARGURA // 2 - 250, ALTURA // 2 - 225, 500, 450);
botao_fechar_popup = pygame.Rect(rect_popup.right - 35, rect_popup.top + 5, 30, 30)
lista_implantes = [
    Implante(5, 10, "Memory Boost", 0, 2, image_path="MemoryBoost.png"),
    Implante(5, 160, "Kiroshi Optics", 100, 15, image_path="Kiroshi.png"),
    Implante(5, 310, "RAM Upgrader", 500, 75, image_path="RamUpgrade.png"),
    Implante(5, 460, "Biomonitor", 1000, 90, image_path="Biomonitor.png"),
    Implante(5, 610, "AdrenalineBooster", 10000, 200, image_path="AdrenalineBooster.png"),
    Implante(5, 760, "Zetatech Sandevistan", 50000, 900, image_path="ZetatechSandevistan.png"),
    Implante(5, 910, "Gorilla Arms", 100000, 1400, image_path="GorillaArms.png"),
    Implante(5, 1060, "Atomic Sensors", 500000, 9000, image_path="AtomicSensors.png"),
    Implante(5, 1210, "Tattoo: Together Forever", 1000000, 15000, image_path="TogetherForever.png"),
    Implante(5, 1360, "Malorian Arms 3516", 1000000000, 2000000, image_path="Malorian.png"),
    Implante(5, 1510, "Zetatech Berserk", 1000000000000, 3000000, image_path="ZetatechBerserk.png"),
    Implante(5, 1650, "Monowire", 100000000000000, 120000000, image_path="Monowire.png"),
]
clock = pygame.time.Clock();
rodando = True
while rodando:
    dt = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT: rodando = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if popup_visivel:
                    if botao_fechar_popup.collidepoint(
                        event.pos): popup_visivel = False; implante_selecionado_popup = None
                    if implante_selecionado_popup:
                        for up in implante_selecionado_popup.upgrades_unicos:
                            if up.rect and up.rect.collidepoint(
                                    event.pos) and not up.comprado and dinheiro >= up.custo and implante_selecionado_popup.quantidade >= up.nivel_req:
                                dinheiro -= up.custo;
                                up.comprado = True
                                implante_selecionado_popup._recalculate_total_income();
                                implante_selecionado_popup._update_custo_proximo_nivel(lista_implantes)
                else:
                    if rect_botao_jackie.collidepoint(event.pos):
                        print("Botão do Jackie clicado! Nenhuma ação definida.")
                        pass
                    for texto, rect in botoes_modo_compra.items():
                        if rect.collidepoint(event.pos): modo_compra = texto
                    if rect_area_scroll.collidepoint(event.pos):
                        mouse_pos_relativa = (event.pos[0] - rect_area_scroll.x, event.pos[1] - rect_area_scroll.y)
                        for implante in lista_implantes:
                            rect_no_scroll = implante.rect_principal.move(0, scroll_offset_y)
                            if rect_no_scroll.collidepoint(mouse_pos_relativa):
                                click_no_card_x = mouse_pos_relativa[0] - rect_no_scroll.x;
                                click_no_card_y = mouse_pos_relativa[1] - rect_no_scroll.y
                                if implante.rect_botao_upgrades.collidepoint((click_no_card_x, click_no_card_y)):
                                    popup_visivel = True;
                                    implante_selecionado_popup = implante
                                else:
                                    custo_da_compra, bonus_imediato = implante.comprar(dinheiro, modo_compra,
                                                                                       lista_implantes)
                                    if custo_da_compra is not None: dinheiro -= custo_da_compra; dinheiro += bonus_imediato
        if not popup_visivel and event.type == pygame.MOUSEWHEEL:
            scroll_offset_y += event.y * 30;
            scroll_offset_y = min(scroll_offset_y, 0)
            altura_total_conteudo = lista_implantes[-1].rect_principal.bottom if lista_implantes else 0
            if altura_total_conteudo > rect_area_scroll.height:
                limite_scroll = rect_area_scroll.height - altura_total_conteudo - 10
                scroll_offset_y = max(scroll_offset_y, limite_scroll)
            else:
                scroll_offset_y = 0
    dinheiro_por_segundo = sum(implante.renda_total for implante in lista_implantes)
    dinheiro += dinheiro_por_segundo * dt
    if background_imagem:
        tela.blit(background_imagem, (0, 0))
    else:
        tela.fill(FUNDO_ESCURO)
    rect_display_dinheiro = pygame.Rect(LARGURA - 420, 20, 400, 60);
    surface_dinheiro = pygame.Surface(rect_display_dinheiro.size, pygame.SRCALPHA)
    pygame.draw.rect(surface_dinheiro, (30, 30, 30, 200), surface_dinheiro.get_rect(), border_radius=5);
    texto_dinheiro = fonte_dinheiro.render(f"Edinhos: {formatar_numero(dinheiro)}", True, CIANO_NEON);
    surface_dinheiro.blit(texto_dinheiro, (15, 10));
    tela.blit(surface_dinheiro, rect_display_dinheiro.topleft)
    upgrades_surface.fill((0, 0, 0, 0))
    for implante in lista_implantes:
        implante.draw(upgrades_surface, fonte_nome_upgrade, fonte_item, scroll_offset_y, dinheiro, modo_compra,
                      lista_implantes)
    pygame.draw.rect(tela, PRETO, rect_quadro_preto, border_radius=5)
    tela.blit(upgrades_surface, rect_area_scroll.topleft)
    for texto, rect in botoes_modo_compra.items():
        cor = CIANO_NEON if modo_compra == texto else CINZA_BOTAO
        pygame.draw.rect(tela, cor, rect, border_radius=5)
        texto_surface = fonte_botoes.render(texto, True, PRETO)
        tela.blit(texto_surface,
                  (rect.centerx - texto_surface.get_width() // 2, rect.centery - texto_surface.get_height() // 2))
    if imagem_botao_jackie:
        tela.blit(imagem_botao_jackie, rect_botao_jackie)
    else:
        pygame.draw.rect(tela, CINZA_BOTAO, rect_botao_jackie, border_radius=5)
        texto_jackie = fonte_botoes.render("JACKIE", True, PRETO)
        tela.blit(texto_jackie, (rect_botao_jackie.centerx - texto_jackie.get_width() // 2,
                                 rect_botao_jackie.centery - texto_jackie.get_height() // 2))
    if popup_visivel and implante_selecionado_popup:
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA);
        overlay.fill((0, 0, 0, 180));
        tela.blit(overlay, (0, 0))
        pygame.draw.rect(tela, CINZA_UPGRADE, rect_popup, border_radius=10);
        pygame.draw.rect(tela, CIANO_NEON, rect_popup, width=2, border_radius=10)
        titulo_popup = fonte_popup_titulo.render("Upgrades", True, CIANO_NEON)
        tela.blit(titulo_popup, (rect_popup.centerx - titulo_popup.get_width() // 2, rect_popup.top + 20))
        y_pos_up = rect_popup.top + 80
        for up in implante_selecionado_popup.upgrades_unicos:
            if implante_selecionado_popup.quantidade >= up.nivel_req:
                tela.blit(up.imagem, (rect_popup.left + 15, y_pos_up))
                desc_rect = pygame.Rect(rect_popup.left + 75, y_pos_up + 5, 275, 100)
                altura_texto = draw_text_wrapped(tela, up.descricao, fonte_item, BRANCO, desc_rect)
                rect_compra = pygame.Rect(rect_popup.left + 360, y_pos_up, 120, 50)
                up.rect = rect_compra
                if up.comprado:
                    pygame.draw.rect(tela, VERDE, rect_compra, border_radius=5)
                    texto_botao = fonte_botoes.render("COMPRADO", True, PRETO)
                elif dinheiro >= up.custo:
                    pygame.draw.rect(tela, CIANO_NEON, rect_compra, border_radius=5)
                    texto_botao = fonte_botoes.render(f"{formatar_numero(up.custo)}", True, PRETO)
                else:
                    pygame.draw.rect(tela, VERMELHO, rect_compra, border_radius=5)
                    texto_botao = fonte_botoes.render(f"{formatar_numero(up.custo)}", True, PRETO)
                tela.blit(texto_botao, (rect_compra.centerx - texto_botao.get_width() // 2,
                                        rect_compra.centery - texto_botao.get_height() // 2))
                y_pos_up += max(50, altura_texto) + 15
        pygame.draw.rect(tela, VERMELHO, botao_fechar_popup, border_radius=5)
        texto_fechar = fonte_botoes.render("X", True, BRANCO)
        tela.blit(texto_fechar, (botao_fechar_popup.centerx - texto_fechar.get_width() // 2,
                                 botao_fechar_popup.centery - texto_fechar.get_height() // 2))
    pygame.display.flip()
pygame.quit()
