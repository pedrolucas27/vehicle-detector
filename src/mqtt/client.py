import paho.mqtt.client as mqtt
import json

MQTT_BROKER = "io.adafruit.com"
MQTT_PORT = 1883
USERNAME = "SEU_USERNAME"
AIO_KEY = "SUA_AIOKEY"

MQTT_TOPICS = {
    "car": f"{USERNAME}/feeds/carros",
    "motorbike": f"{USERNAME}/feeds/motos",
    "truck": f"{USERNAME}/feeds/caminhoes",
}

# Função de callback para quando a conexão com o broker é estabelecida
def on_connect(client, userdata, flags, rc):
    print(f"Conectado ao broker MQTT com código de retorno {rc}.")
    if rc == 0:
        # Inscrever-se em todos os tópicos necessários
        for topic in MQTT_TOPICS.values():
            client.subscribe(topic)
            print(f"Inscrito no tópico: {topic}")
    else:
        print(f"Falha na conexão. Código de retorno: {rc}")

# Função de callback para quando uma mensagem é recebida
def on_message(client, userdata, msg):
    print(f"Mensagem recebida no tópico {msg.topic}: {msg.payload.decode()}")
    try:
        evento = json.loads(msg.payload.decode())  # Assumindo que as mensagens são em JSON
        print(f"Evento processado: {evento}")
        # Aqui você pode adicionar lógica específica para lidar com o evento
    except json.JSONDecodeError:
        print("Falha ao processar a mensagem JSON")

# Função para publicar evento
def publish_event(client, evento, vehicle_type):
    if vehicle_type not in MQTT_TOPICS:
        print(f"Tipo de veículo '{vehicle_type}' inválido.")
        return
    topic = MQTT_TOPICS[vehicle_type]
    evento_json = json.dumps(evento)
    client.publish(topic, evento_json)
    print(f"Evento enviado para o tópico {topic}: {evento_json}")

# Função para criar e configurar o cliente MQTT
def create_client():
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.username_pw_set(USERNAME, AIO_KEY)  # Adiciona autenticação
    client.on_connect = on_connect
    client.on_message = on_message
    return client

# Função para conectar ao broker
def connect_client(client):
    client.connect(MQTT_BROKER, MQTT_PORT, 60)