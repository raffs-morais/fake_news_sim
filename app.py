import streamlit as st
import matplotlib
matplotlib.use('Agg')  # backend não-interativo — obrigatório no Streamlit
import matplotlib.pyplot as plt
import networkx as nx
import random
import time

from rede import criar_rede, get_influencers, get_periferico
from modelo import simular

# ── Configuração da página ────────────────────────────────────
st.set_page_config(
    page_title="Simulador de Fake News",
    page_icon="🦠",
    layout="wide"
)

# ── CSS customizado ───────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 2rem; }
    .block-container { padding-top: 1.5rem; }
    h1 { font-size: 1.6rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state — preserva dados entre reruns ───────────────
for chave in ['historico', 'historico_estados', 'rede',
              'no_inicial', 'simulado']:
    if chave not in st.session_state:
        st.session_state[chave] = None

if 'simulado' not in st.session_state:
    st.session_state.simulado = False


# ── Funções de plotagem (retornam fig, não usam plt.show) ─────

CORES_SIR = {'S': 'steelblue', 'I': 'crimson', 'R': 'gray'}


def fig_rede(rede, estados, titulo=''):
    pos = nx.spring_layout(rede, seed=42)
    cores   = [CORES_SIR[estados[n]] for n in rede.nodes()]
    tamanhos = [200 + rede.degree(n) * 60 for n in rede.nodes()]

    fig, ax = plt.subplots(figsize=(7, 5))
    nx.draw(rede, pos=pos,
            node_color=cores,
            node_size=tamanhos,
            ax=ax,
            with_labels=False,
            edge_color='#cccccc',
            width=0.5)

    if titulo:
        ax.set_title(titulo, fontsize=11)

    fig.patch.set_alpha(0)
    return fig


def fig_curvas_sir(historico):
    dias = [r['dia'] for r in historico]
    s    = [r['S']   for r in historico]
    i    = [r['I']   for r in historico]
    r    = [r['R']   for r in historico]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(dias, s, color='steelblue', linewidth=2, label='Suscetíveis (S)')
    ax.plot(dias, i, color='crimson',   linewidth=2, label='Infectados (I)')
    ax.plot(dias, r, color='gray',      linewidth=2, label='Removidos (R)')
    ax.set_xlabel("Dias")
    ax.set_ylabel("Pessoas")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.patch.set_alpha(0)
    return fig


def fig_comparativo(resultados):
    n = len(resultados)
    fig, eixos = plt.subplots(1, n, figsize=(5 * n, 4), sharey=True)

    if n == 1:
        eixos = [eixos]

    for ax, (nome, historico) in zip(eixos, resultados.items()):
        dias = [r['dia'] for r in historico]
        ax.plot(dias, [r['S'] for r in historico],
                color='steelblue', linewidth=1.8, label='S')
        ax.plot(dias, [r['I'] for r in historico],
                color='crimson',   linewidth=1.8, label='I')
        ax.plot(dias, [r['R'] for r in historico],
                color='gray',      linewidth=1.8, label='R')

        pico = max(r['I'] for r in historico)
        ax.set_title(f"{nome}\nPico: {pico}", fontsize=10)
        ax.set_xlabel("Dias")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)

    eixos[0].set_ylabel("Pessoas")
    fig.tight_layout()
    fig.patch.set_alpha(0)
    return fig


def fig_sensibilidade(probs, picos):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(probs, picos,
            marker='o', color='crimson', linewidth=2, markersize=6)
    ax.set_xlabel("Probabilidade de Contágio")
    ax.set_ylabel("Pico de Infectados")
    ax.set_title("Efeito da Probabilidade de Contágio")
    ax.grid(True, alpha=0.3)
    fig.patch.set_alpha(0)
    return fig


# ═════════════════════════════════════════════════════════════
# SIDEBAR — Parâmetros e botão Simular
# ═════════════════════════════════════════════════════════════

