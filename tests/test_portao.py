from funcoes_portao import *

# --- TESTES SIMPLES DE PRESENÇA ---

def test_presenca_detectada_True():
    assert presenca_detectada(7) == True

def test_presenca_detectada_False():
    # Alterado de 25 para 60 (qualquer valor acima de 50 deve retornar False)
    assert presenca_detectada(60) == False


# --- TESTES DE ESTADO DO PORTÃO ---

def test_status_portao_ABERTO():
    assert status_portao(5) == "ABERTO"

def test_status_portao_FECHADO():
    # Alterado de 40 para 60 (qualquer valor acima de 50 deve manter o portão FECHADO)
    assert status_portao(60) == "FECHADO"


# --- TESTE DE FORMATO DOS DADOS (DICIONÁRIO / JSON) ---

def test_formatar_dados_evento():
    dados_esperados = {
        "distancia": 8,
        "status": "ABERTO",
        "presenca": True
    }
    assert formatar_dados_evento(8) == dados_esperados


# --- TESTE DE EXCEÇÃO (SENSOR COM ERRO OU DISTÂNCIA NEGATIVA) ---

def test_distancia_invalida_excecao():
    assert formatar_dados_evento(-10) == {"erro": "Distancia invalida"}


from funcoes_portao import calcular_angulo_servo, verificar_dados_banco


# --- NOVOS TESTES ---

def test_calcular_angulo_servo_aberto():
    # Se o sistema mandar abrir, o ângulo do motor deve ser 90
    assert calcular_angulo_servo("ABERTO") == 90


def test_verificar_dados_banco_invalido():
    # Simula um erro onde a placa ESP32 não enviou o "status" (Teste de Exceção)
    dados_incompletos = {
        "distancia": 15,
        "presenca": False
        # Falta a chave "status" aqui
    }

    # A função deve retornar False bloqueando o salvamento no banco
    assert verificar_dados_banco(dados_incompletos) == False
