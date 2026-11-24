
import customtkinter as ctk
import json
import cv2
import shutil

from pathlib import Path
from tkinter import filedialog
from interface.janela_captura_facial import JanelaCapturaFacial
from interface.captura_facial import processar_foto_importada

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

        self.fotos_faciais = []
        self.janela_captura = None

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

        conteudo = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_fg_color="#CBD5E1",
            scrollbar_button_color="#94A3B8",
            scrollbar_button_hover_color="#64748B"
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

        ctk.CTkButton(
            area_facial,
            text="Importar fotos do dispositivo",
            height=42,
            font=("Arial", 14, "bold"),
            fg_color=AZUL_CLARO,
            hover_color="#456F9C",
            command=self.importar_fotos
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

        # 1. Validar os campos
        if not codigo or not nome or not apartamento:
            self.status_cadastro.configure(
                text="Preencha todos os campos do cadastro.",
                text_color=VERMELHO
            )
            return

        # 2. Verificar as fotos capturadas
        if not 5 <= len(self.fotos_faciais) <= 11:
            self.status_cadastro.configure(
                text="É necessário ter entre 5 e 11 fotos faciais.",
                text_color=VERMELHO
            )
            return

        # 3. Carregar os moradores existentes
        moradores = self.carregar_moradores()

        if not isinstance(moradores, list):
            self.status_cadastro.configure(
                text="Erro ao carregar os dados dos moradores.",
                text_color=VERMELHO
            )
            return

        # 4. Verificar código duplicado
        for morador in moradores:
            if morador["codigo"].casefold() == codigo.casefold():
                self.status_cadastro.configure(
                    text="Este código já está cadastrado.",
                    text_color=VERMELHO
                )
                return

        # 5. Gerar um ID facial automaticamente
        id_facial = self.gerar_id_facial()

        novo_morador = {
            "codigo": codigo,
            "nome": nome,
            "apartamento": apartamento,
            "id_facial": id_facial,
            "status_facial": "pendente_treinamento"
        }

        pasta_fotos = None

        try:
            # 6. Salvar as imagens faciais
            pasta_fotos = self.salvar_fotos_faciais(id_facial)

            # 7. Adicionar o morador à lista
            moradores.append(novo_morador)

            # 8. Salvar o JSON usando um arquivo temporário
            PASTA_DADOS.mkdir(parents=True, exist_ok=True)

            arquivo_temporario = ARQUIVO_MORADORES.with_suffix(
                ".json.tmp"
            )

            try:
                with open(
                        arquivo_temporario,
                        "w",
                        encoding="utf-8"
                ) as arquivo:
                    json.dump(
                        moradores,
                        arquivo,
                        ensure_ascii=False,
                        indent=4
                    )

                # Substitui o JSON somente após a gravação
                arquivo_temporario.replace(ARQUIVO_MORADORES)

            finally:
                arquivo_temporario.unlink(missing_ok=True)

        except (OSError, ValueError) as erro:

            # Desfaz o salvamento das fotos caso o cadastro falhe
            if pasta_fotos is not None and pasta_fotos.exists():
                shutil.rmtree(pasta_fotos)

            self.status_cadastro.configure(
                text=f"Erro ao salvar cadastro: {erro}",
                text_color=VERMELHO
            )
            return

        # 9. Confirmar o cadastro
        self.status_cadastro.configure(
            text=(
                f"Morador cadastrado! ID facial: {id_facial}. "
                "Aguardando treinamento."
            ),
            text_color=VERDE
        )

        # 10. Limpar os campos
        self.campo_codigo.delete(0, "end")
        self.campo_nome.delete(0, "end")
        self.campo_apartamento.delete(0, "end")

        self.fotos_faciais = []

        self.status_captura.configure(
            text="Nenhuma imagem capturada",
            text_color=CINZA
        )

        # CRIAR MORADOR

        novo_morador = {
            "codigo": codigo,
            "nome": nome,
            "apartamento": apartamento
        }

        moradores.append(novo_morador)

        # SALVAR JSON

    # Limpar os campos após salvar
        self.campo_codigo.delete(0, "end")
        self.campo_nome.delete(0, "end")
        self.campo_apartamento.delete(0, "end")

        self.fotos_faciais = []

        self.status_captura.configure(
            text="Nenhuma imagem capturada",
            text_color=CINZA
    )

    # ======================================
    # AÇÕES
    # ======================================

    def voltar(self):

        if self.voltar_callback:
            self.voltar_callback()

    def capturar_imagens(self):
        # Evita abrir duas janelas de captura
        if (
                self.janela_captura is not None
                and self.janela_captura.winfo_exists()
        ):
            self.janela_captura.focus()
            return

        self.status_captura.configure(
            text="Iniciando captura facial...",
            text_color=AZUL_CLARO
        )

        self.janela_captura = JanelaCapturaFacial(
            self,
            ao_concluir=self.receber_fotos
        )

    def importar_fotos(self):

        caminhos = filedialog.askopenfilenames(
            title="Selecionar fotos do morador",
            filetypes=[
                ("Imagens", "*.jpg *.jpeg *.png"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if not caminhos:
            return

        if not 5 <= len(caminhos) <= 11:
            self.status_captura.configure(
                text="Selecione entre 5 e 11 fotos.",
                text_color=VERMELHO
            )
            return


        try:
            # Localiza os arquivos do detector SSD
            pasta_modelos = (
                    Path(__file__).resolve().parents[1]
                    / "Modelos"
            )

            arquivo_prototxt = (
                    pasta_modelos / "deploy.prototxt.txt"
            )

            arquivo_modelo = (
                    pasta_modelos
                    / "res10_300x300_ssd_iter_140000.caffemodel"
            )

            detector = cv2.dnn.readNetFromCaffe(
                str(arquivo_prototxt),
                str(arquivo_modelo)
            )

            fotos_processadas = []

            for indice, caminho in enumerate(caminhos, start=1):
                foto = processar_foto_importada(
                    caminho,
                    detector
                )

                fotos_processadas.append(foto)

            # Só substitui as fotos anteriores se todas forem válidas
            self.fotos_faciais = fotos_processadas

            self.status_captura.configure(
                text=f"{len(fotos_processadas)} fotos importadas e processadas!",
                text_color=VERDE
            )

        except (ValueError, cv2.error, OSError) as erro:
            self.status_captura.configure(
                text=f"Erro ao importar fotos: {erro}",
                text_color=VERMELHO
            )

    def receber_fotos(self, fotos):
        self.fotos_faciais = fotos
        self.janela_captura = None

        self.status_captura.configure(
            text=f"{len(fotos)} imagens faciais capturadas!",
            text_color=VERDE
        )


    def salvar_fotos_faciais(self, id_facial):
        # Pasta exclusiva do dataset dos moradores
        pasta_dataset = (
            Path(__file__).resolve().parents[1]
            / "dataset_moradores"
        )

        pasta_morador = pasta_dataset / str(id_facial)

        # Evita sobrescrever imagens existentes
        if pasta_morador.exists():
            raise FileExistsError(
                f"O ID facial {id_facial} já possui imagens."
            )

        pasta_morador.mkdir(parents=True)

        try:
            for indice, foto in enumerate(
                self.fotos_faciais, start=1
            ):
                caminho = pasta_morador / f"foto_{indice:02d}.jpg"

                sucesso = cv2.imwrite(str(caminho), foto)

                if not sucesso:
                    raise OSError(
                        f"Não foi possível salvar {caminho.name}"
                    )

        except Exception:
            # Remove arquivos parciais caso alguma foto falhe
            import shutil
            shutil.rmtree(pasta_morador)
            raise

        return pasta_morador

    def gerar_id_facial(self):
        pasta_dataset = (
                Path(__file__).resolve().parents[1]
                / "dataset_moradores"
        )

        pasta_dataset.mkdir(parents=True, exist_ok=True)

        ids_existentes = []

        for pasta in pasta_dataset.iterdir():
            if pasta.is_dir() and pasta.name.isdigit():
                ids_existentes.append(int(pasta.name))

        if not ids_existentes:
            return 1

        return max(ids_existentes) + 1

    #salvar_fotos_faciais()
    #gerar_id_facial()