with st.sidebar:
    st.title("⚙️ Parâmetros")
    st.divider()

    prob_contagio    = st.slider("Probabilidade de Contágio",
                                  0.01, 1.0, 0.30, 0.01)
    prob_recuperacao = st.slider("Probabilidade de Recuperação",
                                  0.01, 1.0, 0.10, 0.01)
    tamanho_rede     = st.slider("Tamanho da Rede (nós)",
                                  20, 200, 100, 10)
    dias             = st.slider("Número de Dias",
                                  10, 100, 50, 5)

    st.divider()
    tipo_pz = st.selectbox(
        "Paciente Zero",
        ["Influencer (mais conectado)",
         "Aleatório",
         "Periférico (menos conectado)"]
    )

    st.divider()

    if st.button("🚀 Simular", use_container_width=True, type="primary"):
        with st.spinner("Simulando..."):
            rede = criar_rede(n=tamanho_rede, m=2, seed=42)

            if "Influencer" in tipo_pz:
                no_inicial = get_influencers(rede, top_n=1)[0]
            elif "Periférico" in tipo_pz:
                no_inicial = get_periferico(rede)
            else:
                no_inicial = random.choice(list(rede.nodes()))

            historico, historico_estados = simular(
                rede,
                no_inicial=no_inicial,
                dias=dias,
                prob_contagio=prob_contagio,
                prob_recuperacao=prob_recuperacao
            )

            st.session_state.rede              = rede
            st.session_state.historico         = historico
            st.session_state.historico_estados = historico_estados
            st.session_state.no_inicial        = no_inicial
            st.session_state.simulado          = True

        st.success("Simulação concluída!")

    st.divider()
    st.caption("INF0288 — Linguagens e Paradigmas de Programação\n\n"
               "Paradigma Orientado a Dados | Modelo SIR")


# ═════════════════════════════════════════════════════════════
# CABEÇALHO
# ═════════════════════════════════════════════════════════════

st.title("🦠 Simulador de Propagação de Fake News")
st.caption("Modelo SIR em rede Barabási-Albert com credulidade individual")

tab_sim, tab_exp, tab_sobre = st.tabs([
    "📊 Simulação",
    "🔬 Experimentos",
    "ℹ️ Sobre o Projeto"
])


# ═════════════════════════════════════════════════════════════
# TAB 1 — SIMULAÇÃO
# ═════════════════════════════════════════════════════════════

with tab_sim:
    if not st.session_state.simulado:
        st.info("👈 Configure os parâmetros na barra lateral e clique em **Simular**.")

    else:
        historico         = st.session_state.historico
        historico_estados = st.session_state.historico_estados
        rede              = st.session_state.rede
        no_inicial        = st.session_state.no_inicial

        # ── Métricas ─────────────────────────────────────────
        pico         = max(r['I'] for r in historico)
        total        = max(r['I'] + r['R'] for r in historico)
        dia_pico     = next(r['dia'] for r in historico if r['I'] == pico)
        nao_atingidos = tamanho_rede - total
        duracao      = historico[-1]['dia']

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("🔴 Pico de Infectados", pico)
        c2.metric("👥 Total Atingido",     total)
        c3.metric("📅 Dia do Pico",        dia_pico)
        c4.metric("🛡️ Nunca Atingidos",   nao_atingidos)
        c5.metric("⏱️ Duração",            f"{duracao} dias")

        st.divider()

        # ── Rede + Curvas lado a lado ─────────────────────────
        col_rede, col_curva = st.columns([1.1, 1])

        with col_rede:
            st.subheader("Estado Final da Rede")
            st.caption("🔵 Suscetível  🔴 Infectado  ⚫ Removido")
            estados_finais = historico_estados[-1]
            fig = fig_rede(rede, estados_finais)
            st.pyplot(fig)
            plt.close(fig)

            # Info do paciente zero
            dados_pz = rede.nodes[no_inicial]
            st.info(
                f"**Paciente zero:** nó {no_inicial}  \n"
                f"Conexões: {rede.degree(no_inicial)}  |  "
                f"Credulidade: {dados_pz.get('credulidade', '—'):.3f}  |  "
                f"Influência: {dados_pz.get('influencia', '—'):.3f}"
            )

        with col_curva:
            st.subheader("Curvas SIR")
            fig = fig_curvas_sir(historico)
            st.pyplot(fig)
            plt.close(fig)

        st.divider()

        # ── Animação ──────────────────────────────────────────
        st.subheader("🎬 Animação da Propagação")

        vel_col, _ = st.columns([1, 2])
        with vel_col:
            velocidade = st.select_slider(
                "Velocidade",
                options=["Devagar (0.5s)", "Normal (0.2s)", "Rápido (0.05s)"],
                value="Normal (0.2s)"
            )
        vel_map = {
            "Devagar (0.5s)": 0.5,
            "Normal (0.2s)" : 0.2,
            "Rápido (0.05s)": 0.05
        }

        if st.button("▶️ Animar"):
            placeholder  = st.empty()
            barra        = st.progress(0)
            pos          = nx.spring_layout(rede, seed=42)
            total_frames = len(historico_estados)

            for dia, estados_dia in enumerate(historico_estados):
                s = list(estados_dia.values()).count('S')
                i = list(estados_dia.values()).count('I')
                r = list(estados_dia.values()).count('R')

                titulo = (f"Dia {dia}  |  "
                          f"Suscetíveis: {s}   "
                          f"Infectados: {i}   "
                          f"Removidos: {r}")

                fig = fig_rede(rede, estados_dia, titulo=titulo)
                placeholder.pyplot(fig)
                plt.close(fig)

                barra.progress((dia + 1) / total_frames)
                time.sleep(vel_map[velocidade])

                if i == 0 and dia > 0:
                    break

            barra.empty()
            st.success(f"Fake news extinta no dia {dia}. "
                       f"{r} pessoas foram atingidas no total.")


