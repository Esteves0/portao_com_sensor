import os
import sqlite3
from flask import Flask, jsonify, request, render_template
import paho.mqtt.client as mqtt
from database import *

# Configurações do Broker
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "equipe/portao/estado"

app = Flask(__name__)

# Controla o último estado processado para evitar gravação dupla
ultimo_estado = "FECHADO"


# --- MQTT ---
def on_connect(client, userdata, flags, rc, properties=None):
    print("[MQTT] Conectado ao Broker!")
    client.subscribe(MQTT_TOPIC)
    print(f"[MQTT] Inscrito no tópico: {MQTT_TOPIC}")


def on_message(client, userdata, msg):
    global ultimo_estado
    texto_mensagem = msg.payload.decode()
    print(f"[MQTT] Mensagem recebida no tópico '{msg.topic}': {texto_mensagem}")

    # Registra no banco de dados SOMENTE quando transitar de FECHADO para ABERTO
    if texto_mensagem == 'ABERTO' and ultimo_estado != 'ABERTO':
        ultimo_estado = 'ABERTO'
        print("[MQTT] Portão aberto! Registrando novo acesso no banco de dados...")

        try:
            conn = conexao()
            cur = conn.cursor()
            sql = "INSERT INTO acessos(hora_entrada) VALUES (CURRENT_TIMESTAMP)"
            cur.execute(sql)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[ERRO BANCO] Falha ao inserir registro: {e}")

    elif texto_mensagem == 'FECHADO':
        ultimo_estado = 'FECHADO'


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
    # Garante que o MQTT só inicie uma vez (evita duplicação do reloader do modo debug=True)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        iniciar_mqtt()

    print("[FLASK] Servidor rodando em http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)