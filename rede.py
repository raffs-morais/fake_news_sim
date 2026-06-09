import networkx as nx
import matplotlib.pyplot as plt

def criar_rede_teste():
    # Rede Barabási-Albert: imita redes sociais reais
    # 50 pessoas, cada nova conecta com 2 existentes
    rede = nx.barabasi_albert_graph(n=50, m=2)
    return rede

def desenhar_rede(rede):
    plt.figure(figsize=(10, 7))
    plt.title("Rede Social - Estrutura Inicial")

    # Tamanho do nó proporcional ao número de conexões
    tamanhos = [rede.degree(n) * 100 for n in rede.nodes()]

    nx.draw(rede,
            node_size=tamanhos,
            node_color='lightblue',
            with_labels=True,
            font_size=7)

    plt.show()

# Teste
rede = criar_rede_teste()
print(f"Nós (pessoas): {rede.number_of_nodes()}")
print(f"Arestas (conexões): {rede.number_of_edges()}")
desenhar_rede(rede)