
import customtkinter as ctk
import json
from pathlib import Path


# ==========================================
# CORES DO FACEGATE
# ==========================================

AZUL_ESCURO = "#172B45"
AZUL_CLARO = "#365B82"
FUNDO = "#F5F7FA"
BRANCO = "#FFFFFF"
CINZA = "#64748B"
VERDE = "#16803C"
VERMELHO = "#DC2626"


# ==========================================
# ARQUIVO DE DADOS
# ==========================================

PASTA_DADOS = Path(__file__).resolve().parents[1] / "dados"
ARQUIVO_MORADORES = PASTA_DADOS / "moradores.json"


class TelaCadastro(ctk.CTkFrame):

    def __init__(self, master, voltar_callback=None):
        super().__init__(master, fg_color=FUNDO)

        self.voltar_callback = voltar_callback

        self.pack(fill="both", expand=True)

        self.criar_cabecalho()
        self.criar_conteudo()

    # ======================================
    # CABEÇALHO
    # ======================================

    def criar_cabecalho(self):

        cabecalho = ctk.CTkFrame(
            self,
            fg_color=AZUL_ESCURO,
            corner_radius=0,
            height=75
        )

        cabecalho.pack(fill="x")
        cabecalho.pack_propagate(False)

        titulo = ctk.CTkLabel(
            cabecalho,
            text="◉  FaceGate",
            font=("Arial", 25, "bold"),
            text_color=BRANCO
        )

        titulo.pack(side="left", padx=30)

        botao_voltar = ctk.CTkButton(
            cabecalho,
            text="Voltar",
            width=90,
            fg_color=AZUL_CLARO,
            hover_color="#456F9C",
            command=self.voltar
        )

        botao_voltar.pack(side="right", padx=30)

    # ======================================
    # CONTEÚDO
    # ======================================

    def criar_conteudo(self):

        conteudo = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        conteudo.pack(
            fill="both",
            expand=True,
            padx=45,
            pady=30
        )

        titulo = ctk.CTkLabel(
            conteudo,
            text="Cadastro de morador",
            font=("Arial", 28, "bold"),
            text_color=AZUL_ESCURO
        )

        titulo.pack(anchor="w")

        subtitulo = ctk.CTkLabel(
            conteudo,
            text="Cadastre os dados do residente do condomínio.",
            font=("Arial", 13),
            text_color=CINZA
        )

        subtitulo.pack(anchor="w", pady=(5, 25))

        # ==================================
        # CÓDIGO DO MORADOR
        # ==================================

        ctk.CTkLabel(
            conteudo,
            text="Código do morador",
            font=("Arial", 13, "bold"),
            text_color=AZUL_ESCURO
        ).pack(anchor="w")

        self.campo_codigo = ctk.CTkEntry(
            conteudo,
            placeholder_text="Ex.: MOR001",
            height=42,
            corner_radius=8
        )

        self.campo_codigo.pack(fill="x", pady=(7, 18))

        # ==================================
        # NOME COMPLETO
        # ==================================

        ctk.CTkLabel(
            conteudo,
            text="Nome completo",
            font=("Arial", 13, "bold"),
            text_color=AZUL_ESCURO
        ).pack(anchor="w")

        self.campo_nome = ctk.CTkEntry(
            conteudo,
            placeholder_text="Digite o nome completo do morador",
            height=42,
            corner_radius=8
        )

        self.campo_nome.pack(fill="x", pady=(7, 18))

        # ==================================
        # APARTAMENTO
        # ==================================

        ctk.CTkLabel(
            conteudo,
            text="Apartamento / Unidade",
            font=("Arial", 13, "bold"),
            text_color=AZUL_ESCURO
        ).pack(anchor="w")

        self.campo_apartamento = ctk.CTkEntry(
            conteudo,
            placeholder_text="Ex.: Bloco A - Apartamento 102",
            height=42,
            corner_radius=8
        )

        self.campo_apartamento.pack(fill="x", pady=(7, 22))

        # ==================================
        # CADASTRO FACIAL
        # ==================================

        area_facial = ctk.CTkFrame(
            conteudo,
            fg_color=BRANCO,
            corner_radius=12,
            border_width=1,
            border_color="#E2E8F0"
        )

        area_facial.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            area_facial,
            text="Cadastro facial",
            font=("Arial", 17, "bold"),
            text_color=AZUL_ESCURO
        ).pack(anchor="w", padx=20, pady=(18, 8))

        ctk.CTkLabel(
            area_facial,
            text="As imagens serão utilizadas para cadastrar o rosto do morador no sistema de reconhecimento facial.",
            font=("Arial", 12),
            text_color=CINZA,
            wraplength=650
        ).pack(anchor="w", padx=20)

        self.status_captura = ctk.CTkLabel(
            area_facial,
            text="Nenhuma imagem capturada",
            font=("Arial", 12),
            text_color=CINZA
        )

        self.status_captura.pack(anchor="w", padx=20, pady=15)

        ctk.CTkButton(
            area_facial,
            text="Abrir câmera para captura",
            height=42,
            fg_color=AZUL_ESCURO,
            hover_color=AZUL_CLARO,
            command=self.capturar_imagens
        ).pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        # ==================================
        # STATUS DO CADASTRO
        # ==================================

        self.status_cadastro = ctk.CTkLabel(
            conteudo,
            text="",
            font=("Arial", 12),
            text_color=CINZA
        )

        self.status_cadastro.pack(pady=(0, 8))

        # ==================================
        # BOTÃO SALVAR
        # ==================================

        ctk.CTkButton(
            conteudo,
            text="Salvar cadastro",
            height=45,
            font=("Arial", 14, "bold"),
            fg_color=AZUL_ESCURO,
            hover_color=AZUL_CLARO,
            command=self.salvar_cadastro
        ).pack(fill="x", pady=(5, 0))

    # ======================================
    # CARREGAR MORADORES
    # ======================================

    def carregar_moradores(self):

        PASTA_DADOS.mkdir(parents=True, exist_ok=True)

        if not ARQUIVO_MORADORES.exists():
            return []

        try:

            with open(
                ARQUIVO_MORADORES,
                "r",
                encoding="utf-8"
            ) as arquivo:

                return json.load(arquivo)

        except (json.JSONDecodeError, OSError):

            return None

    # ======================================
    # SALVAR CADASTRO
    # ======================================

    def salvar_cadastro(self):

        codigo = self.campo_codigo.get().strip()
        nome = self.campo_nome.get().strip()
        apartamento = self.campo_apartamento.get().strip()

        # VALIDAR CAMPOS

        if not codigo or not nome or not apartamento:

            self.status_cadastro.configure(
                text="Preencha todos os campos do cadastro.",
                text_color=VERMELHO
            )

            return

        moradores = self.carregar_moradores()

        if moradores is None:

            self.status_cadastro.configure(
                text="Erro ao carregar os dados dos moradores.",
                text_color=VERMELHO
            )

            return

        # VERIFICAR CÓDIGO DUPLICADO

        for morador in moradores:

            if morador["codigo"].casefold() == codigo.casefold():

                self.status_cadastro.configure(
                    text="Este código já está cadastrado.",
                    text_color=VERMELHO
                )

                return

        # CRIAR MORADOR

        novo_morador = {
            "codigo": codigo,
            "nome": nome,
            "apartamento": apartamento
        }

        moradores.append(novo_morador)

        # SALVAR JSON

        try:

            PASTA_DADOS.mkdir(parents=True, exist_ok=True)

            with open(
                ARQUIVO_MORADORES,
                "w",
                encoding="utf-8"
            ) as arquivo:

                json.dump(
                    moradores,
                    arquivo,
                    ensure_ascii=False,
                    indent=4
                )

            self.status_cadastro.configure(
                text="Morador cadastrado com sucesso!",
                text_color=VERDE
            )

            self.campo_codigo.delete(0, "end")
            self.campo_nome.delete(0, "end")
            self.campo_apartamento.delete(0, "end")

        except OSError:

            self.status_cadastro.configure(
                text="Não foi possível salvar o cadastro.",
                text_color=VERMELHO
            )

    # ======================================
    # AÇÕES
    # ======================================

    def voltar(self):

        if self.voltar_callback:
            self.voltar_callback()

    def capturar_imagens(self):

        self.status_captura.configure(
            text="Captura facial ainda não conectada.",
            text_color=AZUL_CLARO
        )
