
import customtkinter as ctk
import json
from pathlib import Path
from tkinter import messagebox


# ==========================================
# CORES
# ==========================================

AZUL_ESCURO = "#172B45"
AZUL_CLARO = "#365B82"
FUNDO = "#F5F7FA"
BRANCO = "#FFFFFF"
CINZA = "#64748B"
VERDE = "#15803D"


# ==========================================
# ARQUIVO DE DADOS
# ==========================================

PASTA_DADOS = Path(__file__).resolve().parents[1] / "dados"
ARQUIVO_MORADORES = PASTA_DADOS / "moradores.json"


class TelaMoradores(ctk.CTkFrame):

    def __init__(self, master, voltar_callback=None):

        super().__init__(master, fg_color=FUNDO)

        self.voltar_callback = voltar_callback

        self.pack(fill="both", expand=True)

        self.criar_cabecalho()
        self.criar_conteudo()
        self.carregar_moradores()

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

        ctk.CTkLabel(
            cabecalho,
            text="◉  FaceGate",
            font=("Arial", 25, "bold"),
            text_color=BRANCO
        ).pack(side="left", padx=30)

        ctk.CTkButton(
            cabecalho,
            text="Voltar",
            width=90,
            fg_color=AZUL_CLARO,
            hover_color="#456F9C",
            command=self.voltar
        ).pack(side="right", padx=30)

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

        ctk.CTkLabel(
            conteudo,
            text="Moradores cadastrados",
            font=("Arial", 28, "bold"),
            text_color=AZUL_ESCURO
        ).pack(anchor="w")

        ctk.CTkLabel(
            conteudo,
            text="Consulte e edite os moradores registrados no condomínio.",
            font=("Arial", 13),
            text_color=CINZA
        ).pack(anchor="w", pady=(5, 20))

        self.contador = ctk.CTkLabel(
            conteudo,
            text="Total de moradores: 0",
            font=("Arial", 13, "bold"),
            text_color=AZUL_ESCURO
        )

        self.contador.pack(anchor="w", pady=(0, 12))

        self.lista = ctk.CTkScrollableFrame(
            conteudo,
            fg_color="transparent",
            corner_radius=0
        )

        self.lista.pack(
            fill="both",
            expand=True
        )

    # ======================================
    # CARREGAR MORADORES
    # ======================================

    def carregar_moradores(self):

        for widget in self.lista.winfo_children():
            widget.destroy()

        if not ARQUIVO_MORADORES.exists():
            moradores = []

        else:

            try:

                with open(
                    ARQUIVO_MORADORES,
                    "r",
                    encoding="utf-8"
                ) as arquivo:

                    moradores = json.load(arquivo)

                if not isinstance(moradores, list):
                    raise ValueError("Formato inválido.")

            except (json.JSONDecodeError, OSError, ValueError):

                self.contador.configure(
                    text="Não foi possível carregar os moradores."
                )

                return

        self.contador.configure(
            text=f"Total de moradores: {len(moradores)}"
        )

        if not moradores:

            ctk.CTkLabel(
                self.lista,
                text="Nenhum morador cadastrado.",
                font=("Arial", 14),
                text_color=CINZA
            ).pack(pady=30)

            return

        for morador in moradores:

            cartao = ctk.CTkFrame(
                self.lista,
                fg_color=BRANCO,
                corner_radius=12,
                border_width=1,
                border_color="#E2E8F0"
            )

            cartao.pack(
                fill="x",
                pady=7,
                padx=5
            )

            ctk.CTkLabel(
                cartao,
                text=morador.get("nome", "Nome não informado"),
                font=("Arial", 17, "bold"),
                text_color=AZUL_ESCURO
            ).pack(
                anchor="w",
                padx=20,
                pady=(15, 5)
            )

            ctk.CTkLabel(
                cartao,
                text=f"Código: {morador.get('codigo', 'Não informado')}",
                font=("Arial", 12),
                text_color=CINZA
            ).pack(
                anchor="w",
                padx=20,
                pady=3
            )

            ctk.CTkLabel(
                cartao,
                text=f"Unidade: {morador.get('apartamento', 'Não informada')}",
                font=("Arial", 12),
                text_color=CINZA
            ).pack(
                anchor="w",
                padx=20,
                pady=3
            )

            ctk.CTkButton(
                cartao,
                text="Editar morador",
                width=140,
                height=35,
                fg_color=AZUL_CLARO,
                hover_color="#456F9C",
                command=lambda dados=morador: self.abrir_edicao(dados)
            ).pack(
                anchor="e",
                padx=20,
                pady=(8, 15)
            )

    # ======================================
    # ABRIR JANELA DE EDIÇÃO
    # ======================================

    def abrir_edicao(self, morador):

        janela = ctk.CTkToplevel(self)

        janela.title("Editar morador")
        janela.geometry("450x480")
        janela.resizable(False, False)
        janela.configure(fg_color=FUNDO)

        janela.transient(self.winfo_toplevel())
        janela.grab_set()

        ctk.CTkLabel(
            janela,
            text="Editar morador",
            font=("Arial", 25, "bold"),
            text_color=AZUL_ESCURO
        ).pack(pady=(30, 10))

        ctk.CTkLabel(
            janela,
            text="Altere as informações do morador abaixo.",
            font=("Arial", 12),
            text_color=CINZA
        ).pack(pady=(0, 20))

        # CAMPO NOME

        ctk.CTkLabel(
            janela,
            text="Nome completo",
            font=("Arial", 13, "bold"),
            text_color=AZUL_ESCURO
        ).pack(anchor="w", padx=45)

        campo_nome = ctk.CTkEntry(
            janela,
            width=360,
            height=40,
            placeholder_text="Nome completo"
        )

        campo_nome.pack(pady=(5, 15))
        campo_nome.insert(0, morador.get("nome", ""))

        # CAMPO CÓDIGO

        ctk.CTkLabel(
            janela,
            text="Código do morador",
            font=("Arial", 13, "bold"),
            text_color=AZUL_ESCURO
        ).pack(anchor="w", padx=45)

        campo_codigo = ctk.CTkEntry(
            janela,
            width=360,
            height=40,
            placeholder_text="Código"
        )

        campo_codigo.pack(pady=(5, 15))
        campo_codigo.insert(0, morador.get("codigo", ""))

        # CAMPO APARTAMENTO

        ctk.CTkLabel(
            janela,
            text="Apartamento / Unidade",
            font=("Arial", 13, "bold"),
            text_color=AZUL_ESCURO
        ).pack(anchor="w", padx=45)

        campo_apartamento = ctk.CTkEntry(
            janela,
            width=360,
            height=40,
            placeholder_text="Exemplo: Apartamento 101"
        )

        campo_apartamento.pack(pady=(5, 20))
        campo_apartamento.insert(0, morador.get("apartamento", ""))

        # BOTÃO SALVAR

        ctk.CTkButton(
            janela,
            text="Salvar alterações",
            width=360,
            height=45,
            font=("Arial", 14, "bold"),
            fg_color=AZUL_ESCURO,
            hover_color=AZUL_CLARO,
            command=lambda: self.salvar_edicao(
                janela,
                morador,
                campo_nome.get(),
                campo_codigo.get(),
                campo_apartamento.get()
            )
        ).pack(pady=10)

    # ======================================
    # SALVAR EDIÇÃO
    # ======================================

    def salvar_edicao(
        self,
        janela,
        morador,
        novo_nome,
        novo_codigo,
        novo_apartamento
    ):

        novo_nome = novo_nome.strip()
        novo_codigo = novo_codigo.strip()
        novo_apartamento = novo_apartamento.strip()

        if not novo_nome or not novo_codigo or not novo_apartamento:

            messagebox.showwarning(
                "Campos obrigatórios",
                "Preencha todos os campos antes de salvar.",
                parent=janela
            )

            return

        try:

            with open(
                ARQUIVO_MORADORES,
                "r",
                encoding="utf-8"
            ) as arquivo:

                moradores = json.load(arquivo)

            # VERIFICAR CÓDIGO DUPLICADO

            for outro_morador in moradores:

                mesmo_morador = (
                    outro_morador.get("codigo") == morador.get("codigo")
                )

                mesmo_codigo = (
                    outro_morador.get("codigo", "").casefold()
                    == novo_codigo.casefold()
                )

                if not mesmo_morador and mesmo_codigo:

                    messagebox.showwarning(
                        "Código já cadastrado",
                        "Esse código já pertence a outro morador.",
                        parent=janela
                    )

                    return

            # ATUALIZAR DADOS

            for outro_morador in moradores:

                if outro_morador.get("codigo") == morador.get("codigo"):

                    outro_morador["nome"] = novo_nome
                    outro_morador["codigo"] = novo_codigo
                    outro_morador["apartamento"] = novo_apartamento

                    break

            # SALVAR NO JSON

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

            messagebox.showinfo(
                "Sucesso",
                "Dados do morador atualizados com sucesso!",
                parent=janela
            )

            janela.destroy()

            self.carregar_moradores()

        except (json.JSONDecodeError, OSError):

            messagebox.showerror(
                "Erro",
                "Não foi possível salvar as alterações.",
                parent=janela
            )

    # ======================================
    # VOLTAR
    # ======================================

    def voltar(self):

        if self.voltar_callback:
            self.voltar_callback()

