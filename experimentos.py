from modelo import simular
from vizualizacao import plotar_comparativo
import networkx as nx
import matplotlib.pyplot as plt

def experimento_prob_contagio():
    """
    Mantém a rede e prob_recuperacao fixos.
    Varia apenas prob_contagio e observa o pico de infectados.
    """
    rede = nx.barabasi_albert_graph(n=100, m=2, seed=42)
    probabilidades = [0.05, 0.10, 0.20, 0.30, 0.40, 0.50]
    resultados = []

    for prob in probabilidades:
        historico, _ = simular(
            rede,
            dias=50,
            prob_contagio=prob,
            prob_recuperacao=0.1
        )
        pico = max(r['I'] for r in historico)
        resultados.append((prob, pico))
        print(f"  prob_contagio={prob:.2f} → pico de infectados: {pico}")

    # Plota o resultado
    probs  = [r[0] for r in resultados]
    picos  = [r[1] for r in resultados]

    plt.figure(figsize=(8, 5))
    plt.title("Efeito da Probabilidade de Contágio no Pico de Infectados")
    plt.plot(probs, picos, marker='o', color='crimson', linewidth=2)
    plt.xlabel("Probabilidade de Contágio")
    plt.ylabel("Pico de Infectados")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def experimento_estrutura_rede():
    """
    Mantém os parâmetros fixos.
    Compara como diferentes estruturas de rede
    afetam a propagação — esse é o argumento
    central do paradigma data-driven.
    """
    redes = {
        'Centralizada\n(Estrela)'   : nx.star_graph(99),
        'Comunitária\n(Caveman)'    : nx.connected_caveman_graph(10, 10),
        'Aleatória\n(Barabási)'     : nx.barabasi_albert_graph(100, 2, seed=42),
        'Malha\n(Grid)'             : nx.grid_2d_graph(10, 10)
    }

    print("\nEstrutura da rede vs. propagação:")
    print(f"{'Rede':<25} {'Pico':>6}  {'Dia do pico':>12}  {'Total atingido':>15}")
    print("-" * 62)

    todos_historicos = {}

    for nome, rede in redes.items():
        historico, _ = simular(
            rede,
            no_inicial=0,
            dias=50,
            prob_contagio=0.3,
            prob_recuperacao=0.1
        )

        pico          = max(r['I'] for r in historico)
        dia_do_pico   = next(r['dia'] for r in historico if r['I'] == pico)
        total_atingido = max(r['I'] + r['R'] for r in historico)

        print(f"{nome.replace(chr(10), ' '):<25} "
              f"{pico:>6}  "
              f"{dia_do_pico:>12}  "
              f"{total_atingido:>15}")

        todos_historicos[nome] = historico

    plotar_comparativo(todos_historicos)

def experimento_paciente_zero():
    """
    O mesmo código, mesmos parâmetros, mesma rede.
    Só muda quem postou a fake news primeiro.
    Mostra que nos dados (a posição do paciente zero)
    determinam o resultado.
    """
    rede = nx.barabasi_albert_graph(n=100, m=2, seed=42)

    # Identifica os nós mais conectados (influencers)
    nos_por_conexoes = sorted(
        rede.nodes(),
        key=lambda n: rede.degree(n),
        reverse=True
    )

    influencer   = nos_por_conexoes[0]   # mais conectado
    intermediario = nos_por_conexoes[50]  # conexões medianas
    periferico   = nos_por_conexoes[-1]  # menos conectado

    cenarios = {
        f'Influencer (nó {influencer}, '
        f'{rede.degree(influencer)} conexões)'  : influencer,

        f'Intermediário (nó {intermediario}, '
        f'{rede.degree(intermediario)} conexões)': intermediario,

        f'Periférico (nó {periferico}, '
        f'{rede.degree(periferico)} conexões)'  : periferico
    }

    print("\nImpacto do paciente zero:")
    historicos = {}

    for descricao, no_inicial in cenarios.items():
        historico, _ = simular(
            rede,
            no_inicial=no_inicial,
            dias=50,
            prob_contagio=0.3,
            prob_recuperacao=0.1
        )
        pico = max(r['I'] for r in historico)
        print(f"  {descricao} → pico: {pico}")
        historicos[descricao] = historico

    plotar_comparativo(historicos)

if __name__ == "__main__":
    print("=" * 50)
    print("EXPERIMENTO 1 — Probabilidade de Contágio")
    print("=" * 50)
    experimento_prob_contagio()

    print("\n" + "=" * 50)
    print("EXPERIMENTO 2 — Estrutura da Rede")
    print("=" * 50)
    experimento_estrutura_rede()

    print("\n" + "=" * 50)
    print("EXPERIMENTO 3 — Paciente Zero")
    print("=" * 50)
    experimento_paciente_zero()
