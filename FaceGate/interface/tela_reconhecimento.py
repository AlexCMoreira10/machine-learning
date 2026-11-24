import time
import math
import cv2
import customtkinter as ctk
#import pickle
import json
from PIL import Image
from pathlib import Path

# ==========================================
# CONFIGURAÇÕES DA VALIDAÇÃO FACIAL
# ==========================================

LIMITE_DISTANCIA = 2500.0
LEITURAS_NECESSARIAS = 10
TEMPO_MAXIMO_RECONHECIMENTO = 15


class TelaReconhecimento(ctk.CTkFrame):

    def reconhecer_rosto(self, imagem, x, y, w, h):

        # Recorta o rosto detectado pelo SSD
        rosto = imagem[y:y + h, x:x + w]

        if rosto.size == 0:
            return None, "Rosto inválido", None

        # Converte para escala de cinza
        rosto_cinza = cv2.cvtColor(
            rosto,
            cv2.COLOR_BGR2GRAY
        )

        # Mantém as dimensões do treinamento
        rosto_cinza = cv2.resize(
            rosto_cinza,
            (90, 120)
        )

        # Obtém o ID candidato e a distância
        id_previsto, distancia = self.reconhecedor.predict(
            rosto_cinza
        )

        print(
            f"ID candidato: {id_previsto} | "
            f"Distância Eigenfaces: {distancia:.2f}"
        )

        # Procura o nome do morador no cadastro
        nome = self.face_names.get(int(id_previsto))

        if nome is None:
            nome = f"ID {id_previsto} sem cadastro"

        return int(id_previsto), str(nome), float(distancia)

    def __init__(self, master, voltar_callback, acesso_callback=None):
        super().__init__(master, fg_color="#F5F7FA")

        self.voltar_callback = voltar_callback
        self.acesso_callback = acesso_callback
        self.camera = None
        self.atualizacao_id = None
        # Controle da validação facial
        self.id_candidato = None
        self.leituras_consecutivas = 0
        self.identidade_confirmada = False
        self.reconhecimento_finalizado = False
        self.inicio_reconhecimento = None

        self.pack(fill="both", expand=True)

        area_rolavel = ctk.CTkScrollableFrame(
            self,
            fg_color="#F5F7FA",
            corner_radius=0,
            scrollbar_fg_color="#CBD5E1",
            scrollbar_button_color="#94A3B8",
            scrollbar_button_hover_color="#64748B"
        )
        area_rolavel.pack(fill="both", expand=True)

        # Título da tela
        ctk.CTkLabel(
            area_rolavel,
            text="Reconhecimento Facial",
            font=("Arial", 25, "bold"),
            text_color="#172B45"
        ).pack(pady=25)

        # Área onde a webcam será exibida
        self.area_camera = ctk.CTkLabel(
            area_rolavel,
            text="Iniciando webcam...",
            width=640,
            height=400,
            fg_color="#172B45",
            text_color="white"
        )
        self.area_camera.pack(pady=15)

        # ==========================================
        # INDICADORES DO RECONHECIMENTO
        # ==========================================

        self.status_rosto = ctk.CTkLabel(
            area_rolavel,
            text="Rosto: aguardando detecção",
            font=("Arial", 14, "bold"),
            text_color="#64748B"
        )
        self.status_rosto.pack(pady=3)

        self.status_identidade = ctk.CTkLabel(
            area_rolavel,
            text="Identidade candidata: nenhuma",
            font=("Arial", 14),
            text_color="#172B45"
        )
        self.status_identidade.pack(pady=3)

        self.status_validacao = ctk.CTkLabel(
            area_rolavel,
            text="Identidade não confirmada",
            font=("Arial", 14, "bold"),
            text_color="#D97706"
        )
        self.status_validacao.pack(pady=3)

        # Botão de voltar
        ctk.CTkButton(
            area_rolavel,
            text="Voltar",
            command=self.voltar
        ).pack(pady=20)

        # Diretório principal do FaceGate
        pasta_projeto = Path(__file__).resolve().parent.parent

        # Modelo SSD original (detecção facial)
        pasta_modelos = pasta_projeto / "Modelos"

        arquivo_prototxt = pasta_modelos / "deploy.prototxt.txt"
        arquivo_modelo = (
                pasta_modelos
                / "res10_300x300_ssd_iter_140000.caffemodel"
        )

        # Novo modelo Eigenfaces dos moradores
        arquivo_eigenfaces = (
                pasta_projeto
                / "modelos_moradores"
                / "eigen_classifier.yml"
        )

        # Cadastro dos moradores
        arquivo_moradores = (
                pasta_projeto
                / "dados"
                / "moradores.json"
        )

        if not hasattr(cv2, "face"):
            raise RuntimeError(
                "O módulo cv2.face não está disponível. "
                "Instale o pacote opencv-contrib-python."
            )

        if hasattr(cv2.face, "EigenFaceRecognizer_create"):
            criador_eigenfaces = cv2.face.EigenFaceRecognizer_create
        elif hasattr(cv2.face, "EigenFaceRecognizer"):
            criador_eigenfaces = cv2.face.EigenFaceRecognizer.create
        else:
            raise RuntimeError(
                "Eigenfaces não está disponível nesta instalação do OpenCV."
            )

        if not arquivo_eigenfaces.exists():
            raise RuntimeError(
                "Modelo facial não encontrado. Execute o treinamento facial "
                "antes de iniciar o reconhecimento."
            )

        # Carrega o novo reconhecedor
        self.reconhecedor = criador_eigenfaces()
        self.reconhecedor.read(str(arquivo_eigenfaces))

        # Carrega os moradores cadastrados
        with open(arquivo_moradores, "r", encoding="utf-8") as arquivo:
            moradores = json.load(arquivo)

        # Relaciona ID facial ao nome do morador
        self.face_names = {}

        for morador in moradores:
            id_facial = morador.get("id_facial")

            if id_facial is not None:
                self.face_names[int(id_facial)] = morador["nome"]

        # Mantém o detector SSD existente
        self.detector_facial = cv2.dnn.readNetFromCaffe(
            str(arquivo_prototxt),
            str(arquivo_modelo)
        )

        # Inicializa a câmera
        self.iniciar_camera()

    def iniciar_camera(self):
        self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():
            self.area_camera.configure(
                text="Erro ao conectar à webcam"
            )
            self.camera.release()
            self.camera = None
            return
        self.inicio_reconhecimento = time.monotonic()
        self.atualizar_camera()

    def reiniciar_validacao(self):

        self.id_candidato = None
        self.leituras_consecutivas = 0

    def validar_identidade(self, id_facial, nome, distancia):

        if self.reconhecimento_finalizado:
            return

        # Verifica se o ID pertence a um morador
        if id_facial not in self.face_names:

            self.reiniciar_validacao()

            self.status_validacao.configure(
                text="Identidade não cadastrada",
                text_color="#DC2626"
            )

            return

        # Verifica a distância Eigenfaces
        if (
            distancia is None
            or not math.isfinite(distancia)
            or distancia < 0
            or distancia > LIMITE_DISTANCIA
        ):

            self.reiniciar_validacao()

            self.status_validacao.configure(
                text="Distância acima do limite ou inválida",
                text_color="#DC2626"
            )

            return

        # Verifica se continua sendo o mesmo candidato
        if self.id_candidato == id_facial:

            self.leituras_consecutivas += 1

        else:

            self.id_candidato = id_facial
            self.leituras_consecutivas = 1

        # Atualiza o progresso na interface
        self.status_validacao.configure(
            text=(
                f"Validando identidade: "
                f"{self.leituras_consecutivas}/"
                f"{LEITURAS_NECESSARIAS}"
            ),
            text_color="#D97706"
        )

        # Verifica se atingiu a quantidade necessária
        if self.leituras_consecutivas >= LEITURAS_NECESSARIAS:

            self.identidade_confirmada = True
            self.reconhecimento_finalizado = True

            self.status_validacao.configure(
                text="Acesso autorizado (simulação)",
                text_color="#16A34A"
            )

            print("\n================================")
            print("ACESSO AUTORIZADO - SIMULAÇÃO")
            print(f"Morador: {nome}")
            print(f"ID facial: {id_facial}")
            print(f"Distância: {distancia:.2f}")
            print("================================\n")

            print("[DEBUG 1] Identidade validada")
            print(f"[DEBUG 2] Callback: {self.acesso_callback}")
            # Comunica o resultado ao sistema principal
            if self.acesso_callback is not None:
                try:
                    resultado = self.acesso_callback(
                        id_facial,
                        nome,
                        distancia
                    )
                    print("[DEBUG 3] Executando callback de autorização")
                    self.status_validacao.configure(
                        text=resultado,
                        text_color="#16A34A"
                    )

                except Exception as erro:
                    self.status_validacao.configure(
                        text="Falha na comunicação de acesso",
                        text_color="#DC2626"
                    )
                    print(f"[FaceGate] Erro: {erro}")


    def detectar_rostos(self, imagem):

        if self.reconhecimento_finalizado:
            return imagem

        altura, largura = imagem.shape[:2]

        rostos = []

        # Prepara a imagem para o detector SSD
        blob = cv2.dnn.blobFromImage(
            imagem,
            scalefactor=1.0,
            size=(300, 300),
            mean=(104.0, 177.0, 123.0)
        )

        self.detector_facial.setInput(blob)
        deteccoes = self.detector_facial.forward()

        # ======================================
        # DETECTAR TODOS OS ROSTOS
        # ======================================

        for i in range(deteccoes.shape[2]):

            confianca = float(deteccoes[0, 0, i, 2])

            if confianca < 0.85:
                continue

            caixa = deteccoes[0, 0, i, 3:7] * [
                largura, altura, largura, altura
            ]

            x1, y1, x2, y2 = caixa.astype(int)

            x1 = max(0, min(x1, largura))
            x2 = max(0, min(x2, largura))
            y1 = max(0, min(y1, altura))
            y2 = max(0, min(y2, altura))

            w = x2 - x1
            h = y2 - y1

            if w <= 0 or h <= 0:
                continue

            rostos.append((x1, y1, w, h))

        # ======================================
        # NENHUM ROSTO DETECTADO
        # ======================================

        if len(rostos) == 0:

            self.reiniciar_validacao()

            self.status_rosto.configure(
                text="Rosto: não detectado",
                text_color="#64748B"
            )

            self.status_identidade.configure(
                text="Identidade candidata: nenhuma",
                text_color="#172B45"
            )

            self.status_validacao.configure(
                text="Aguardando detecção facial",
                text_color="#D97706"
            )

            return imagem

        # ======================================
        # MAIS DE UM ROSTO DETECTADO
        # ======================================

        if len(rostos) > 1:

            self.reiniciar_validacao()

            self.status_rosto.configure(
                text=f"Rostos detectados: {len(rostos)}",
                text_color="#DC2626"
            )

            self.status_identidade.configure(
                text="Identidade candidata: nenhuma"
            )

            self.status_validacao.configure(
                text="Apenas uma pessoa por vez",
                text_color="#DC2626"
            )

            for x, y, w, h in rostos:

                cv2.rectangle(
                    imagem,
                    (x, y),
                    (x + w, y + h),
                    (0, 0, 255),
                    2
                )

            return imagem

        # ======================================
        # RECONHECER UM ÚNICO ROSTO
        # ======================================

        x, y, w, h = rostos[0]

        if w < 105 or h < 105:

            self.reiniciar_validacao()

            self.status_rosto.configure(
                text="Rosto: muito distante",
                text_color="#D97706"
            )

            self.status_identidade.configure(
                text="Identidade candidata: nenhuma"
            )

            self.status_validacao.configure(
                text="Aproxime-se da câmera",
                text_color="#D97706"
            )

            return imagem

        id_facial, nome, distancia = self.reconhecer_rosto(
            imagem, x, y, w, h
        )

        # Atualiza os indicadores
        self.status_rosto.configure(
            text="Rosto: detectado",
            text_color="#16A34A"
        )

        self.status_identidade.configure(
            text=f"Identidade candidata: {nome}",
            text_color="#172B45"
        )

        # Executa a validação facial
        self.validar_identidade(
            id_facial,
            nome,
            distancia
        )

        # Define a cor do retângulo
        if self.identidade_confirmada:

            cor = (0, 255, 0)

        elif (
            id_facial not in self.face_names
            or distancia is None
            or not math.isfinite(distancia)
            or distancia < 0
            or distancia > LIMITE_DISTANCIA
        ):

            cor = (0, 0, 255)

        else:

            cor = (0, 165, 255)

        cv2.rectangle(
            imagem,
            (x, y),
            (x + w, y + h),
            cor,
            2
        )

        cv2.putText(
            imagem,
            f"Candidato: {nome}",
            (x, max(20, y - 35)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            cor,
            2
        )

        if distancia is not None:

            cv2.putText(
                imagem,
                f"Distancia: {distancia:.1f}",
                (x, max(40, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                cor,
                2
            )

        return imagem

    def atualizar_camera(self):

        self.atualizacao_id = None

        if self.camera is None:
            return

        if self.reconhecimento_finalizado:
            return

        # Calcula o tempo decorrido
        tempo_decorrido = (
            time.monotonic() - self.inicio_reconhecimento
        )

        # Verifica o tempo máximo
        if tempo_decorrido >= TEMPO_MAXIMO_RECONHECIMENTO:

            self.reiniciar_validacao()

            self.reconhecimento_finalizado = True
            self.identidade_confirmada = False

            self.status_validacao.configure(
                text="Acesso negado: tempo limite atingido",
                text_color="#DC2626"
            )

            print("[FaceGate] Acesso negado: tempo limite.")

            self.camera.release()
            self.camera = None

            return

        conectado, imagem = self.camera.read()

        if conectado and imagem is not None and imagem.size > 0:

            imagem = self.detectar_rostos(imagem)

            imagem_rgb = cv2.cvtColor(
                imagem,
                cv2.COLOR_BGR2RGB
            )

            imagem_pil = Image.fromarray(imagem_rgb)

            imagem_ctk = ctk.CTkImage(
                light_image=imagem_pil,
                dark_image=imagem_pil,
                size=(640, 400)
            )

            self.area_camera.configure(
                image=imagem_ctk,
                text=""
            )

        else:

            self.reiniciar_validacao()

            self.status_rosto.configure(
                text="Falha na leitura da webcam",
                text_color="#DC2626"
            )

            self.status_identidade.configure(
                text="Identidade candidata: nenhuma"
            )

            self.status_validacao.configure(
                text="Aguardando imagem válida",
                text_color="#D97706"
            )

        # Encerra a captura após a confirmação
        if self.reconhecimento_finalizado:

            self.camera.release()
            self.camera = None

            return

        # Agenda a próxima leitura
        self.atualizacao_id = self.after(
            30,
            self.atualizar_camera
        )

    def liberar_recursos(self):

        if self.atualizacao_id is not None:

            self.after_cancel(self.atualizacao_id)
            self.atualizacao_id = None

        if self.camera is not None:

            self.camera.release()
            self.camera = None

    def voltar(self):

        self.liberar_recursos()

        self.voltar_callback()

    def destroy(self):

        self.liberar_recursos()

        super().destroy()
