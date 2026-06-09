from modelo import simular
from vizualizacao import (plotar_curvas_sir,
                           animar_propagacao,
                           plotar_comparativo)
from experimentos import (experimento_prob_contagio,
                           experimento_estrutura_rede,
                           experimento_paciente_zero)
import networkx as nx


# ── Configurações padrão ──────────────────────────────────────
PROB_CONTAGIO   = 0.3
PROB_RECUPERACAO = 0.1
DIAS            = 50
TAMANHO_REDE    = 100


def cabecalho():
    print("""
╔══════════════════════════════════════════════════════════╗
║     SIMULADOR DE PROPAGAÇÃO DE FAKE NEWS                 ║
║     Paradigma Orientado a Dados — Data-Driven            ║                                                          
╚══════════════════════════════════════════════════════════╝
    """)


def menu():
    print("""
Escolha uma opção:
──────────────────────────────────────────────────────────
  [1] Simulação básica com curvas SIR
  [2] Animação da propagação na rede
  [3] Comparativo entre estruturas de rede
  [4] Experimento — efeito da prob. de contágio
  [5] Experimento — efeito da estrutura da rede
  [6] Experimento — efeito do paciente zero
  [7] Rodar todos os experimentos em sequência
  [0] Sair
──────────────────────────────────────────────────────────""")
    return input("  Opção: ").strip()


def criar_rede_padrao():
    return nx.barabasi_albert_graph(
        n=TAMANHO_REDE,
        m=2,
        seed=42
    )


def opcao_1():
    print("\nRodando simulação básica...")
    rede = criar_rede_padrao()
    historico, _ = simular(
        rede,
        dias=DIAS,
        prob_contagio=PROB_CONTAGIO,
        prob_recuperacao=PROB_RECUPERACAO
    )

    pico = max(r['I'] for r in historico)
    total = max(r['I'] + r['R'] for r in historico)
    print(f"\nResultados:")
    print(f"  Pico de infectados : {pico} pessoas")
    print(f"  Total atingido     : {total} pessoas")
    print(f"  Nunca atingidos    : {TAMANHO_REDE - total} pessoas")

    plotar_curvas_sir(historico)


def opcao_2():
    print("\nRodando animação — isso pode demorar alguns segundos...")
    rede = criar_rede_padrao()
    historico, historico_estados = simular(
        rede,
        dias=DIAS,
        prob_contagio=PROB_CONTAGIO,
        prob_recuperacao=PROB_RECUPERACAO
    )
    animar_propagacao(rede, historico_estados, intervalo=300)


def opcao_3():
    print("\nComparando estruturas de rede...")
    redes = {
        'Centralizada' : nx.star_graph(TAMANHO_REDE - 1),
        'Comunitária'  : nx.connected_caveman_graph(10, 10),
        'Barabási'     : nx.barabasi_albert_graph(TAMANHO_REDE, 2, seed=42),
        'Aleatória'    : nx.erdos_renyi_graph(TAMANHO_REDE, 0.04, seed=42)
    }

    historicos = {}
    for nome, rede in redes.items():
        hist, _ = simular(
            rede,
            dias=DIAS,
            prob_contagio=PROB_CONTAGIO,
            prob_recuperacao=PROB_RECUPERACAO
        )
        historicos[nome] = hist

    plotar_comparativo(historicos)


def opcao_7():
    print("\nRodando todos os experimentos em sequência...")
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


# ── Loop principal ────────────────────────────────────────────

def main():
    cabecalho()

    acoes = {
        '1': opcao_1,
        '2': opcao_2,
        '3': opcao_3,
        '4': experimento_prob_contagio,
        '5': experimento_estrutura_rede,
        '6': experimento_paciente_zero,
        '7': opcao_7
    }

    while True:
        escolha = menu()

        if escolha == '0':
            print("\nEncerrando o simulador. Até mais!\n")
            break
        elif escolha in acoes:
            acoes[escolha]()
        else:
            print("\nOpção inválida. Tente novamente.")


if __name__ == "__main__":
    main()