import customtkinter as ctk
import json
from pathlib import Path
from tkinter import messagebox


# ==========================================
# CORES
# ==========================================

AZUL_ESCURO = "#172B45"
AZUL_CLARO = "#365B82"
FUNDO = "#F5F7FA"
BRANCO = "#FFFFFF"
CINZA = "#64748B"
VERMELHO = "#B91C1C"


# ==========================================
# ARQUIVO DE DADOS
# ==========================================

PASTA_DADOS = Path(__file__).resolve().parents[1] / "dados"
ARQUIVO_MORADORES = PASTA_DADOS / "moradores.json"


class TelaMoradores(ctk.CTkFrame):

    def __init__(self, master, voltar_callback=None):

        super().__init__(master, fg_color=FUNDO)

        self.voltar_callback = voltar_callback

        self.pack(fill="both", expand=True)

        self.criar_cabecalho()
        self.criar_conteudo()
        self.carregar_moradores()

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

        ctk.CTkLabel(
            cabecalho,
            text="◉  FaceGate",
            font=("Arial", 25, "bold"),
            text_color=BRANCO
        ).pack(side="left", padx=30)

        ctk.CTkButton(
            cabecalho,
            text="Voltar",
            width=90,
            fg_color=AZUL_CLARO,
            hover_color="#456F9C",
            command=self.voltar
        ).pack(side="right", padx=30)

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

        ctk.CTkLabel(
            conteudo,
            text="Moradores cadastrados",
            font=("Arial", 28, "bold"),
            text_color=AZUL_ESCURO
        ).pack(anchor="w")

        ctk.CTkLabel(
            conteudo,
            text="Consulte e edite os moradores registrados no condomínio.",
            font=("Arial", 13),
            text_color=CINZA
        ).pack(anchor="w", pady=(5, 20))

        self.contador = ctk.CTkLabel(
            conteudo,
            text="Total de moradores: 0",
            font=("Arial", 13, "bold"),
            text_color=AZUL_ESCURO
        )

        self.contador.pack(anchor="w", pady=(0, 12))

        self.lista = ctk.CTkScrollableFrame(
            conteudo,
            fg_color="transparent",
            corner_radius=0
        )

        self.lista.pack(
            fill="both",
            expand=True
        )

    # ======================================
    # CARREGAR MORADORES
    # ======================================

    def carregar_moradores(self):

        for widget in self.lista.winfo_children():
            widget.destroy()

        if not ARQUIVO_MORADORES.exists():
            moradores = []

        else:

            try:

                with open(
                    ARQUIVO_MORADORES,
                    "r",
                    encoding="utf-8"
                ) as arquivo:

                    moradores = json.load(arquivo)

                if not isinstance(moradores, list):
                    raise ValueError("Formato inválido.")

            except (json.JSONDecodeError, OSError, ValueError):

                self.contador.configure(
                    text="Não foi possível carregar os moradores."
                )

                return

        self.contador.configure(
            text=f"Total de moradores: {len(moradores)}"
        )

        if not moradores:

            ctk.CTkLabel(
                self.lista,
                text="Nenhum morador cadastrado.",
                font=("Arial", 14),
                text_color=CINZA
            ).pack(pady=30)

            return

        for morador in moradores:

            cartao = ctk.CTkFrame(
                self.lista,
                fg_color=BRANCO,
                corner_radius=12,
                border_width=1,
                border_color="#E2E8F0"
            )

            cartao.pack(
                fill="x",
                pady=7,
                padx=5
            )

            ctk.CTkLabel(
                cartao,
                text=morador.get("nome", "Nome não informado"),
                font=("Arial", 17, "bold"),
                text_color=AZUL_ESCURO
            ).pack(
                anchor="w",
                padx=20,
                pady=(15, 5)
            )

            ctk.CTkLabel(
                cartao,
                text=f"Código: {morador.get('codigo', 'Não informado')}",
                font=("Arial", 12),
                text_color=CINZA
            ).pack(
                anchor="w",
                padx=20,
                pady=3
            )

            ctk.CTkLabel(
                cartao,
                text=f"Unidade: {morador.get('apartamento', 'Não informada')}",
                font=("Arial", 12),
                text_color=CINZA
            ).pack(
                anchor="w",
                padx=20,
                pady=3
            )

            # ÁREA DOS BOTÕES

            area_botoes = ctk.CTkFrame(
                cartao,
                fg_color="transparent"
            )

            area_botoes.pack(
                anchor="e",
                padx=20,
                pady=(8, 15)
            )

            # BOTÃO EDITAR

            ctk.CTkButton(
                area_botoes,
                text="Editar",
                width=110,
                height=35,
                fg_color=AZUL_CLARO,
                hover_color="#456F9C",
                command=lambda dados=morador: self.abrir_edicao(dados)
            ).pack(side="left", padx=(0, 8))

            # BOTÃO EXCLUIR

            ctk.CTkButton(
                area_botoes,
                text="Excluir",
                width=110,
                height=35,
                fg_color=VERMELHO,
                hover_color="#991B1B",
                command=lambda codigo=morador.get("codigo"): self.excluir_morador(codigo)
            ).pack(side="left")

    # ======================================
    # ABRIR JANELA DE EDIÇÃO
    # ======================================

    def abrir_edicao(self, morador):

        janela = ctk.CTkToplevel(self)

        janela.title("Editar morador")
        janela.geometry("450x480")
        janela.resizable(False, False)
        janela.configure(fg_color=FUNDO)

        janela.transient(self.winfo_toplevel())
        janela.grab_set()

        ctk.CTkLabel(
            janela,
            text="Editar morador",
            font=("Arial", 25, "bold"),
            text_color=AZUL_ESCURO
        ).pack(pady=(30, 10))

        ctk.CTkLabel(
            janela,
            text="Altere as informações do morador abaixo.",
            font=("Arial", 12),
            text_color=CINZA
        ).pack(pady=(0, 20))

        # CAMPO NOME

        ctk.CTkLabel(
            janela,
            text="Nome completo",
            font=("Arial", 13, "bold"),
            text_color=AZUL_ESCURO
        ).pack(anchor="w", padx=45)

        campo_nome = ctk.CTkEntry(
            janela,
            width=360,
            height=40,
            placeholder_text="Nome completo"
        )

        campo_nome.pack(pady=(5, 15))
        campo_nome.insert(0, morador.get("nome", ""))

        # CAMPO CÓDIGO

        ctk.CTkLabel(
            janela,
            text="Código do morador",
            font=("Arial", 13, "bold"),
            text_color=AZUL_ESCURO
        ).pack(anchor="w", padx=45)

        campo_codigo = ctk.CTkEntry(
            janela,
            width=360,
            height=40,
            placeholder_text="Código"
        )

        campo_codigo.pack(pady=(5, 15))
        campo_codigo.insert(0, morador.get("codigo", ""))

        # CAMPO APARTAMENTO

        ctk.CTkLabel(
            janela,
            text="Apartamento / Unidade",
            font=("Arial", 13, "bold"),
            text_color=AZUL_ESCURO
        ).pack(anchor="w", padx=45)

        campo_apartamento = ctk.CTkEntry(
            janela,
            width=360,
            height=40,
            placeholder_text="Exemplo: Apartamento 101"
        )

        campo_apartamento.pack(pady=(5, 20))
        campo_apartamento.insert(0, morador.get("apartamento", ""))

        # BOTÃO SALVAR

        ctk.CTkButton(
            janela,
            text="Salvar alterações",
            width=360,
            height=45,
            font=("Arial", 14, "bold"),
            fg_color=AZUL_ESCURO,
            hover_color=AZUL_CLARO,
            command=lambda: self.salvar_edicao(
                janela,
                morador,
                campo_nome.get(),
                campo_codigo.get(),
                campo_apartamento.get()
            )
        ).pack(pady=10)

    # ======================================
    # SALVAR EDIÇÃO
    # ======================================

    def salvar_edicao(
        self,
        janela,
        morador,
        novo_nome,
        novo_codigo,
        novo_apartamento
    ):

        novo_nome = novo_nome.strip()
        novo_codigo = novo_codigo.strip()
        novo_apartamento = novo_apartamento.strip()

        if not novo_nome or not novo_codigo or not novo_apartamento:

            messagebox.showwarning(
                "Campos obrigatórios",
                "Preencha todos os campos antes de salvar.",
                parent=janela
            )

            return

        try:

            with open(
                ARQUIVO_MORADORES,
                "r",
                encoding="utf-8"
            ) as arquivo:

                moradores = json.load(arquivo)

            if not isinstance(moradores, list):
                raise ValueError("Formato inválido.")

            # VERIFICAR CÓDIGO DUPLICADO

            for outro_morador in moradores:

                mesmo_morador = (
                    outro_morador.get("codigo") == morador.get("codigo")
                )

                mesmo_codigo = (
                    outro_morador.get("codigo", "").casefold()
                    == novo_codigo.casefold()
                )

                if not mesmo_morador and mesmo_codigo:

                    messagebox.showwarning(
                        "Código já cadastrado",
                        "Esse código já pertence a outro morador.",
                        parent=janela
                    )

                    return

            # ATUALIZAR DADOS

            encontrado = False

            for outro_morador in moradores:

                if outro_morador.get("codigo") == morador.get("codigo"):

                    outro_morador["nome"] = novo_nome
                    outro_morador["codigo"] = novo_codigo
                    outro_morador["apartamento"] = novo_apartamento

                    encontrado = True
                    break

            if not encontrado:

                messagebox.showerror(
                    "Erro",
                    "Morador não encontrado no arquivo.",
                    parent=janela
                )

                return

            # SALVAR NO JSON

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

            messagebox.showinfo(
                "Sucesso",
                "Dados do morador atualizados com sucesso!",
                parent=janela
            )

            janela.destroy()

            self.carregar_moradores()

        except (json.JSONDecodeError, OSError, ValueError):

            messagebox.showerror(
                "Erro",
                "Não foi possível salvar as alterações.",
                parent=janela
            )

    # ======================================
    # EXCLUIR MORADOR
    # ======================================

    def excluir_morador(self, codigo):

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            "Tem certeza de que deseja excluir este morador?",
            parent=self.winfo_toplevel()
        )

        if not confirmar:
            return

        try:

            with open(
                ARQUIVO_MORADORES,
                "r",
                encoding="utf-8"
            ) as arquivo:

                moradores = json.load(arquivo)

            if not isinstance(moradores, list):
                raise ValueError("Formato inválido.")

            # REMOVER MORADOR

            moradores_atualizados = [
                morador for morador in moradores
                if morador.get("codigo") != codigo
            ]

            if len(moradores_atualizados) == len(moradores):

                messagebox.showwarning(
                    "Aviso",
                    "Morador não encontrado."
                )

                return

            # ATUALIZAR ARQUIVO JSON

            with open(
                ARQUIVO_MORADORES,
                "w",
                encoding="utf-8"
            ) as arquivo:

                json.dump(
                    moradores_atualizados,
                    arquivo,
                    ensure_ascii=False,
                    indent=4
                )

            messagebox.showinfo(
                "Sucesso",
                "Morador excluído com sucesso!"
            )

            self.carregar_moradores()

        except (json.JSONDecodeError, OSError, ValueError):

            messagebox.showerror(
                "Erro",
                "Não foi possível excluir o morador."
            )

    # ======================================
    # VOLTAR
    # ======================================

    def voltar(self):

        if self.voltar_callback:
            self.voltar_callback()
