# main.py — Larica Zero (Flet + Gemini, mobile, com cards e botão "Nova receita")
# Requisitos:
#   pip install flet google-genai python-dotenv
# Ambiente:
#   .env com GEMINI_API_KEY=suachave

import os
import re
import flet as ft
from dotenv import load_dotenv
from google import genai  # cliente moderno do Gemini

# ---------- Paleta ----------
PRIMARY_GREEN   = "#2D7230"
ACCENT_ORANGE   = "#FF6F36"
TEXT_DARK       = "#111111"
TEXT_MUTED      = "#666666"
CARD_SHADOW     = "#15000000"  # #aarrggbb
APP_BG          = "#FFF6EE"

# ---------- Fontes ----------
FONT_DISPLAY = "Poppins"
FONT_BODY    = "Montserrat"

# ---------- Título das seções ----------
TITLE_COLOR = ft.Colors.GREEN_700  # troque por ft.Colors.BLUE_700 se preferir azul

# ---------- IA ----------
load_dotenv()
client = genai.Client()            # lê GEMINI_API_KEY do ambiente
MODEL_NAME = "gemini-2.0-flash"    # modelo do catálogo atual

def main(page: ft.Page):
    # Página
    page.title   = "Larica Zero"
    page.padding = 16
    page.bgcolor = APP_BG
    page.scroll  = "adaptive"

    # Mapeamento de fontes (se tiver os arquivos em assets/fonts)
    page.fonts = {
        FONT_DISPLAY: "assets/fonts/Poppins-SemiBold.ttf",
        FONT_BODY:    "assets/fonts/Montserrat-Regular.ttf",
    }
    page.theme = ft.Theme(font_family=FONT_BODY)

    # SnackBar compatível
    def avisar(msg: str):
        page.snack_bar = ft.SnackBar(content=ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    # ---------- Cabeçalho com imagem escolhida ----------
    header = ft.Container(
        alignment=ft.alignment.center,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Image(
                    src="assets/chef-weed.png",   # mantém sua imagem escolhida
                    width=page.width * 0.75,
                    height=220,
                    fit=ft.ImageFit.COVER,
                    expand=True,
                ),
                ft.Text(
                    "Larica Zero",
                    size=44,
                    weight=ft.FontWeight.W_700,
                    color=PRIMARY_GREEN,
                    font_family=FONT_DISPLAY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Com Chef Bob Weed",
                    color=ACCENT_ORANGE,
                    font_family=FONT_BODY,
                    size=20,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Transforme sobras em receitas!",
                    size=14,
                    color=TEXT_MUTED,
                    font_family=FONT_BODY,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
    )

    # ---------- Entrada (uma linha, vírgulas) ----------
    ingredientes_tf = ft.TextField(
        label="Ingredientes (separe por vírgulas)",
        hint_text="Ex.: pão, frango, alface, tomate ",
        multiline=False,
        max_lines=1,
        expand=True,
    )

    def ler_ingredientes() -> list[str]:
        bruto = (ingredientes_tf.value or "").strip()
        itens = [p.strip() for p in bruto.split(",")]
        return [p for p in itens if p]

    # ---------- Área de resultado ----------
    receita_area = ft.Column(spacing=16)

    # ---------- Parser de texto -> seções ----------
    def parse_receita_texto(texto: str) -> dict:
        """
        Retorna: {titulo, tempo, ingredientes:list, preparo:list, dica:str}
        NÃO Aceita cabeçalhos com markdown e captura dica na MESMA linha após ':'.
        """
        dados = {"titulo": "", "tempo": "", "ingredientes": [], "preparo": [], "dica": ""}

        linhas = [l.strip() for l in (texto or "").splitlines()]
        linhas = [re.sub(r"^[#>\*\s_]+", "", l) for l in linhas]  # remove #, *, >, _, espaços

        sec = None
        for l in linhas:
            if not l:
                continue

            low = l.lower()

            # Título
            if low.startswith(("título", "titulo")):
                dados["titulo"] = l.split(":", 1)[-1].strip() if ":" in l else l
                sec = None
                continue

            # Tempo
            if low.startswith("tempo"):
                dados["tempo"] = l.split(":", 1)[-1].strip() if ":" in l else l
                sec = None
                continue

            # Ingredientes (com possível item inline após ':')
            if low.startswith("ingredientes"):
                sec = "ingredientes"
                if ":" in l:
                    resto = l.split(":", 1)[-1].strip()
                    if resto:
                        resto = re.sub(r"^[-•]\s*", "", resto)
                        dados["ingredientes"].append(resto)
                continue

            # Preparo (com possível passo inline após ':')
            if low.startswith("modo de preparo") or low.startswith("modo de prepraro"):
                sec = "preparo"
                if ":" in l:
                    resto = l.split(":", 1)[-1].strip()
                    if resto:
                        resto = re.sub(r"^\d+\)\s*", "", resto)
                        dados["preparo"].append(resto)
                continue

            # Dica do Chef (variações) — CAPTURA inline e continua acumulando
            if low.startswith(("dica do chef", "dica do chefe", "dica")):
                sec = "dica"
                if ":" in l:
                    inline = l.split(":", 1)[-1].strip()
                    if inline:
                        dados["dica"] += (("" if not dados["dica"] else " ") + inline)
                continue

            # Conteúdo por seção atual
            if sec == "ingredientes":
                item = re.sub(r"^[-•]\s*", "", l)
                if item:
                    dados["ingredientes"].append(item)
            elif sec == "preparo":
                passo = re.sub(r"^\d+\)\s*", "", l)
                if passo:
                    dados["preparo"].append(passo)
            elif sec == "dica":
                frag = re.sub(r"^[-•]\s*", "", l)
                if frag:
                    dados["dica"] += (("" if not dados["dica"] else " ") + frag)

        # Fallback do título
        if not dados["titulo"]:
            for l in linhas:
                if l:
                    dados["titulo"] = l
                    break

        return dados

    # ---------- Fábrica de UI ----------
    def titulo_secao(texto: str, cor=TITLE_COLOR, size=22):
        return ft.Text(texto, size=size, weight=ft.FontWeight.BOLD, color=cor)

    def card_secao(titulo: str, corpo_controls: list[ft.Control], icon: ft.Icon | None = None):
        cabecalho = ft.Row(
            controls=[icon if icon else ft.Container(width=0, height=0), titulo_secao(titulo)],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        return ft.Card(
            content=ft.Container(
                bgcolor="white",
                padding=20,
                border_radius=12,
                shadow=ft.BoxShadow(blur_radius=16, spread_radius=2, color=CARD_SHADOW),
                content=ft.Column(spacing=12, controls=[cabecalho] + corpo_controls),
            )
        )

    def bullets(itens: list[str]) -> list[ft.Control]:
        return [ft.Row(spacing=8, controls=[ft.Text("•", color=TITLE_COLOR), ft.Text(t, color=TEXT_DARK)]) for t in itens]

    def numerados(passos: list[str]) -> list[ft.Control]:
        out = []
        for i, p in enumerate(passos, 1):
            out.append(ft.Row(spacing=8, controls=[ft.Text(f"{i}.", color=TITLE_COLOR), ft.Text(p, color=TEXT_DARK)]))
        return out

    # ---------- Handler de geração ----------
    def gerar_receita(e=None):
        itens = ler_ingredientes()
        if not itens:
            avisar("Digite ao menos 1 ingrediente.")
            return

        # Mantém seu prompt (estilo irreverente do Chef)
        prompt = (
            "Gere 1 receita em português BR, direta e organizada, de um jeito descontraído e engraçado, "
            "como se fosse um hippie legal conversando com suas gírias. Sugira nomes curtos, bacanas e engraçados para a receita.\n"
            "Formato:\n"
            "Título\n"
            "Tempo: X min\n"
            "Ingredientes:\n"
            "- item\n"
            "Modo de Preparo:\n"
            "1) passo\n"
            "Dica do Chef Bob Weed: frase curta.\n"
            f"Ingredientes: {', '.join(itens)}"
        )

        try:
            resp = client.models.generate_content(model=MODEL_NAME, contents=[prompt])
            texto = (getattr(resp, "text", None) or "").strip()
            if not texto:
                avisar("A resposta veio vazia.")
                return
        except Exception as err:
            avisar(f"Erro na geração: {err}")
            return

        dados = parse_receita_texto(texto)
        cards: list[ft.Control] = []

        # Card 1: Título
        cards.append(
            card_secao(
                "Nome da Receita",
                [ft.Text(dados["titulo"] or "Receita", size=26, weight=ft.FontWeight.W_700, color=ft.Colors.BLUE_600)],
                icon=ft.Icon(name=ft.Icons.RESTAURANT, color=TITLE_COLOR),
            )
        )

        # Card 2: Tempo
        cards.append(
            card_secao(
                "Tempo de Preparo",
                [ft.Text(dados["tempo"] or "—", size=18, color=TEXT_DARK)],
                icon=ft.Icon(name=ft.Icons.TIMER, color=TITLE_COLOR),
            )
        )

        # Card 3: Ingredientes
        cards.append(
            card_secao(
                "Ingredientes",
                bullets(dados["ingredientes"] or []),
                icon=ft.Icon(name=ft.Icons.SHOPPING_BAG, color=TITLE_COLOR),
            )
        )

        # Card 4: Modo de Preparo
        cards.append(
            card_secao(
                "Modo de Preparo",
                numerados(dados["preparo"] or []),
                icon=ft.Icon(name=ft.Icons.LIST, color=TITLE_COLOR),
            )
        )

        # Card 5: Dica do Chef (só se houver conteúdo)
        if (dados.get("dica") or "").strip():
            dica_card = card_secao(
                "Dica do Chef Bob Weed",
                [
                    ft.Container(
                        bgcolor=ft.Colors.GREEN_50 if TITLE_COLOR == ft.Colors.GREEN_700 else ft.Colors.BLUE_50,
                        border_radius=8,
                        padding=12,
                        content=ft.Text(dados["dica"], italic=True, color=TEXT_DARK),
                    )
                ],
                icon=ft.Icon(name=ft.Icons.TIPS_AND_UPDATES, color=TITLE_COLOR),
            )
            cards.append(dica_card)

        # Botão de retorno (sempre por último)
        def voltar_inicio(e=None):
            receita_area.controls.clear()
            ingredientes_tf.value = ""
            page.update()
            ingredientes_tf.focus()

        cards.append(
            ft.Container(
                alignment=ft.alignment.center,
                content=ft.OutlinedButton(
                    text="Nova receita",
                    on_click=voltar_inicio,
                    icon=ft.Icons.ARROW_UPWARD,
                ),
            )
        )

        # Render
        receita_area.controls.clear()
        for c in cards:
            receita_area.controls.append(c)
        page.update()

    gerar_btn = ft.ElevatedButton(
        text="Gerar Receita",
        on_click=gerar_receita,
        bgcolor=ACCENT_ORANGE,
        color="white",
        width=220,
        height=55,
    )

    # ---------- Montagem ----------
    page.add(
        header,
        ft.Divider(height=12, color="#EEEEEE"),
        ingredientes_tf,
        ft.Container(height=10),
        ft.Row([gerar_btn], alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(height=10, color="#EEEEEE"),
        receita_area,
    )

ft.app(target=main, assets_dir="assets")
