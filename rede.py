import networkx as nx
import matplotlib.pyplot as plt
import random


# ── Criação da rede ───────────────────────────────────────────

def criar_rede(n=100, m=2, seed=42):
    """
    Cria uma rede Barabási-Albert e enriquece
    cada nó com atributos individuais.
    """
    rede = nx.barabasi_albert_graph(n=n, m=m, seed=seed)
    rede = atribuir_perfis(rede)
    return rede


def atribuir_perfis(rede):
    """
    Adiciona atributos individuais a cada nó.

    A credulidade é inversamente proporcional
    ao número de conexões — influencers tendem
    a ser mais céticos porque estão mais expostos
    a conteúdo variado.
    """
    max_conexoes = max(dict(rede.degree()).values())

    for no in rede.nodes():
        conexoes = rede.degree(no)

        # Influencers (muitas conexões) são mais céticos
        # Usuários comuns (poucas conexões) são mais crédulos
        credulidade_base = 1 - (conexoes / max_conexoes)

        # Adiciona variação aleatória realista
        credulidade = max(0.05, min(0.95,
                                    credulidade_base + random.uniform(-0.15, 0.15)
                                    ))

        # Influencia: proporcional às conexões
        # quem tem mais seguidores convence mais
        influencia = min(0.95,
                         (conexoes / max_conexoes) + random.uniform(0.0, 0.2)
                         )

        # Ativo: 70% dos usuários são ativos
        ativo = random.random() < 0.7

        rede.nodes[no]['credulidade'] = round(credulidade, 3)
        rede.nodes[no]['influencia'] = round(influencia, 3)
        rede.nodes[no]['ativo'] = ativo
        rede.nodes[no]['conexoes'] = conexoes

    return rede


# ── Utilitários ───────────────────────────────────────────────

def get_influencers(rede, top_n=5):
    """
    Retorna os nós mais conectados da rede —
    os 'influencers'.
    """
    return sorted(
        rede.nodes(),
        key=lambda n: rede.degree(n),
        reverse=True
    )[:top_n]


def get_periferico(rede):
    """
    Retorna o nó menos conectado da rede.
    """
    return min(rede.nodes(), key=lambda n: rede.degree(n))


def estatisticas_rede(rede):
    """
    Imprime um resumo dos atributos da rede.
    """
    credulidades = [rede.nodes[n]['credulidade'] for n in rede.nodes()]
    influencias = [rede.nodes[n]['influencia'] for n in rede.nodes()]
    ativos = [n for n in rede.nodes() if rede.nodes[n]['ativo']]
    influencers = get_influencers(rede)

    print("\nEstatísticas da Rede:")
    print(f"  Nós (pessoas)          : {rede.number_of_nodes()}")
    print(f"  Arestas (conexões)     : {rede.number_of_edges()}")
    print(f"  Usuários ativos        : {len(ativos)} "
          f"({100 * len(ativos) // rede.number_of_nodes()}%)")
    print(f"  Credulidade média      : "
          f"{sum(credulidades) / len(credulidades):.3f}")
    print(f"  Influência média       : "
          f"{sum(influencias) / len(influencias):.3f}")

    print(f"\n  Top 5 influencers:")
    for no in influencers:
        dados = rede.nodes[no]
        print(f"    Nó {no:>3} | "
              f"conexões: {dados['conexoes']:>3} | "
              f"credulidade: {dados['credulidade']:.3f} | "
              f"influência: {dados['influencia']:.3f}")


# ── Visualização ──────────────────────────────────────────────

def desenhar_rede(rede, atributo='credulidade'):
    """
    Desenha a rede colorindo os nós pelo atributo escolhido.
    Quanto mais vermelho, maior o valor do atributo.
    """
    valores = [rede.nodes[n][atributo] for n in rede.nodes()]
    tamanhos = [300 + rede.degree(n) * 80 for n in rede.nodes()]

    plt.figure(figsize=(12, 8))
    plt.title(f"Rede Social — nós coloridos por '{atributo}'\n"
              f"(vermelho = alto | azul = baixo)", fontsize=12)

    pos = nx.spring_layout(rede, seed=42)

    nos = nx.draw_networkx_nodes(
        rede, pos,
        node_color=valores,
        node_size=tamanhos,
        cmap=plt.cm.RdYlBu_r,  # azul → amarelo → vermelho
        vmin=0, vmax=1
    )
    nx.draw_networkx_edges(rede, pos, alpha=0.2)
    nx.draw_networkx_labels(rede, pos, font_size=6)

    plt.colorbar(nos, label=atributo)
    plt.axis('off')
    plt.tight_layout()
    plt.show()


# ── Teste ─────────────────────────────────────────────────────

if __name__ == "__main__":
    random.seed(42)

    rede = criar_rede(n=100, m=2, seed=42)
    estatisticas_rede(rede)

    print("\nDesenhando rede colorida por credulidade...")
    desenhar_rede(rede, atributo='credulidade')

    print("Desenhando rede colorida por influência...")
    desenhar_rede(rede, atributo='influencia')