
from comunicacao.mqtt_client import MQTTClient


def receber_mensagem(topico, mensagem):

    if topico == "portao/1/sensor":

        if mensagem == "perto":
            print("[SENSOR] Pessoa detectada!")

        elif mensagem == "longe":
            print("[SENSOR] Nenhuma pessoa próxima.")

    elif topico == "portao/1/status":

        print(f"[CATRACA] {mensagem}")


broker = MQTTClient(
    ao_receber=receber_mensagem
)

try:

    while True:

        comando = input(
            "\n1 - Ligar broker\n"
            "2 - Desligar broker\n"
            "3 - Sair\n"
            "Escolha: "
        ).strip()

        if comando == "1":
            broker.conectar()

        elif comando == "2":
            broker.desconectar()

        elif comando == "3":
            break

finally:

    broker.desconectar()



import time
from comunicacao.mqtt_client import MQTTClient

broker = MQTTClient()

try:
    broker.conectar()

    # Aguarda a conexão com o broker
    for tentativa in range(15):

        if broker.conectado:
            break

        time.sleep(1)

    if broker.conectado:

        print("\nConexão estabelecida!")
        print(f"Tópico: {broker.topico_comando}")

        resultado = broker.client.publish(
            topic=broker.topico_comando,
            payload="teste_facegate",
            qos=0,
            retain=False
        )

        print(f"Código de retorno: {resultado.rc}")

        if resultado.rc == 0:
            resultado.wait_for_publish(timeout=5)

            print(
                f"Publicação concluída: "
                f"{resultado.is_published()}"
            )

        time.sleep(3)

    else:

        print("Não foi possível conectar ao broker.")

finally:

    broker.desconectar()
