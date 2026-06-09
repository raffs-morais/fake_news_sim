import random


def inicializar_estados(rede, no_inicial=0):
    """
    Cada pessoa começa como Suscetível (S).
    Só o nó inicial começa como Infectado (I).
    """
    estados = {}

    for pessoa in rede.nodes():
        estados[pessoa] = 'S'  # todos suscetíveis no início

    estados[no_inicial] = 'I'  # paciente zero — quem postou a fake news

    return estados

import networkx as nx

rede = nx.barabasi_albert_graph(n=50, m=2)
estados = inicializar_estados(rede, no_inicial=0)

# Confere se funcionou
infectados = [p for p, e in estados.items() if e == 'I']
suscetíveis = [p for p, e in estados.items() if e == 'S']

print(f"Infectados iniciais: {infectados}")
print(f"Suscetíveis: {len(suscetíveis)}")


def um_passo(rede, estados, prob_contagio=0.3, prob_recuperacao=0.1):
    """
    Simula um dia de propagação da fake news.

    prob_contagio   → chance de uma pessoa infectada
                      convencer um vizinho suscetível
    prob_recuperacao → chance de uma pessoa infectada
                       parar de compartilhar
    """
    novos_estados = estados.copy()  # não modifica o original — funcional!

    for pessoa in rede.nodes():

        # Se essa pessoa acredita na fake news...
        if estados[pessoa] == 'I':

            # ...tenta convencer cada contato
            for vizinho in rede.neighbors(pessoa):
                if estados[vizinho] == 'S':
                    if random.random() < prob_contagio:
                        novos_estados[vizinho] = 'I'

            # ...pode parar de compartilhar com o tempo
            if random.random() < prob_recuperacao:
                novos_estados[pessoa] = 'R'

    return novos_estados


if __name__ == "__main__":
    rede = nx.barabasi_albert_graph(n=50, m=2)

    historico, estados_finais = simular(
        rede,
        no_inicial=0,
        dias=30,
        prob_contagio=0.3,
        prob_recuperacao=0.1
    )

    print("\nEvolução dia a dia:")
    print(f"{'Dia':<6} {'Suscetíveis':<14} {'Infectados':<13} {'Removidos'}")
    print("-" * 45)

    for registro in historico:
        print(f"{registro['dia']:<6} "
              f"{registro['S']:<14} "
              f"{registro['I']:<13} "
              f"{registro['R']}")


def simular(rede, no_inicial=0, dias=30,
            prob_contagio=0.3, prob_recuperacao=0.1):
    """
    Roda a simulação por N dias e retorna:
      - historico        → contagens de S, I, R por dia (para os gráficos)
      - historico_estados → estado completo de cada nó por dia (para a animação)
    """
    estados = inicializar_estados(rede, no_inicial)
    historico         = []
    historico_estados = []   # ← isso é o que a animação precisa

    for dia in range(dias):

        # Guarda as contagens do dia (como antes)
        contagem = {
            'dia': dia,
            'S': list(estados.values()).count('S'),
            'I': list(estados.values()).count('I'),
            'R': list(estados.values()).count('R')
        }
        historico.append(contagem)

        # Guarda o snapshot completo do dia (novo)
        historico_estados.append(estados.copy())

        # Avança um dia
        estados = um_passo(rede, estados, prob_contagio, prob_recuperacao)

        # Se não há mais infectados, a fake news morreu
        if contagem['I'] == 0:
            print(f"Fake news extinta no dia {dia}.")
            break

    return historico, historico_estados   # ← agora retorna os dois