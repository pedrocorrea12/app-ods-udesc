import streamlit as st
import pandas as pd
import json
import pickle
import networkx as nx
from pyvis.network import Network
import tempfile, os

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="ODS · Rede de Interdependências · SC",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS customizado ─────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap');

  html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #080c14;
    color: #e2e8f0;
  }
  .stApp { background-color: #080c14; }

  section[data-testid="stSidebar"] {
    background-color: #0d1524;
    border-right: 1px solid #1e2d45;
  }
  section[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

  .hero-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.1rem;
    letter-spacing: -0.03em;
    line-height: 1.15;
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #34d399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
  }
  .hero-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: #475569;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1.8rem;
  }
  .metric-row { display: flex; gap: 12px; margin-bottom: 1.5rem; flex-wrap: wrap; }
  .metric-card {
    background: #0f1c2e;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 14px 20px;
    min-width: 110px;
    flex: 1;
  }
  .metric-val {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.9rem;
    line-height: 1;
    color: #60a5fa;
  }
  .metric-lbl {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
  }
  .legend-block {
    background: #0d1524;
    border: 1px solid #1e2d45;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 12px;
  }
  .legend-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #475569;
    margin-bottom: 10px;
  }
  .legend-item {
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 6px; font-size: 0.78rem; color: #94a3b8;
  }
  .dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
  .line-sin { width: 20px; height: 3px; background: #4ade80; border-radius: 2px; flex-shrink: 0; }
  .line-trd { width: 20px; height: 3px; background: #f87171; border-radius: 2px; flex-shrink: 0; }
  .badge {
    display: inline-block; background: #1e3a5f; color: #60a5fa;
    border-radius: 20px; padding: 2px 10px;
    font-size: 0.72rem; font-family: 'DM Mono', monospace;
    margin-right: 4px; margin-bottom: 4px;
  }
  .info-box {
    background: #0a1628; border-left: 3px solid #3b82f6;
    border-radius: 0 8px 8px 0; padding: 10px 14px;
    font-size: 0.8rem; color: #94a3b8; margin-top: 0.5rem;
    font-family: 'DM Mono', monospace; line-height: 1.6;
  }
  hr { border-color: #1e2d45; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Paletas ─────────────────────────────────────────────────────────────────
CORES_COM = {
    0:  "#3b82f6",
    1:  "#f43f5e",
    2:  "#10b981",
    3:  "#f59e0b",
    -1: "#475569",
}
CORES_ODS = {
    1:"#e5243b", 2:"#dda63a", 3:"#4c9f38", 4:"#c5192d", 5:"#ff3a21",
    6:"#26bde2", 7:"#fcc30b", 8:"#a21942", 9:"#fd6925", 10:"#dd1367",
    11:"#fd9d24", 12:"#bf8b2e", 13:"#3f7e44", 14:"#0a97d9", 15:"#56c02b",
    16:"#00689d", 17:"#19486a",
}
NOMES_COM = {
    0: "Institucional e Ambiental",
    1: "Vulnerabilidade Social",
    2: "Doenças e Resíduos",
    3: "Infraestrutura Escolar",
    -1: "Lacuna de Integração",
}

# ── Dados ────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.join(os.path.dirname(__file__), "data")
    nodes  = pd.read_csv(f"{base}/nodes.csv")
    edges  = pd.read_csv(f"{base}/edges.csv")
    perfil = pd.read_csv(f"{base}/municipios_perfil.csv")
    meta   = json.load(open(f"{base}/metadata.json"))
    return nodes, edges, perfil, meta

@st.cache_resource
def load_graph():
    base = os.path.join(os.path.dirname(__file__), "data")
    return pickle.load(open(f"{base}/graph.pkl", "rb"))

nodes_df, edges_df, perfil_df, meta = load_data()
G = load_graph()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='font-family:DM Mono,monospace;font-size:0.62rem;
         text-transform:uppercase;letter-spacing:0.12em;color:#334155;
         margin-bottom:4px;'>Sistema de Monitoramento</div>
    <div style='font-family:Syne,sans-serif;font-weight:800;font-size:1.15rem;
         color:#e2e8f0;margin-bottom:1.2rem;letter-spacing:-0.02em;
         line-height:1.3;'>ODS<br>Santa Catarina</div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    tela = st.radio("", ["🌐  A Rede", "📊  Hubs & Lacunas", "🏙️  Perfil Municipal"],
                    label_visibility="collapsed")
    st.markdown("---")

    if "A Rede" in tela:
        st.markdown("<div class='legend-title'>Filtros</div>", unsafe_allow_html=True)

        tipo_aresta = st.radio("Arestas", ["Todas", "Só Sinergias", "Só Trade-offs"],
                                horizontal=False)

        com_opcoes = ["Todas"] + [f"C{i+1} — {NOMES_COM[i]}" for i in range(4)]
        filtro_com = st.selectbox("Comunidade em foco", com_opcoes)

        ods_lista = sorted(nodes_df["ods"].unique().tolist())
        filtro_ods = st.multiselect("Destacar ODS", ods_lista,
                                     format_func=lambda x: f"ODS {x}")

        mostrar_isolados = st.checkbox("Mostrar lacunas (nós isolados)", value=True)

        bt_min = st.slider("Betweenness mínimo", 0.0, 0.10, 0.0, 0.005,
                            format="%.3f",
                            help="Filtra nós abaixo deste valor de centralidade")

        st.markdown("---")

        # Legenda comunidades
        st.markdown("<div class='legend-block'>", unsafe_allow_html=True)
        st.markdown("<div class='legend-title'>Comunidades (cor do nó)</div>",
                    unsafe_allow_html=True)
        for cid, nome in NOMES_COM.items():
            cor = CORES_COM[cid]
            st.markdown(
                f"<div class='legend-item'>"
                f"<span class='dot' style='background:{cor}'></span>"
                f"<span>{'C'+str(cid+1)+' — ' if cid >= 0 else ''}{nome}</span></div>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # Legenda arestas
        st.markdown("<div class='legend-block'>", unsafe_allow_html=True)
        st.markdown("<div class='legend-title'>Arestas (|r| ≥ 0.3, p < 0.05)</div>",
                    unsafe_allow_html=True)
        st.markdown(
            "<div class='legend-item'><span class='line-sin'></span>"
            "<span>Sinergia (r > 0)</span></div>"
            "<div class='legend-item'><span class='line-trd'></span>"
            "<span>Trade-off (r < 0)</span></div>"
            "<div style='font-size:0.68rem;color:#334155;margin-top:4px;"
            "font-family:DM Mono,monospace;'>Espessura proporcional a |r|</div>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Nota borda
        st.markdown(
            "<div style='font-size:0.68rem;color:#334155;"
            "font-family:DM Mono,monospace;line-height:1.5;'>"
            "Borda do nó = cor do ODS de origem.<br>"
            "Tamanho do nó ∝ betweenness centrality.</div>",
            unsafe_allow_html=True
        )

# ══════════════════════════════════════════════════════════════════════════════
#  TELA 1 — A REDE
# ══════════════════════════════════════════════════════════════════════════════
if "A Rede" in tela:

    st.markdown("""
    <div class='hero-title'>Rede de Interdependências ODS</div>
    <div class='hero-sub'>Santa Catarina · 295 municípios · Correlação de Spearman · Análise topológica</div>
    """, unsafe_allow_html=True)

    n_sin = len(edges_df[edges_df["tipo"] == "sinergia"])
    n_trd = len(edges_df[edges_df["tipo"] == "trade-off"])
    n_lac = len(nodes_df[nodes_df["comunidade"] == -1])

    st.markdown(f"""
    <div class='metric-row'>
      <div class='metric-card'>
        <div class='metric-val'>{meta['n_indicadores_validos']}</div>
        <div class='metric-lbl'>Indicadores</div>
      </div>
      <div class='metric-card'>
        <div class='metric-val'>{meta['n_arestas']}</div>
        <div class='metric-lbl'>Conexões</div>
      </div>
      <div class='metric-card'>
        <div class='metric-val' style='color:#4ade80'>{n_sin}</div>
        <div class='metric-lbl'>Sinergias</div>
      </div>
      <div class='metric-card'>
        <div class='metric-val' style='color:#f87171'>{n_trd}</div>
        <div class='metric-lbl'>Trade-offs</div>
      </div>
      <div class='metric-card'>
        <div class='metric-val' style='color:#a78bfa'>{meta['n_comunidades']}</div>
        <div class='metric-lbl'>Comunidades</div>
      </div>
      <div class='metric-card'>
        <div class='metric-val' style='color:#475569'>{n_lac}</div>
        <div class='metric-lbl'>Lacunas</div>
      </div>
      <div class='metric-card'>
        <div class='metric-val' style='color:#fbbf24'>{meta['modularidade']}</div>
        <div class='metric-lbl'>Modularidade</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Filtra nós ───────────────────────────────────────────────────────────
    nodes_vis = nodes_df.copy()
    if not mostrar_isolados:
        nodes_vis = nodes_vis[nodes_vis["comunidade"] != -1]
    nodes_vis = nodes_vis[nodes_vis["betweenness"] >= bt_min]
    nos_ativos = set(nodes_vis["cod_indicador"].tolist())

    # Comunidade em foco (id)
    com_foco = None
    for i in range(4):
        if f"C{i+1}" in filtro_com:
            com_foco = i
            break

    # ── Filtra arestas ───────────────────────────────────────────────────────
    edges_vis = edges_df.copy()
    if tipo_aresta == "Só Sinergias":
        edges_vis = edges_vis[edges_vis["tipo"] == "sinergia"]
    elif tipo_aresta == "Só Trade-offs":
        edges_vis = edges_vis[edges_vis["tipo"] == "trade-off"]
    edges_vis = edges_vis[
        edges_vis["source"].isin(nos_ativos) &
        edges_vis["target"].isin(nos_ativos)
    ]

    # ── PyVis ────────────────────────────────────────────────────────────────
    net = Network(
        height="680px", width="100%",
        bgcolor="#080c14", font_color="#cbd5e1",
        directed=False,
    )
    net.barnes_hut(
        gravity=-4200, central_gravity=0.35,
        spring_length=150, spring_strength=0.05, damping=0.09,
    )

    for _, row in nodes_vis.iterrows():
        cod      = row["cod_indicador"]
        nome     = row["nome_indicador"]
        ods      = int(row["ods"])
        com_id   = int(row["comunidade"])
        bt       = float(row["betweenness"])
        degree     = int(row["degree"])
        com_nome = row["comunidade_nome"]
        eigenv   = float(row["eigenvector"])

        cor_no    = CORES_COM.get(com_id, "#475569")
        cor_borda = CORES_ODS.get(ods, "#94a3b8")
        tamanho   = 10 + bt * 380

        # Opacidade: destaca ODS ou comunidade selecionada
        opaco = False
        if filtro_ods and ods not in filtro_ods:
            opaco = True
        if com_foco is not None and com_id != com_foco and com_id != -1:
            opaco = True

        tooltip = (
            f"<div style='font-family:monospace;font-size:12px;"
            f"background:#0d1524;padding:12px;border-radius:8px;"
            f"border:1px solid #1e3a5f;max-width:300px;line-height:1.6;'>"
            f"<b style='color:#60a5fa;font-size:13px;'>{nome}</b><br>"
            f"<span style='color:#64748b;font-size:11px;'>ODS {ods} · {com_nome}</span>"
            f"<hr style='border-color:#1e3a5f;margin:8px 0;'>"
            f"<span style='color:#94a3b8;'>Betweenness: </span>"
            f"<b style='color:#e2e8f0;'>{bt:.4f}</b><br>"
            f"<span style='color:#94a3b8;'>Eigenvector: </span>"
            f"<b style='color:#e2e8f0;'>{eigenv:.4f}</b><br>"
            f"<span style='color:#94a3b8;'>Conexões (degree): </span>"
            f"<b style='color:#e2e8f0;'>{degree}</b>"
            f"</div>"
        )

        net.add_node(
            cod,
            label=nome[:26] + "…" if len(nome) > 26 else nome,
            title=tooltip,
            color={
                "background": cor_no if not opaco else "#1e293b",
                "border": cor_borda if not opaco else "#334155",
                "highlight": {"background": "#fbbf24", "border": "#f59e0b"},
                "hover": {"background": "#a78bfa", "border": "#7c3aed"},
            },
            size=tamanho,
            borderWidth=2.5 if (filtro_ods and ods in filtro_ods) else 1.5,
            font={
                "size": 8 if opaco else 9,
                "color": "#334155" if opaco else "#e2e8f0",
                "face": "monospace",
            },
            opacity=0.3 if opaco else 1.0,
        )

    for _, row in edges_vis.iterrows():
        src = row["source"]
        tgt = row["target"]
        r   = float(row["r"])
        tp  = row["tipo"]

        cor = "#4ade80" if tp == "sinergia" else "#f87171"
        largura = 0.4 + abs(r) * 5.5

        # Esmaecer arestas entre ODS/comunidades não focadas
        opaco_e = False
        if filtro_ods:
            src_ods = nodes_df.loc[nodes_df["cod_indicador"]==src, "ods"]
            tgt_ods = nodes_df.loc[nodes_df["cod_indicador"]==tgt, "ods"]
            if not src_ods.empty and not tgt_ods.empty:
                if (src_ods.values[0] not in filtro_ods and
                    tgt_ods.values[0] not in filtro_ods):
                    opaco_e = True

        net.add_edge(
            src, tgt,
            title=(f"<div style='font-family:monospace;font-size:11px;"
                   f"background:#0d1524;padding:8px;border-radius:6px;"
                   f"border:1px solid #1e3a5f;'>"
                   f"<b style='color:{'#4ade80' if tp=='sinergia' else '#f87171'}'>"
                   f"{'Sinergia' if tp=='sinergia' else 'Trade-off'}</b><br>"
                   f"r = <b style='color:#e2e8f0'>{r:+.3f}</b></div>"),
            color={"color": cor, "opacity": 0.15 if opaco_e else 0.55},
            width=largura,
        )

    net.set_options("""
    {
      "interaction": {
        "hover": true,
        "tooltipDelay": 60,
        "hideEdgesOnDrag": true,
        "multiselect": false,
        "navigationButtons": false,
        "keyboard": { "enabled": true }
      },
      "physics": {
        "enabled": true,
        "stabilization": { "iterations": 150, "updateInterval": 25 }
      },
      "nodes": {
        "shadow": { "enabled": true, "size": 14, "color": "rgba(0,0,0,0.6)" },
        "scaling": { "min": 8, "max": 50 }
      },
      "edges": {
        "shadow": false,
        "smooth": { "enabled": true, "type": "dynamic" },
        "scaling": { "min": 0.5, "max": 8 }
      }
    }
    """)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w") as f:
        tmp_path = f.name
    net.save_graph(tmp_path)
    with open(tmp_path, "r", encoding="utf-8") as f:
        html_rede = f.read()
    os.unlink(tmp_path)

    html_rede = html_rede.replace(
        "<body>",
        "<body style='background:#080c14;margin:0;padding:0;overflow:hidden;'>"
    )

    st.components.v1.html(html_rede, height=690, scrolling=False)

    st.markdown("""
    <div class='info-box'>
      💡 <b>Interação:</b> arraste para mover · scroll para zoom ·
      clique num nó para ver métricas · use os filtros no menu lateral
      para isolar comunidades, ODS específicos ou tipo de conexão ·
      teclas +/− também funcionam para zoom.
    </div>
    """, unsafe_allow_html=True)

    # Badges de filtros ativos
    ativos = []
    if tipo_aresta != "Todas":  ativos.append(tipo_aresta)
    if filtro_ods:              ativos += [f"ODS {o}" for o in filtro_ods]
    if com_foco is not None:    ativos.append(f"C{com_foco+1} em foco")
    if bt_min > 0:              ativos.append(f"bt ≥ {bt_min:.3f}")
    if not mostrar_isolados:    ativos.append("sem lacunas")

    if ativos:
        badges = "".join(f"<span class='badge'>{a}</span>" for a in ativos)
        st.markdown(
            f"<div style='margin-top:10px;'>"
            f"<span style='font-family:DM Mono,monospace;font-size:0.65rem;"
            f"color:#334155;text-transform:uppercase;letter-spacing:0.08em;"
            f"margin-right:8px;'>Filtros ativos</span>{badges}</div>",
            unsafe_allow_html=True
        )

# ══════════════════════════════════════════════════════════════════════════════
#  TELA 2 — HUBS & LACUNAS
# ══════════════════════════════════════════════════════════════════════════════
elif "Hubs" in tela:
    st.markdown("""
    <div class='hero-title'>Hubs & Lacunas</div>
    <div class='hero-sub'>Centralidade dos indicadores e dimensões estruturalmente isoladas</div>
    """, unsafe_allow_html=True)
    st.info("🚧 Tela 2 — em construção na próxima sessão.")

# ══════════════════════════════════════════════════════════════════════════════
#  TELA 3 — PERFIL MUNICIPAL
# ══════════════════════════════════════════════════════════════════════════════
elif "Perfil" in tela:
    st.markdown("""
    <div class='hero-title'>Perfil Municipal</div>
    <div class='hero-sub'>Situação do município na rede de indicadores ODS</div>
    """, unsafe_allow_html=True)
    st.info("🚧 Tela 3 — em construção na próxima sessão.")
