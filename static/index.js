// Conecta via WebSockets no HiveMQ público (Porta 8000)
const client = mqtt.connect('wss://broker.hivemq.com:8884/mqtt');
const statusConexao = document.getElementById('conexao');
const elDistancia = document.getElementById('distancia');
const elPresenca = document.getElementById('presenca');
const elEstado = document.getElementById('estado');
function atualizarDados() {
    fetch('/api/status')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao buscar dados do servidor');
            }
            return response.json();
        })
        .then(data => {
            // 1. Atualiza textos simples
            document.getElementById('distancia').innerText = data.distancia;
            document.getElementById('presenca').innerText = data.presenca;
            document.getElementById('entradas').innerText = data.numero_entradas;

            // 2. Atualiza Status do Broker (texto e cor)
            const elConexao = document.getElementById('conexao');
            elConexao.innerText = data.estado_broker;
            
            if (data.estado_broker.toLowerCase().includes('conectado') && !data.estado_broker.toLowerCase().includes('desconectado')) {
                elConexao.className = 'status online';
            } else {
                elConexao.className = 'status offline';
            }

            // 3. Atualiza Estado do Portão (texto e estilização das badges)
            const elEstado = document.getElementById('estado');
            elEstado.innerText = data.estado_portao;

            if (data.estado_portao.toUpperCase() === 'ABERTO') {
                elEstado.className = 'badge aberto';
            } else {
                elEstado.className = 'badge fechado';
            }
        })
        .catch(error => {
            console.error('Erro na atualização dinâmica:', error);
        });
}

// Executa a função imediatamente ao carregar a página
atualizarDados();

// Executa novamente a cada 2000 milissegundos (2 segundos)
setInterval(atualizarDados, 2000);

client.on('connect', () => {
  statusConexao.innerText = 'Conectado';
  statusConexao.className = 'status online';

  client.subscribe('equipe/portao/distancia');
  client.subscribe('equipe/portao/presenca');
  client.subscribe('equipe/portao/estado');
});

client.on('offline', () => {
  statusConexao.innerText = 'Desconectado';
  statusConexao.className = 'status offline';
});

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