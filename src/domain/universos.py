"""Universos de discurso e rótulos (§5.1).

Copia exata dos blocos de `src/domain/fuzzy_engine.py`: universos,
rótulos PT-BR, parâmetros dos graus e nomes canônicos das entradas.
Sem `skfuzzy.control`: só `numpy`.
"""

import numpy as np

# ---------------------------------------------------------------------------
# Universos de discurso (§5.1)
# ---------------------------------------------------------------------------
UNIVERSO_ENTRADA = np.arange(0, 10.1, 0.1)     # 4 entradas, escala 0 a 10
UNIVERSO_SAIDA = np.arange(-10, 10.1, 0.1)     # payoff, escala -10 a +10

# ---------------------------------------------------------------------------
# Rótulos de exibição PT-BR (§5.1, tabela de graus). Dicionário auxiliar:
# não participa da inferência, serve apenas à apresentação dos resultados.
# ---------------------------------------------------------------------------
LABELS_GRAUS = {
    "g1": "Irrisório",
    "g2": "Moderado",
    "g3": "Alto",
    "g4": "Altíssimo",
}

LABELS_VARIAVEIS = {
    "premio": "Prêmio",
    "ausencia_fiscalizacao": "Ausência de fiscalização",
    "concentracao_poder": "Concentração de poder",
    "impunidade": "Impunidade",
}

LABELS_TERMOS_PAYOFF = {
    "nao_compensa": "Não compensa",
    "zona_risco": "Zona de risco",
    "compensa": "Compensa se corromper",
}

_PARAMETROS_GRAUS = {
    "g1": [0, 0, 2, 4],
    "g2": [2, 4, 6],
    "g3": [4, 6, 8],
    "g4": [6, 8, 10, 10],
}

_ENTRADAS = ("premio", "ausencia_fiscalizacao", "concentracao_poder", "impunidade")