# ═════════════════════════════════════════════════════════════
# TAB 2 — EXPERIMENTOS
# ═════════════════════════════════════════════════════════════

with tab_exp:
    st.subheader("🔬 Experimentos Científicos")
    st.caption("Cada experimento varia um fator mantendo os demais fixos. "
               "Os resultados demonstram o argumento central do paradigma "
               "data-driven: os dados determinam o comportamento.")

    exp1, exp2, exp3 = st.tabs([
        "Probabilidade de Contágio",
        "Estrutura da Rede",
        "Paciente Zero"
    ])

    # ── Experimento 1 ─────────────────────────────────────────
    with exp1:
        st.markdown(
            "**Pergunta:** a partir de qual probabilidade de contágio "
            "a fake news se torna uma epidemia?"
        )

        if st.button("▶️ Rodar Experimento 1", key="btn_exp1"):
            rede_exp = criar_rede(n=100, m=2, seed=42)
            probabilidades = [0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50]
            probs, picos   = [], []

            barra = st.progress(0)
            for idx, prob in enumerate(probabilidades):
                hist, _ = simular(rede_exp, dias=50,
                                  prob_contagio=prob,
                                  prob_recuperacao=0.1)
                pico = max(r['I'] for r in hist)
                probs.append(prob)
                picos.append(pico)
                barra.progress((idx + 1) / len(probabilidades))

            barra.empty()

            col_tab, col_graf = st.columns([1, 1.5])
            with col_tab:
                st.markdown("**Resultados:**")
                for p, pk in zip(probs, picos):
                    st.write(f"prob = {p:.2f} → pico: **{pk}** pessoas")

            with col_graf:
                fig = fig_sensibilidade(probs, picos)
                st.pyplot(fig)
                plt.close(fig)

            st.info(
                "**Conclusão:** existe um limiar crítico entre 0.10 e 0.20 "
                "onde a fake news passa de propagação local para epidemia. "
                "Abaixo desse limiar ela se extingue rapidamente."
            )

    # ── Experimento 2 ─────────────────────────────────────────
    with exp2:
        st.markdown(
            "**Pergunta:** a estrutura da rede importa mais do que "
            "os parâmetros individuais de comportamento?"
        )

        if st.button("▶️ Rodar Experimento 2", key="btn_exp2"):
            redes_teste = {
                'Centralizada\n(Estrela)'  : nx.star_graph(99),
                'Comunitária\n(Caveman)'   : nx.connected_caveman_graph(10, 10),
                'Barabási-Albert'          : nx.barabasi_albert_graph(100, 2, seed=42),
                'Aleatória\n(Erdős-Rényi)' : nx.erdos_renyi_graph(100, 0.04, seed=42)
            }

            historicos = {}
            barra = st.progress(0)

            for idx, (nome, rede_t) in enumerate(redes_teste.items()):
                hist, _ = simular(rede_t, dias=50,
                                  prob_contagio=0.3,
                                  prob_recuperacao=0.1)
                historicos[nome] = hist
                barra.progress((idx + 1) / len(redes_teste))

            barra.empty()

            fig = fig_comparativo(historicos)
            st.pyplot(fig)
            plt.close(fig)

            # Tabela de resultados
            st.markdown("**Comparativo:**")
            cols = st.columns(len(redes_teste))
            for col, (nome, hist) in zip(cols, historicos.items()):
                pico  = max(r['I'] for r in hist)
                total = max(r['I'] + r['R'] for r in hist)
                col.metric(
                    nome.replace('\n', ' '),
                    f"Pico: {pico}",
                    f"Total: {total}"
                )

            st.info(
                "**Conclusão:** o mesmo código com dados de rede diferentes "
                "produz comportamentos completamente diferentes. "
                "Isso é o paradigma data-driven em ação."
            )

    # ── Experimento 3 ─────────────────────────────────────────
    with exp3:
        st.markdown(
            "**Pergunta:** uma fake news postada por um influencer "
            "tem muito mais impacto do que a mesma postada por "
            "um usuário comum?"
        )

        if st.button("▶️ Rodar Experimento 3", key="btn_exp3"):
            rede_exp3   = criar_rede(n=100, m=2, seed=42)
            influencer  = get_influencers(rede_exp3, top_n=1)[0]
            periferico  = get_periferico(rede_exp3)
            aleatorio   = list(rede_exp3.nodes())[50]

            cenarios = {
                f"Influencer\n(nó {influencer}, "
                f"{rede_exp3.degree(influencer)} conexões)": influencer,

                f"Aleatório\n(nó {aleatorio}, "
                f"{rede_exp3.degree(aleatorio)} conexões)"  : aleatorio,

                f"Periférico\n(nó {periferico}, "
                f"{rede_exp3.degree(periferico)} conexões)" : periferico
            }

            historicos3 = {}
            barra = st.progress(0)

            for idx, (desc, no_i) in enumerate(cenarios.items()):
                hist, _ = simular(rede_exp3, no_inicial=no_i,
                                  dias=50, prob_contagio=0.3,
                                  prob_recuperacao=0.1)
                historicos3[desc] = hist
                barra.progress((idx + 1) / len(cenarios))

            barra.empty()

            fig = fig_comparativo(historicos3)
            st.pyplot(fig)
            plt.close(fig)

            pico_inf = max(r['I'] for r in historicos3[list(cenarios.keys())[0]])
            pico_per = max(r['I'] for r in historicos3[list(cenarios.keys())[2]])
            razao    = round(pico_inf / pico_per, 1) if pico_per > 0 else "∞"

            st.info(
                f"**Conclusão:** a fake news postada pelo influencer causou "
                f"um pico **{razao}x maior** do que a postada pelo usuário "
                f"periférico — com o mesmo código e os mesmos parâmetros. "
                f"Só o ponto de origem nos dados mudou."
            )


