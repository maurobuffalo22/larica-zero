# src/main.py
import flet as ft

def main(page: ft.Page):
    # Configura o título da janela
    page.title = "Larica Zero"
    
    # Adiciona um texto simples na página
    page.add(
        ft.Text("Olá! Bem-vindo ao Larica Zero! 🍳")
    )

# Inicia o aplicativo
ft.app(target=main)
