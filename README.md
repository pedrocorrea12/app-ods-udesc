# app-ods-udesc

Rede de associações entre indicadores ODS de Santa Catarina: protótipo navegável desenvolvido como prova de conceito da pesquisa de mestrado *Arquitetura de representação relacional de indicadores ODS: protótipo baseado em redes complexas para Santa Catarina* (PPGInfo/UDESC).

**Acesse:** https://pedrocorrea12.github.io/app-ods-udesc/

## Conteúdo

| Arquivo | Descrição |
|---|---|
| `index.html` | Protótipo navegável da rede (página única, sem dependências externas). |
| `notebook/mestrado_rede_indicadores_ods_sc.ipynb` | Notebook (Google Colab) com o procedimento analítico que gera a rede. |

## Dados e método

- **Fonte:** Índice de Desenvolvimento Sustentável das Cidades, Brasil (IDSC-BR), planilha de séries temporais.
- **Recorte:** os 295 municípios de Santa Catarina, com registros de 2010 a 2025 (14 anos disponíveis).
- **Seleção:** indicadores com cobertura mínima de 57%, o que resulta em 53 dos 100 indicadores.
- **Agregação:** média municipal de cada indicador, sem padronização.
- **Associações:** correlação de Spearman entre os 1.378 pares de indicadores. Um par vira aresta quando |r| ≥ 0,3 e p < 0,05, o que resulta em 152 arestas (82 positivas e 70 negativas).
- **Métricas:** grau e centralidade de intermediação, comunidades pelo algoritmo de Louvain (100 execuções, estabilidade medida por NMI) e comparação com 1.000 redes Erdős–Rényi.

As arestas representam associações estatísticas, não relações causais. O sinal da correlação indica a direção da associação e não equivale, por si só, a sinergia ou trade-off.

## Como usar o protótipo

- Clique em um indicador para ver suas associações, com o valor de r, e suas métricas.
- Alterne a cor dos nós entre comunidade e ODS, e filtre as associações positivas ou negativas.
- Use a roda do mouse para dar zoom e arraste para mover a rede.

## Reproduzir a análise

Abra o notebook no Google Colab e ajuste as variáveis `BASE` (pasta com `base_dados_idsc_sc.xlsx` e `dicionario_indicadores.xlsx`) e `OUTPUT` (pasta de resultados). As bibliotecas `python-louvain` e `pyvis` são instaladas pelo próprio notebook.
