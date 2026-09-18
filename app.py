import sqlite3
from flask import Flask, jsonify, request, render_template
import paho.mqtt.client as mqtt
from database import *

# Configurações do Broker
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "equipe/portao/estado"

app = Flask(__name__)

# Conexão local


# --- MQTT ---
def on_connect(client, userdata, flags, rc, properties=None):
    print("[MQTT] Conectado ao Broker!")
    client.subscribe(MQTT_TOPIC)
    print(f"[MQTT] Inscrito no tópico: {MQTT_TOPIC}")

def on_message(client, userdata, msg):
    texto_mensagem = msg.payload.decode()
    print(f"[MQTT] Mensagem recebida no tópico '{msg.topic}': {texto_mensagem}")
    conn = conexao()
    cur = conn.cursor()
    if texto_mensagem == 'ABERTO':
        print("[MQTT] Portão aberto! Enviando para o banco de dados...")
        sql = "INSERT INTO acessos(hora_entrada) VALUES (CURRENT_TIMESTAMP)"
        cur.execute(sql)
        conn.commit()
        conn.close()


def iniciar_mqtt():
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    except AttributeError:
        client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

# --- ROTAS ---
@app.route("/", methods=['GET'])
def index():
    conn = conexao()
    cur = conn.cursor()

    sql = "SELECT COUNT(*) FROM acessos"
    cur.execute(sql)
    total_entradas = cur.fetchone()[0]
    conn.close()

    return render_template("index.html", numero_entradas=total_entradas)

# --- EXECUÇÃO ---
if __name__ == '__main__':
    iniciar_mqtt()
    print("[FLASK] Servidor rodando em http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)