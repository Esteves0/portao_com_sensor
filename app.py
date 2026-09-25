import os
from flask import *
import paho.mqtt.client as mqtt
from psycopg2.extras import RealDictCursor

from database import *

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "equipe/portao/estado"
MQTT_TOPIC_DISTANCE = "equipe/portao/distance"
MQTT_TOPIC_PRESENCE = "equipe/portao/presenca"

app = Flask(__name__)
app.secret_key = "chave_login_portao"

ultimo_estado = "FECHADO"
ultima_distancia = "N/A"
ultima_presenca = "N/A"
estado_con_broker = "Desconectado"


def on_connect(client, userdata, flags, rc, properties=None):
    global estado_con_broker
    print("[MQTT] Conectado ao Broker!")
    estado_con_broker ="Conectado!"
    client.subscribe(MQTT_TOPIC)
    client.subscribe(MQTT_TOPIC_DISTANCE)
    client.subscribe(MQTT_TOPIC_PRESENCE)

    print(f"[MQTT] Inscrito no tópico: {MQTT_TOPIC}")
    print(f"[MQTT] Inscrito no tópico: {MQTT_TOPIC_DISTANCE}")


def on_message(client, userdata, msg):
    global ultimo_estado, ultima_distancia, ultima_presenca
    texto_mensagem = msg.payload.decode()
    print(f"[MQTT] Mensagem recebida no tópico '{msg.topic}': {texto_mensagem}")

    if msg.topic == MQTT_TOPIC_DISTANCE:
        ultima_distancia = texto_mensagem
        print(f"Distancia recebida: {ultima_distancia}")


    elif msg.topic == MQTT_TOPIC_PRESENCE:
        ultima_presenca = texto_mensagem

    elif msg.topic == MQTT_TOPIC:
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

        elif ultimo_estado != 'FECHADO' and texto_mensagem == 'FECHADO' :
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


@app.route('/')
def home():
    return redirect(url_for('login'))


# --- ROTAS ---
@app.route("/index", methods=['GET'])
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = conexao()
    cur = conn.cursor()

    sql = "SELECT COUNT(*) FROM acessos"
    cur.execute(sql)
    total_entradas = cur.fetchone()[0]
    conn.close()

    return render_template("index.html", numero_entradas=total_entradas, distancia=ultima_distancia, presenca = ultima_presenca, estado_broker = estado_con_broker, estado_portao= ultimo_estado)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'usuario' in session:
            return redirect(url_for('index'))
        return render_template('login.html')

    if request.method == 'POST':
        conn = conexao()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            email = request.form.get('email')
            password = request.form.get('senha')

            cur.execute('SELECT * FROM "users" WHERE email = %s', (email,))
            user = cur.fetchone()

            if user:
                if user['senha'] == password:
                    session['usuario'] = user['email']
                    return redirect(url_for('index'))
                else:
                    return "Senha incorreta"
            else:
                return "Email não registrado"
        except Exception as e:
            return f"Ocorreu um erro: {e}"
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals(): conn.close()


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        iniciar_mqtt()

    print("[FLASK] Servidor rodando em http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)