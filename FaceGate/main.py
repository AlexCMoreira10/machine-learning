
import customtkinter as ctk

from interface.tela_cadastro import TelaCadastro
from interface.tela_moradores import TelaMoradores


# ==========================================
# CONFIGURAÇÕES
# ==========================================

AZUL_ESCURO = "#172B45"
AZUL_CLARO = "#365B82"
FUNDO = "#F5F7FA"
BRANCO = "#FFFFFF"
CINZA = "#64748B"


# ==========================================
# JANELA PRINCIPAL
# ==========================================

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()

app.title("FaceGate - Sistema de Acesso")
app.geometry("1000x700")
app.minsize(800, 600)

app.configure(fg_color=FUNDO)


# ==========================================
# LIMPAR TELA
# ==========================================

def limpar_tela():

    for widget in app.winfo_children():
        widget.destroy()


# ==========================================
# TELA INICIAL
# ==========================================

def mostrar_inicio():

    limpar_tela()

    cabecalho = ctk.CTkFrame(
        app,
        fg_color=AZUL_ESCURO,
        corner_radius=0,
        height=85
    )

    cabecalho.pack(fill="x")
    cabecalho.pack_propagate(False)

    ctk.CTkLabel(
        cabecalho,
        text="◉  FaceGate",
        font=("Arial", 28, "bold"),
        text_color=BRANCO
    ).pack(side="left", padx=35)

    ctk.CTkLabel(
        app,
        text="Sistema de reconhecimento facial e controle de acesso",
        font=("Arial", 19, "bold"),
        text_color=AZUL_ESCURO
    ).pack(pady=(55, 10))

    ctk.CTkLabel(
        app,
        text="Bem-vindo ao sistema de gerenciamento de moradores.",
        font=("Arial", 13),
        text_color=CINZA
    ).pack(pady=(0, 35))

    area_botoes = ctk.CTkFrame(
        app,
        fg_color=BRANCO,
        corner_radius=15,
        border_width=1,
        border_color="#E2E8F0"
    )

    area_botoes.pack(
        padx=100,
        fill="x",
        pady=10
    )

    ctk.CTkButton(
        area_botoes,
        text="Cadastrar morador",
        height=50,
        font=("Arial", 15, "bold"),
        fg_color=AZUL_ESCURO,
        hover_color=AZUL_CLARO,
        command=mostrar_cadastro
    ).pack(fill="x", padx=35, pady=(30, 12))

    ctk.CTkButton(
        area_botoes,
        text="Moradores cadastrados",
        height=50,
        font=("Arial", 15, "bold"),
        fg_color=AZUL_CLARO,
        hover_color="#456F9C",
        command=mostrar_moradores
    ).pack(fill="x", padx=35, pady=12)

    ctk.CTkButton(
        area_botoes,
        text="Iniciar reconhecimento facial",
        height=50,
        font=("Arial", 15, "bold"),
        fg_color=AZUL_CLARO,
        hover_color="#456F9C",
        command=iniciar_reconhecimento
    ).pack(fill="x", padx=35, pady=12)

    ctk.CTkButton(
        area_botoes,
        text="Histórico de acessos",
        height=50,
        font=("Arial", 15, "bold"),
        fg_color="#64748B",
        hover_color="#475569",
        command=abrir_historico
    ).pack(fill="x", padx=35, pady=(12, 30))


# ==========================================
# ABRIR CADASTRO
# ==========================================

def mostrar_cadastro():

    limpar_tela()

    TelaCadastro(
        app,
        voltar_callback=mostrar_inicio
    )


# ==========================================
# LISTA DE MORADORES
# ==========================================

def mostrar_moradores():

    limpar_tela()

    TelaMoradores(
        app,
        voltar_callback=mostrar_inicio
    )


# ==========================================
# RECONHECIMENTO FACIAL
# ==========================================

def iniciar_reconhecimento():

    limpar_tela()

    ctk.CTkLabel(
        app,
        text="Reconhecimento facial",
        font=("Arial", 25, "bold"),
        text_color=AZUL_ESCURO
    ).pack(pady=50)

    ctk.CTkLabel(
        app,
        text="Esta função será conectada ao modelo facial posteriormente.",
        font=("Arial", 14),
        text_color=CINZA
    ).pack(pady=10)

    ctk.CTkButton(
        app,
        text="Voltar",
        command=mostrar_inicio
    ).pack(pady=30)


# ==========================================
# HISTÓRICO
# ==========================================

def abrir_historico():

    limpar_tela()

    ctk.CTkLabel(
        app,
        text="Histórico de acessos",
        font=("Arial", 25, "bold"),
        text_color=AZUL_ESCURO
    ).pack(pady=50)

    ctk.CTkLabel(
        app,
        text="O histórico será implementado posteriormente.",
        font=("Arial", 14),
        text_color=CINZA
    ).pack(pady=10)

    ctk.CTkButton(
        app,
        text="Voltar",
        command=mostrar_inicio
    ).pack(pady=30)


# ==========================================
# INICIAR SISTEMA
# ==========================================

mostrar_inicio()

app.mainloop()
