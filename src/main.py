# src/main.py
import flet as ft
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configura a API do Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def main(page: ft.Page):
    # Configurações da página
    page.title = "Larica Zero"
    page.padding = 20
    page.bgcolor = "#f5f5f5"
    page.scroll = "adaptive"
    
    # Campo de texto para ingredientes
    ingredientes_input = ft.TextField(
        label="Digite os ingredientes",
        hint_text="Ex: arroz, frango, cenoura",
        multiline=True,
        min_lines=3,
        max_lines=5,
        border_color="#4CAF50",
        width=500
    )
    
    # Container para exibir as receitas
    receitas_container = ft.Column()
    
        # Função que gera receitas com IA
    def gerar_receitas(e):
        print("=== BOTÃO CLICADO ===")  # DEBUG
        ingredientes = ingredientes_input.value
        print(f"Ingredientes capturados: '{ingredientes}'")  # DEBUG
        
        if not ingredientes or ingredientes.strip() == "":
            print("ERRO: Ingredientes vazios")  # DEBUG
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Por favor, digite alguns ingredientes!"),
                open=True
            )
            page.update()
            return
        
        # Mostra mensagem de carregamento
        print("Mostrando mensagem de carregamento...")  # DEBUG
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Gerando receitas... Aguarde! 🔄"),
            open=True
        )
        page.update()
        
        try:
            print("Tentando conectar com Gemini...")  # DEBUG
            
            # Testa se a chave foi carregada
            api_key = os.getenv("GEMINI_API_KEY")
            print(f"Chave API: {api_key[:20] if api_key else 'NENHUMA'}...")  # DEBUG
            
            # Cria o modelo de IA
            model = genai.GenerativeModel('gemini-2.5-flash')

            print("Modelo criado com sucesso")  # DEBUG
            
            # Prompt para a IA
            prompt = f"""
            Com base nos seguintes ingredientes: {ingredientes}
            
            Gere 3 receitas deliciosas e práticas. Para cada receita, forneça:
            
            1. Nome da receita
            2. Ingredientes necessários (incluindo os fornecidos)
            3. Modo de preparo (passo a passo simples)
            4. Tempo de preparo
            
            Formato de resposta:
            
            RECEITA 1:
            Nome: [nome]
            Ingredientes: [lista]
            Modo de preparo: [passos]
            Tempo: [tempo]
            
            RECEITA 2:
            ...
            
            RECEITA 3:
            ...
            """
            
            print("Enviando prompt para IA...")  # DEBUG
            # Gera as receitas
            response = model.generate_content(prompt)
            print("Resposta recebida!")  # DEBUG
            receitas_texto = response.text
            print(f"Texto gerado (primeiros 100 chars): {receitas_texto[:100]}")  # DEBUG
            
            # Limpa o container de receitas
            receitas_container.controls.clear()
            
            # Adiciona o texto das receitas
            receitas_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "🍳 Suas Receitas",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color="#2E7D32"
                        ),
                        ft.Divider(height=20),
                        ft.Text(
                            receitas_texto,
                            size=14,
                            selectable=True
                        )
                    ]),
                    bgcolor="white",
                    padding=20,
                    border_radius=10,
                    width=700
                )
            )
            
            print("Receitas adicionadas ao container")  # DEBUG
            
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Receitas geradas com sucesso! ✅"),
                open=True
            )
            
        except Exception as erro:
            print(f"ERRO CAPTURADO: {erro}")  # DEBUG
            import traceback
            traceback.print_exc()  # Mostra erro completo
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Erro ao gerar receitas: {str(erro)}"),
                open=True
            )
        
        print("Atualizando página...")  # DEBUG
        page.update()
        print("=== FIM ===")  # DEBUG

    
    # Botão para processar
    processar_btn = ft.ElevatedButton(
        text="Gerar Receitas 🍳",
        on_click=gerar_receitas,
        bgcolor="#4CAF50",
        color="white",
        width=500,
        height=50
    )
    
    # Layout organizado
    page.add(
        ft.Column(
            [
                ft.Text(
                    "🍽️ Larica Zero",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color="#2E7D32"
                ),
                ft.Text(
                    "Transforme sobras em receitas deliciosas!",
                    size=16,
                    color="#666666"
                ),
                ft.Divider(height=20, color="transparent"),
                ingredientes_input,
                ft.Divider(height=10, color="transparent"),
                processar_btn,
                ft.Divider(height=30, color="transparent"),
                receitas_container
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

# Inicia o aplicativo
ft.app(target=main)
