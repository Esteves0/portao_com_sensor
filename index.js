// Conecta via WebSockets no HiveMQ público (Porta 8000)
const client = mqtt.connect('wss://broker.hivemq.com:8884/mqtt');
const statusConexao = document.getElementById('conexao');
const elDistancia = document.getElementById('distancia');
const elPresenca = document.getElementById('presenca');
const elEstado = document.getElementById('estado');

// Ao conectar com sucesso ao HiveMQ
client.on('connect', () => {
  statusConexao.innerText = 'Conectado';
  statusConexao.className = 'status online';

  // Inscreve nos tópicos configurados no C++
  client.subscribe('equipe/portao/distancia');
  client.subscribe('equipe/portao/presenca');
  client.subscribe('equipe/portao/estado');
});

// Ao perder a conexão
client.on('offline', () => {
  statusConexao.innerText = 'Desconectado';
  statusConexao.className = 'status offline';
});

// Quando o ESP32 envia uma mensagem
client.on('message', (topico, mensagem) => {
  const valor = mensagem.toString();

  if (topico === 'equipe/portao/distancia') {
    elDistancia.innerText = valor;
  }

  if (topico === 'equipe/portao/presenca') {
    elPresenca.innerText = valor;
  }

  if (topico === 'equipe/portao/estado') {
    elEstado.innerText = valor;
    
    if (valor === 'ABERTO') {
      elEstado.className = 'badge aberto';
    } else {
      elEstado.className = 'badge fechado';
    }
  }
});