# ═════════════════════════════════════════════════════════════
# TAB 3 — SOBRE O PROJETO
# ═════════════════════════════════════════════════════════════

with tab_sobre:
    st.subheader("Sobre o Projeto")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""
**Disciplina:** INF0288 — Linguagens e Paradigmas de Programação  
**Paradigma:** Orientado a Dados (*Data-Driven Programming*)  
**Linguagem:** Python  

---

**O que é o Paradigma Orientado a Dados?**

Em vez de programar regras fixas de comportamento, os dados
determinam o que o programa faz. O mesmo código com dados
diferentes produz resultados completamente diferentes.

Neste projeto, o comportamento da fake news não é programado
manualmente — ele emerge da estrutura da rede e dos atributos
individuais de cada usuário.

---

**Modelo SIR**

Cada pessoa está em um de três estados:
- 🔵 **S — Suscetível:** ainda não viu a fake news
- 🔴 **I — Infectado:** acredita e está compartilhando
- ⚫ **R — Removido:** parou de compartilhar
        """)

    with col_b:
        st.markdown("""
**Estrutura do Projeto**

| Arquivo | Responsabilidade |
|---|---|
| `rede.py` | Cria e enriquece o grafo com atributos individuais |
| `modelo.py` | Lógica SIR com credulidade individual |
| `visualizacao.py` | Gráficos e animações (terminal) |
| `experimentos.py` | Experimentos científicos (terminal) |
| `main.py` | Menu interativo no terminal |
| `app.py` | Interface web (Streamlit) |

---

**Inovações implementadas**

- **Credulidade individual:** cada nó tem sua própria probabilidade
  de acreditar em fake news
- **Influência individual:** nós mais conectados propagam mais
- **Usuários inativos:** 30% dos nós têm acesso reduzido ao conteúdo
- **Rede Barabási-Albert:** imita a distribuição real de seguidores
  em redes sociais (poucos com muitas conexões, muitos com poucas)
        """)

    st.divider()
    st.caption("Desenvolvido para o Seminário Final de LPP — UFG")