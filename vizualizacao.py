import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx

def plotar_curvas_sir(historico):
    """
    Plota a evolução de Suscetíveis, Infectados
    e Removidos ao longo dos dias.
    """
    dias        = [r['dia'] for r in historico]
    suscetíveis = [r['S']   for r in historico]
    infectados  = [r['I']   for r in historico]
    removidos   = [r['R']   for r in historico]

    plt.figure(figsize=(10, 5))
    plt.title("Propagação da Fake News — Modelo SIR", fontsize=14)

    plt.plot(dias, suscetíveis, color='steelblue',
             linewidth=2, label='Suscetíveis (S)')
    plt.plot(dias, infectados,  color='crimson',
             linewidth=2, label='Infectados (I)')
    plt.plot(dias, removidos,   color='gray',
             linewidth=2, label='Removidos (R)')

    plt.xlabel("Dias")
    plt.ylabel("Número de pessoas")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def animar_propagacao(rede, historico_estados, intervalo=500):
    """
    Anima a propagação na rede dia a dia.
    Azul  = Suscetível
    Vermelho = Infectado
    Cinza = Removido
    """
    cores_mapa = {
        'S': 'steelblue',
        'I': 'crimson',
        'R': 'gray'
    }

    # Posição fixa dos nós — não muda entre frames
    posicoes = nx.spring_layout(rede, seed=42)

    fig, ax = plt.subplots(figsize=(10, 7))

    def atualizar_frame(dia):
        ax.clear()
        estados_do_dia = historico_estados[dia]

        cores = [cores_mapa[estados_do_dia[n]] for n in rede.nodes()]
        tamanhos = [300 + rede.degree(n) * 80  for n in rede.nodes()]

        nx.draw(rede,
                pos=posicoes,
                node_color=cores,
                node_size=tamanhos,
                with_labels=True,
                font_size=7,
                ax=ax)

        # Conta os estados nesse dia
        s = list(estados_do_dia.values()).count('S')
        i = list(estados_do_dia.values()).count('I')
        r = list(estados_do_dia.values()).count('R')

        ax.set_title(
            f"Dia {dia}  |  "
            f"Suscetíveis: {s}  "
            f"Infectados: {i}  "
            f"Removidos: {r}",
            fontsize=12
        )

    anim = animation.FuncAnimation(
        fig,
        atualizar_frame,
        frames=len(historico_estados),
        interval=intervalo,   # milissegundos entre frames
        repeat=False
    )

    plt.tight_layout()
    plt.show()
    return anim

def plotar_comparativo(resultados):
    """
    Recebe um dicionário com os históricos de
    diferentes redes e plota lado a lado.

    Exemplo de entrada:
    {
      'Rede Centralizada': historico_a,
      'Rede Comunitária':  historico_b,
      'Rede Aleatória':    historico_c
    }
    """
    fig, eixos = plt.subplots(1, len(resultados),
                               figsize=(16, 5),
                               sharey=True)

    fig.suptitle(
        "Mesmo código — dados diferentes — comportamentos diferentes",
        fontsize=13,
        fontweight='bold'
    )

    for ax, (nome, historico) in zip(eixos, resultados.items()):
        dias        = [r['dia'] for r in historico]
        suscetíveis = [r['S']   for r in historico]
        infectados  = [r['I']   for r in historico]
        removidos   = [r['R']   for r in historico]

        ax.plot(dias, suscetíveis, color='steelblue',
                linewidth=2, label='S')
        ax.plot(dias, infectados,  color='crimson',
                linewidth=2, label='I')
        ax.plot(dias, removidos,   color='gray',
                linewidth=2, label='R')

        pico = max(infectados)
        ax.set_title(f"{nome}\nPico de infectados: {pico}",
                     fontsize=10)
        ax.set_xlabel("Dias")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)

    eixos[0].set_ylabel("Número de pessoas")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    from modelo import simular
    import networkx as nx

    rede = nx.barabasi_albert_graph(n=50, m=2, seed=42)

    # ── Teste 1: curvas SIR ───────────────────────────────────
    historico, historico_estados = simular(rede, dias=30,
                           prob_contagio=0.3,
                           prob_recuperacao=0.1)
    plotar_curvas_sir(historico)

    # ── Teste 2: animação na rede ─────────────────────────────
    historico, historico_estados = simular(rede, dias=30,
                                           prob_contagio=0.3,
                                           prob_recuperacao=0.1)
    animar_propagacao(rede, historico_estados, intervalo=400)

    # ── Teste 3: comparativo entre redes ─────────────────────
    rede_estrela     = nx.star_graph(49)
    rede_comunidades = nx.connected_caveman_graph(5, 10)
    rede_aleatoria   = nx.barabasi_albert_graph(50, 2, seed=42)

    resultados = {}

    for nome, rede_teste in [
        ('Centralizada',  rede_estrela),
        ('Comunitária',   rede_comunidades),
        ('Aleatória',     rede_aleatoria)
    ]:
        hist, _ = simular(rede_teste, dias=30,
                          prob_contagio=0.3,
                          prob_recuperacao=0.1)
        resultados[nome] = hist

    plotar_comparativo(resultados)