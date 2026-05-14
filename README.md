# ODS · Rede de Interdependências · Santa Catarina

Protótipo funcional — Dissertação de Mestrado
João Pedro Corrêa Pereira / PGCIN-UFSC

## Como rodar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Rodar o app
streamlit run app.py
```

O app abre automaticamente em http://localhost:8501

## Estrutura

```
ods_app/
├── app.py                  # Aplicação principal
├── requirements.txt        # Dependências
└── data/
    ├── nodes.csv           # 54 indicadores + métricas topológicas
    ├── edges.csv           # 154 arestas (sinergias e trade-offs)
    ├── municipios_perfil.csv # 295 municípios × semáforo por indicador
    ├── graph.pkl           # Grafo NetworkX serializado
    └── metadata.json       # Metadados do projeto
```

## Telas
- **Tela 1 — A Rede**: grafo interativo com filtros por comunidade, ODS e tipo de aresta
- **Tela 2 — Hubs & Lacunas**: tabela de centralidade (em construção)
- **Tela 3 — Perfil Municipal**: semáforo por município (em construção)
