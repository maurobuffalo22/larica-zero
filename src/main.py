import flet as ft
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def main(page: ft.Page):
    page.title = "Larica Zero"
    page.padding = 30
    page.bgcolor = "#f5f5f5"
    page.scroll = "adaptive"
    
    ingredientes_input = ft.TextField(
        label="Digite os ingredientes disponíveis",
        hint_text="Ex: frango, maionese, repolho, cebola",
        multiline=True,
        min_lines=3,
        max_lines=5,
        border_color="#4CAF50",
        width=600
    )
    
    receita_container = ft.Column(spacing=20, width=800)
    
    def gerar_receita(e):
        ingredientes = ingredientes_input.value
        
        if not ingredientes or not ingredientes.strip():
            page.snack_bar = ft.SnackBar(content=ft.Text("Digite ingredientes!"), open=True)
            page.update()
            return
        
        page.snack_bar = ft.SnackBar(content=ft.Text("Chef Bob Weed preparando..."), open=True)
        page.update()
        
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"""Você é o Chef Bob Weed, um chef descontraído e engraçado! 

Crie UMA receita usando APENAS estes ingredientes: {ingredientes}

IMPORTANTE: Dê um nome ENGRAÇADO e CRIATIVO para a receita.

Formato:
Nome: [nome engraçado]
Tempo: [tempo]
Ingredientes:
- item 1
- item 2
Preparo:
1. passo 1
2. passo 2
Dica do Chef Bob Weed: [dica descontraída]"""

            response = model.generate_content(prompt)
            texto_completo = response.text.strip().replace("**", "").replace("*", "")
            
            print(f"\n{'='*60}\n{texto_completo}\n{'='*60}\n")
            
            linhas_texto = texto_completo.split("\n")
            
            receita_container.controls.clear()
            
            texto_widgets = []
            for linha in linhas_texto:
                linha_lower = linha.lower().strip()
                
                if linha_lower.startswith("nome:"):
                    nome = linha.split(":", 1)[1].strip()
                    texto_widgets.append(ft.Container(height=10))
                    texto_widgets.append(
                        ft.Text(
                            nome,
                            size=32,
                            color="#FF6B35",
                            weight=ft.FontWeight.BOLD,
                            selectable=True
                        )
                    )
                    texto_widgets.append(ft.Container(height=15))
                    
                elif linha_lower.startswith("tempo:"):
                    tempo = linha.split(":", 1)[1].strip()
                    texto_widgets.append(
                        ft.Text(
                            f"Tempo: {tempo}",
                            size=16,
                            color="#000000",
                            weight=ft.FontWeight.W_500,
                            selectable=True
                        )
                    )
                    texto_widgets.append(ft.Container(height=15))
                    
                elif linha_lower.startswith("ingredientes:"):
                    texto_widgets.append(ft.Divider(height=20, color="#E0E0E0"))
                    texto_widgets.append(
                        ft.Text(
                            "Ingredientes",
                            size=24,
                            color="#4CAF50",
                            weight=ft.FontWeight.BOLD
                        )
                    )
                    texto_widgets.append(ft.Container(height=10))
                    
                elif linha_lower.startswith("preparo:"):
                    texto_widgets.append(ft.Container(height=10))
                    texto_widgets.append(ft.Divider(height=20, color="#E0E0E0"))
                    texto_widgets.append(
                        ft.Text(
                            "Modo de Preparo",
                            size=24,
                            color="#2196F3",
                            weight=ft.FontWeight.BOLD
                        )
                    )
                    texto_widgets.append(ft.Container(height=10))
                    
                elif "dica" in linha_lower and ("chef" in linha_lower or "bob" in linha_lower):
                    dica_texto = linha.split(":", 1)[1].strip() if ":" in linha else linha
                    texto_widgets.append(ft.Container(height=10))
                    texto_widgets.append(ft.Divider(height=20, color="#E0E0E0"))
                    texto_widgets.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "Dicas do Chef Bob Weed",
                                    size=22,
                                    color="#FF6B6B",
                                    weight=ft.FontWeight.BOLD
                                ),
                                ft.Container(height=8),
                                ft.Text(
                                    dica_texto,
                                    size=15,
                                    color="#000000",
                                    selectable=True
                                )
                            ]),
                            bgcolor="#FFF9E6",
                            padding=20,
                            border_radius=10,
                            border=ft.border.all(2, "#FFD54F")
                        )
                    )
                    
                elif linha.strip():
                    texto_widgets.append(
                        ft.Text(
                            linha,
                            size=15,
                            color="#000000",
                            selectable=True
                        )
                    )
                else:
                    texto_widgets.append(ft.Container(height=5))
            
            card = ft.Container(
                content=ft.Column(
                    controls=texto_widgets,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=5
                ),
                bgcolor="white",
                padding=35,
                border_radius=15,
                shadow=ft.BoxShadow(spread_radius=2, blur_radius=15, color="#00000015"),
                width=800,
                height=650
            )
            
            receita_container.controls.append(card)
            page.snack_bar = ft.SnackBar(content=ft.Text("Receita pronta!"), open=True)
            
        except Exception as erro:
            print(f"\n{erro}\n")
            import traceback
            traceback.print_exc()
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Erro: {erro}"), open=True)
        
        page.update()
    
    btn = ft.ElevatedButton(
        text="Gerar Receita com Chef Bob Weed",
        on_click=gerar_receita,
        bgcolor="#4CAF50",
        color="white",
        width=600,
        height=55
    )
    
    page.add(
        ft.Column([
            ft.Container(height=20),
            ft.Text("Larica Zero", size=42, weight=ft.FontWeight.BOLD, color="#2E7D32"),
            ft.Text("Com Chef Bob Weed", size=18, color="#FF6B35", text_align=ft.TextAlign.CENTER),
            ft.Text("Transforme sobras em receita!", size=18, color="#666"),
            ft.Container(height=20),
            ingredientes_input,
            ft.Container(height=15),
            btn,
            ft.Container(height=30),
            receita_container
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main)
