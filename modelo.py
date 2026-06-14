import random


# ── Inicialização ─────────────────────────────────────────────

def inicializar_estados(rede, no_inicial=0):
    """
    Cada pessoa começa como Suscetível (S).
    Só o nó inicial começa como Infectado (I).
    """
    estados = {}

    for pessoa in rede.nodes():
        estados[pessoa] = 'S'

    estados[no_inicial] = 'I'
    return estados


# ── Cálculo de probabilidade individual ───────────────────────

def calcular_prob_contagio(rede, receptor, emissor, prob_base):
    """
    Calcula a probabilidade real de contágio entre
    dois nós específicos, levando em conta:

      - prob_base   → probabilidade global do cenário
      - credulidade → atributo do receptor
      - influencia  → atributo do emissor

    Se os nós não tiverem atributos (rede sem perfis),
    cai de volta para a prob_base — compatibilidade
    com redes sintéticas simples.
    """
    credulidade = rede.nodes[receptor].get('credulidade', prob_base)
    influencia  = rede.nodes[emissor].get('influencia',  prob_base)
    ativo       = rede.nodes[receptor].get('ativo', True)

    # Usuário inativo tem chance reduzida de ver o conteúdo
    fator_ativo = 1.0 if ativo else 0.3

    # Combina os três fatores
    prob_final = prob_base * credulidade * (1 + influencia) * fator_ativo

    # Garante que fica entre 0 e 1
    return max(0.0, min(1.0, prob_final))


def calcular_prob_recuperacao(rede, no, prob_base):
    """
    Calcula a probabilidade de um nó parar
    de compartilhar a fake news.

    Influencers param mais devagar — eles têm
    mais engajamento e continuam compartilhando
    por mais tempo.
    """
    influencia = rede.nodes[no].get('influencia', prob_base)

    # Quanto mais influente, mais devagar para de compartilhar
    prob_final = prob_base * (1 - influencia * 0.5)

    return max(0.0, min(1.0, prob_final))


# ── Um passo de propagação ────────────────────────────────────

def um_passo(rede, estados, prob_contagio=0.3, prob_recuperacao=0.1):
    """
    Simula um dia de propagação da fake news
    usando atributos individuais de cada nó.
    """
    novos_estados = estados.copy()

    for pessoa in rede.nodes():

        if estados[pessoa] == 'I':

            # Tenta convencer cada vizinho suscetível
            for vizinho in rede.neighbors(pessoa):
                if estados[vizinho] == 'S':

                    # Probabilidade individual — não mais global
                    prob = calcular_prob_contagio(
                        rede,
                        receptor=vizinho,
                        emissor=pessoa,
                        prob_base=prob_contagio
                    )

                    if random.random() < prob:
                        novos_estados[vizinho] = 'I'

            # Probabilidade individual de parar de compartilhar
            prob_rec = calcular_prob_recuperacao(
                rede,
                no=pessoa,
                prob_base=prob_recuperacao
            )

            if random.random() < prob_rec:
                novos_estados[pessoa] = 'R'

    return novos_estados


# ── Simulação completa ────────────────────────────────────────

def simular(rede, no_inicial=0, dias=30,
            prob_contagio=0.3, prob_recuperacao=0.1):
    """
    Roda a simulação por N dias e retorna:
      - historico         → contagens S, I, R por dia
      - historico_estados → estado completo de cada nó por dia
    """
    estados           = inicializar_estados(rede, no_inicial)
    historico         = []
    historico_estados = []

    for dia in range(dias):

        contagem = {
            'dia': dia,
            'S': list(estados.values()).count('S'),
            'I': list(estados.values()).count('I'),
            'R': list(estados.values()).count('R')
        }
        historico.append(contagem)
        historico_estados.append(estados.copy())

        estados = um_passo(rede, estados, prob_contagio, prob_recuperacao)

        if contagem['I'] == 0:
            print(f"  Fake news extinta no dia {dia}.")
            break

    return historico, historico_estados


# ── Teste ─────────────────────────────────────────────────────

if __name__ == "__main__":
    from rede import criar_rede, estatisticas_rede, get_influencers, get_periferico

    rede = criar_rede(n=100, m=2, seed=42)
    estatisticas_rede(rede)

    influencer  = get_influencers(rede, top_n=1)[0]
    periferico  = get_periferico(rede)

    # ── Cenário 1: paciente zero é um influencer ──────────────
    print(f"\nCenário 1 — Paciente zero: influencer (nó {influencer})")
    print(f"  credulidade : {rede.nodes[influencer]['credulidade']:.3f}")
    print(f"  influência  : {rede.nodes[influencer]['influencia']:.3f}")

    hist_influencer, _ = simular(
        rede,
        no_inicial=influencer,
        dias=50,
        prob_contagio=0.3,
        prob_recuperacao=0.1
    )
    pico_i = max(r['I'] for r in hist_influencer)
    total_i = max(r['I'] + r['R'] for r in hist_influencer)
    print(f"  Pico de infectados : {pico_i}")
    print(f"  Total atingido     : {total_i}")

    # ── Cenário 2: paciente zero é um periférico ──────────────
    print(f"\nCenário 2 — Paciente zero: periférico (nó {periferico})")
    print(f"  credulidade : {rede.nodes[periferico]['credulidade']:.3f}")
    print(f"  influência  : {rede.nodes[periferico]['influencia']:.3f}")

    hist_periferico, _ = simular(
        rede,
        no_inicial=periferico,
        dias=50,
        prob_contagio=0.3,
        prob_recuperacao=0.1
    )
    pico_p = max(r['I'] for r in hist_periferico)
    total_p = max(r['I'] + r['R'] for r in hist_periferico)
    print(f"  Pico de infectados : {pico_p}")
    print(f"  Total atingido     : {total_p}")

    # ── Comparativo direto ────────────────────────────────────
    print(f"\nComparativo:")
    print(f"  Influencer atingiu {total_i} pessoas")
    print(f"  Periférico atingiu {total_p} pessoas")

    if total_p > 0:
        print(f"  Razão: {total_i / total_p:.1f}x mais impacto")