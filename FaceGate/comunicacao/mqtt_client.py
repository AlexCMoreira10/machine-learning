
import os
import ssl
import threading
from pathlib import Path

import paho.mqtt.client as mqtt
from dotenv import load_dotenv


# Carregar as configurações do arquivo .env
PASTA_PROJETO = Path(__file__).resolve().parents[1]

load_dotenv(PASTA_PROJETO / ".env")


class MQTTClient:

    def __init__(self, ao_receber=None):

        self.host = os.getenv("MQTT_HOST")
        self.porta = int(os.getenv("MQTT_PORT", "8883"))

        self.usuario = os.getenv("MQTT_USERNAME")
        self.senha = os.getenv("MQTT_PASSWORD")

        self.topico_sensor = os.getenv(
            "MQTT_TOPICO_SENSOR",
            "portao/1/sensor"
        )

        self.topico_comando = os.getenv(
            "MQTT_TOPICO_COMANDO",
            "portao/1/comando"
        )

        self.topico_status = os.getenv(
            "MQTT_TOPICO_STATUS",
            "portao/1/status"
        )

        self.ao_receber = ao_receber

        self.ativo = False
        self.conectado = False

        self.lock = threading.RLock()

        # Criar cliente MQTT
        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )

        self.client.username_pw_set(
            self.usuario,
            self.senha
        )

        # Configurar conexão TLS segura
        self.client.tls_set_context(
            ssl.create_default_context()
        )

        # Configurar eventos
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        self.client.reconnect_delay_set(
            min_delay=1,
            max_delay=30
        )

    # ======================================
    # CONECTAR AO BROKER
    # ======================================

    def conectar(self):

        if self.ativo:
            return

        if not all([
            self.host,
            self.usuario,
            self.senha
        ]):
            raise ValueError(
                "Configurações MQTT incompletas no .env"
            )

        with self.lock:
            self.ativo = True

        try:
            self.client.connect_async(
                self.host,
                self.porta,
                keepalive=60
            )

            self.client.loop_start()

            print("[MQTT] Iniciando conexão...")

        except Exception:
            self.ativo = False
            raise

    # ======================================
    # DESCONECTAR DO BROKER
    # ======================================

    def desconectar(self):

        with self.lock:
            self.ativo = False
            self.conectado = False

        self.client.disconnect()
        self.client.loop_stop()

        print("[MQTT] Comunicação desativada.")

    # ======================================
    # EVENTO DE CONEXÃO
    # ======================================

    def on_connect(
        self,
        client,
        userdata,
        flags,
        reason_code,
        properties
    ):

        with self.lock:

            if not self.ativo:
                return

            if reason_code == 0:

                self.conectado = True

                print("[MQTT] Conectado ao broker!")

                client.subscribe(self.topico_sensor)
                client.subscribe(self.topico_status)

                print(
                    f"[MQTT] Inscrito em: "
                    f"{self.topico_sensor}"
                )

                print(
                    f"[MQTT] Inscrito em: "
                    f"{self.topico_status}"
                )

            else:
                self.conectado = False

                print(
                    f"[MQTT] Falha na conexão: "
                    f"{reason_code}"
                )

    # ======================================
    # EVENTO DE DESCONEXÃO
    # ======================================

    def on_disconnect(
        self,
        client,
        userdata,
        disconnect_flags,
        reason_code,
        properties
    ):

        with self.lock:
            self.conectado = False

        print("[MQTT] Broker desconectado.")

    # ======================================
    # RECEBER MENSAGENS
    # ======================================

    def on_message(self, client, userdata, msg):

        with self.lock:

            if not self.ativo:
                return

            mensagem = msg.payload.decode(
                "utf-8",
                errors="replace"
            ).strip()

            print(
                f"[MQTT] {msg.topic}: {mensagem}"
            )

            if self.ao_receber:
                self.ao_receber(
                    msg.topic,
                    mensagem
                )

    # ======================================
    # ENVIAR COMANDO DE LIBERAÇÃO
    # ======================================

    def liberar_catraca(self):
        print("[DEBUG 8] Entrou em liberar_catraca")
        print(f"[DEBUG 9] Tópico: {self.topico_comando}")

        with self.lock:
            if not self.ativo:
                print("[MQTT] Comunicação desativada.")
                return False

            if not self.conectado:
                print("[MQTT] Broker desconectado.")
                return False

            resultado = self.client.publish(
                topic=self.topico_comando,
                payload="liberar",
                qos=0,
                retain=False
            )

            if resultado.rc == mqtt.MQTT_ERR_SUCCESS:

                print(
                    f"[MQTT] Comando solicitado em "
                    f"{self.topico_comando}: liberar"
                )

                return True

            print("[MQTT] Falha ao publicar comando.")

            return False
