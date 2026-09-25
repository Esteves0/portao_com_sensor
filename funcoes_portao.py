def presenca_detectada(distancia):
    # Considera presença se a distância for entre 1cm e 10cm
    return 0 < distancia <= 50


def status_portao(distancia):
    if presenca_detectada(distancia):
        return "ABERTO"
    return "FECHADO"


def formatar_dados_evento(distancia):
    # Caso receba um valor impossível do sensor
    if distancia < 0:
        return {"erro": "Distancia invalida"}

    return {
        "distancia": distancia,
        "status": status_portao(distancia),
        "presenca": presenca_detectada(distancia)
    }
def calcular_angulo_servo(status):
    # O servo motor gira 90 graus para abrir o portão, e volta para 0 para fechar
    if status == "ABERTO":
        return 90
    return 0

def verificar_dados_banco(dados):
    # Verifica se os dados estão completos antes de salvar no banco Neon
    if "status" not in dados or "distancia" not in dados:
        return False
    return True