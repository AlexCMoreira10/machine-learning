
import customtkinter as ctk
from tkinter import messagebox
import json
from datetime import datetime
from pathlib import Path
from interface.tela_cadastro import TelaCadastro
from interface.tela_moradores import TelaMoradores
from interface.tela_reconhecimento import TelaReconhecimento
from treinamento_moradores import treinar_moradores
from comunicacao.mqtt_client import MQTTClient
from queue import Queue, Empty

# ==========================================
# CONFIGURAÇÕES
# ==========================================

AZUL_ESCURO = "#172B45"
AZUL_CLARO = "#365B82"
FUNDO = "#F5F7FA"
BRANCO = "#FFFFFF"
CINZA = "#64748B"

ARQUIVO_HISTORICO = (
    Path(__file__).resolve().parent
    / "dados"
    / "historico_acessos.json"
)

# Habilitar exclusivamente para testes no Wokwi
LIBERACAO_SIMULADA_HABILITADA = True

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
# CONTROLE MQTT
# ==========================================

fila_mqtt = Queue()
tela_atual = None
sensor_perto = False
status_broker = None
switch_broker = None
encerrando = False

def receber_mensagem_mqtt(topico, mensagem):
    fila_mqtt.put((topico, mensagem))

broker = MQTTClient(
    ao_receber=receber_mensagem_mqtt
)


def alternar_broker():

    global sensor_perto
    try:
        if switch_broker.get() == 1:
            sensor_perto = False
            broker.conectar()
        else:
            broker.desconectar()
            sensor_perto = False
            # Descartar mensagens pendentes
            while True:
                try:
                    fila_mqtt.get_nowait()
                except Empty:
                    break

    except Exception as erro:

        broker.desconectar()
        switch_broker.deselect()
        messagebox.showerror(
            "Erro MQTT",
            f"Erro na comunicação com o broker:\n{erro}"
        )
    atualizar_status_broker()


def atualizar_status_broker():

    if status_broker is None:
        return
    if not status_broker.winfo_exists():
        return
    if not broker.ativo:
        status_broker.configure(
            text="● Desconectado",
            text_color="#F87171"
        )
    elif broker.conectado:
        status_broker.configure(
            text="● Conectado",
            text_color="#4ADE80"
        )
    else:
        status_broker.configure(
            text="● Conectando...",
            text_color="#FACC15"
        )


def processar_eventos_mqtt():

    global sensor_perto

    if encerrando:
        return

    try:

        while True:

            topico, mensagem = fila_mqtt.get_nowait()

            if not broker.ativo or not broker.conectado:
                continue

            if topico == broker.topico_sensor:

                mensagem = mensagem.lower().strip()

                if mensagem == "perto":

                    if not sensor_perto:

                        sensor_perto = True

                        print("[FaceGate] Presença detectada.")

                        if tela_atual == "inicio":

                            iniciar_reconhecimento()

                elif mensagem == "longe":

                    sensor_perto = False

                    print("[FaceGate] Sensor rearmado.")

            elif topico == broker.topico_status:

                print(f"[CATRACA] {mensagem}")

    except Empty:
        pass

    finally:

        atualizar_status_broker()

        if not encerrando:

            app.after(100, processar_eventos_mqtt)


# ==========================================
# LIMPAR TELA
# ==========================================


def limpar_tela():

    global status_broker
    global switch_broker

    status_broker = None
    switch_broker = None

    for widget in app.winfo_children():
        widget.destroy()



# ==========================================
# TELA INICIAL
# ==========================================

def mostrar_inicio():
    global tela_atual
    global status_broker
    global switch_broker

    limpar_tela()

    tela_atual = "inicio"

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


    # ======================================
    # CONTROLE DO BROKER NO CABEÇALHO
    # ======================================

    area_broker = ctk.CTkFrame(
        cabecalho,
        fg_color="transparent"
    )

    area_broker.pack(
        side="right",
        padx=35,
        pady=10
    )

    switch_broker = ctk.CTkSwitch(
        area_broker,
        text="Comunicação MQTT",
        font=("Arial", 13, "bold"),
        text_color=BRANCO,
        progress_color="#16A34A",
        command=alternar_broker
    )

    switch_broker.pack(
        anchor="e",
        pady=(0, 5)
    )

    status_broker = ctk.CTkLabel(
        area_broker,
        text="● Desconectado",
        font=("Arial", 12),
        text_color="#F87171"
    )

    status_broker.pack(anchor="e")

    # Restaurar o estado do botão
    if broker.ativo:
        switch_broker.select()
    else:
        switch_broker.deselect()

    atualizar_status_broker()


    area_rolavel = ctk.CTkScrollableFrame(
        app,
        fg_color=FUNDO,
        corner_radius=0,
        scrollbar_fg_color="#CBD5E1",
        scrollbar_button_color="#94A3B8",
        scrollbar_button_hover_color="#64748B"
    )
    area_rolavel.pack(fill="both", expand=True)

    ctk.CTkLabel(
        area_rolavel,
        text="Sistema de reconhecimento facial e controle de acesso",
        font=("Arial", 19, "bold"),
        text_color=AZUL_ESCURO
    ).pack(pady=(55, 10))

    ctk.CTkLabel(
        area_rolavel,
        text="Bem-vindo ao sistema de gerenciamento de moradores.",
        font=("Arial", 13),
        text_color=CINZA
    ).pack(pady=(0, 35))

    area_botoes = ctk.CTkFrame(
        area_rolavel,
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

    ctk.CTkButton(
        area_botoes,
        text="Treinamento Facial",
        height=50,
        font=("Arial", 15, "bold"),
        fg_color=AZUL_CLARO,
        hover_color="#456F9C",
        command=iniciar_treinamento
    ).pack(fill="x", padx=35, pady=(12, 30))


# ==========================================
# ABRIR CADASTRO
# ==========================================

def mostrar_cadastro():

    global tela_atual
    limpar_tela()
    tela_atual = "cadastro"
    TelaCadastro(
        app,
        voltar_callback=mostrar_inicio
    )


# ==========================================
# LISTA DE MORADORES
# ==========================================

def mostrar_moradores():

    global tela_atual
    limpar_tela()
    tela_atual = "moradores"
    TelaMoradores(
        app,
        voltar_callback=mostrar_inicio
    )



# ==========================================
# PROCESSAR AUTORIZAÇÃO DE ACESSO
# ==========================================

def processar_autorizacao(id_facial, nome, distancia):
    print("[DEBUG 4] Entrou em processar_autorizacao")
    print(f"[DEBUG 5] Liberação habilitada: {LIBERACAO_SIMULADA_HABILITADA}")
    print(f"[DEBUG 6] Broker ativo: {broker.ativo}")
    print(f"[DEBUG 7] Broker conectado: {broker.conectado}")

    print("\n[FaceGate] Validação facial concluída.")
    print(f"[FaceGate] Morador: {nome}")
    print(f"[FaceGate] ID facial: {id_facial}")
    print(f"[FaceGate] Distância: {distancia:.2f}")

    registrar_acesso(id_facial, nome, distancia)

    if not LIBERACAO_SIMULADA_HABILITADA:
        return "Validação concluída - liberação desativada"

    if not broker.ativo:
        return "Validação concluída - MQTT desligado"

    if not broker.conectado:
        return "Validação concluída - broker desconectado"

    enviado = broker.liberar_catraca()

    if enviado:
        print("[FaceGate] Comando de liberação solicitado.")
        return "Comando de liberação solicitado (simulação)"
    return "Validação concluída - falha no envio"

# ==========================================
# RECONHECIMENTO FACIAL
# ==========================================



def iniciar_reconhecimento():

    global tela_atual

    if tela_atual == "reconhecimento":
        return

    limpar_tela()

    tela_atual = "reconhecimento"

    try:

        TelaReconhecimento(
            app,
            voltar_callback=mostrar_inicio,
            acesso_callback=processar_autorizacao
        )

    except Exception as erro:

        mostrar_inicio()

        messagebox.showerror(
            "Erro no reconhecimento",
            f"Não foi possível iniciar o reconhecimento:\n{erro}"
        )


# ==========================================
# HISTÓRICO
# ==========================================

def registrar_acesso(id_facial, nome, distancia):

    registro = {
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "nome": nome,
        "id_facial": id_facial,
        "distancia": round(float(distancia), 2),
        "status": "Acesso autorizado"
    }

    try:
        ARQUIVO_HISTORICO.parent.mkdir(parents=True, exist_ok=True)

        if ARQUIVO_HISTORICO.exists():
            with open(
                ARQUIVO_HISTORICO,
                "r",
                encoding="utf-8"
            ) as arquivo:
                historico = json.load(arquivo)
                if not isinstance(historico, list):
                    historico = []
        else:
            historico = []

        historico.insert(0, registro)

        with open(
            ARQUIVO_HISTORICO,
            "w",
            encoding="utf-8"
        ) as arquivo:
            json.dump(historico, arquivo, ensure_ascii=False, indent=4)

    except Exception as erro:
        print(f"[FaceGate] Falha ao registrar acesso no histórico: {erro}")


def carregar_historico():

    if not ARQUIVO_HISTORICO.exists():
        return []

    try:
        with open(
            ARQUIVO_HISTORICO,
            "r",
            encoding="utf-8"
        ) as arquivo:
            historico = json.load(arquivo)
            return historico if isinstance(historico, list) else []

    except (json.JSONDecodeError, OSError) as erro:
        print(f"[FaceGate] Falha ao carregar histórico: {erro}")
        return []


def abrir_historico():

    global tela_atual
    limpar_tela()
    tela_atual = "historico"

    ctk.CTkLabel(
        app,
        text="Histórico de acessos",
        font=("Arial", 25, "bold"),
        text_color=AZUL_ESCURO
    ).pack(pady=(30, 15))

    area_historico = ctk.CTkScrollableFrame(
        app,
        fg_color=FUNDO,
        corner_radius=0,
        scrollbar_fg_color="#CBD5E1",
        scrollbar_button_color="#94A3B8",
        scrollbar_button_hover_color="#64748B"
    )
    area_historico.pack(fill="both", expand=True, padx=30)

    historico = carregar_historico()

    if not historico:
        ctk.CTkLabel(
            area_historico,
            text="Nenhum acesso registrado.",
            font=("Arial", 14),
            text_color=CINZA
        ).pack(pady=30)
    else:
        for registro in historico:
            card = ctk.CTkFrame(
                area_historico,
                fg_color=BRANCO,
                corner_radius=12,
                border_width=1,
                border_color="#E2E8F0"
            )
            card.pack(fill="x", pady=8)

            ctk.CTkLabel(
                card,
                text=str(registro.get("nome", "Morador desconhecido")),
                font=("Arial", 15, "bold"),
                text_color=AZUL_ESCURO,
                anchor="w"
            ).pack(fill="x", padx=20, pady=(12, 2))

            ctk.CTkLabel(
                card,
                text=(
                    f"{registro.get('data_hora', '--')}  |  "
                    f"ID: {registro.get('id_facial', '--')}  |  "
                    f"Distância: {registro.get('distancia', '--')}"
                ),
                font=("Arial", 12),
                text_color=CINZA,
                anchor="w"
            ).pack(fill="x", padx=20, pady=(0, 12))

    ctk.CTkButton(
        app,
        text="Voltar",
        command=mostrar_inicio
    ).pack(pady=30)


def iniciar_treinamento():
    try:
        quantidade = treinar_moradores()

        messagebox.showinfo(
            "Treinamento Facial",
            f"Treinamento concluído com sucesso!\n\n"
            f"Total de imagens utilizadas: {quantidade}\n\n"
            f"O modelo facial foi atualizado."
        )

    except Exception as erro:
        messagebox.showerror(
            "Erro no treinamento",
            f"Não foi possível concluir o treinamento.\n\n{erro}"
        )

# ==========================================
# INICIAR SISTEMA
# ==========================================

# ==========================================
# ENCERRAR SISTEMA
# ==========================================

def fechar_aplicacao():
    global encerrando
    encerrando = True
    try:
        broker.desconectar()

    finally:
        limpar_tela()
        app.destroy()


# ==========================================
# INICIAR SISTEMA
# ==========================================

app.protocol(
    "WM_DELETE_WINDOW",
    fechar_aplicacao
)

mostrar_inicio()
app.after(
    100,
    processar_eventos_mqtt
)

app.mainloop()
