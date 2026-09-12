"""Motor de inferência fuzzy (capa de domínio).

Responsabilidade: transformar os 4 fatores de entrada (universo 0-10, graus 1-4)
no payoff líquido de agir corruptamente (universo -10 a +10, 3 termos).

Referências conceitual (docs/documentacao-conceitual.md):
- §5.1: universos de discurso, direção dos graus e funções de pertinência.
- §5.2: base de regras fuzzy (14 regras em 5 grupos lógicos).
"""

import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl

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

# ---------------------------------------------------------------------------
# Antecedents: 4 entradas canônicas, cada uma com 4 graus (§5.1)
# ---------------------------------------------------------------------------
premio = ctrl.Antecedent(UNIVERSO_ENTRADA, "premio")
ausencia_fiscalizacao = ctrl.Antecedent(UNIVERSO_ENTRADA, "ausencia_fiscalizacao")
concentracao_poder = ctrl.Antecedent(UNIVERSO_ENTRADA, "concentracao_poder")
impunidade = ctrl.Antecedent(UNIVERSO_ENTRADA, "impunidade")

_PARAMETROS_GRAUS = {
    "g1": [0, 0, 2, 4],
    "g2": [2, 4, 6],
    "g3": [4, 6, 8],
    "g4": [6, 8, 10, 10],
}

for _antecedente in (premio, ausencia_fiscalizacao, concentracao_poder, impunidade):
    _antecedente["g1"] = fuzz.trapmf(UNIVERSO_ENTRADA, _PARAMETROS_GRAUS["g1"])
    _antecedente["g2"] = fuzz.trimf(UNIVERSO_ENTRADA, _PARAMETROS_GRAUS["g2"])
    _antecedente["g3"] = fuzz.trimf(UNIVERSO_ENTRADA, _PARAMETROS_GRAUS["g3"])
    _antecedente["g4"] = fuzz.trapmf(UNIVERSO_ENTRADA, _PARAMETROS_GRAUS["g4"])

# ---------------------------------------------------------------------------
# Consequent: payoff líquido, 3 termos (§5.1)
# ---------------------------------------------------------------------------
payoff = ctrl.Consequent(UNIVERSO_SAIDA, "payoff", defuzzify_method="centroid")
payoff["nao_compensa"] = fuzz.trapmf(UNIVERSO_SAIDA, [-10, -10, -6, -2])
payoff["zona_risco"] = fuzz.trimf(UNIVERSO_SAIDA, [-4, 0, 4])
payoff["compensa"] = fuzz.trapmf(UNIVERSO_SAIDA, [2, 6, 10, 10])

# ---------------------------------------------------------------------------
# Base de regras (§5.2): 14 regras em 5 grupos lógicos. Alias locais para
# manter as expressões das regras fiéis à notação da especificação.
# ---------------------------------------------------------------------------
pre = premio
aus = ausencia_fiscalizacao
con = concentracao_poder
imp = impunidade

# Regra 1 (âncora): contrapesos plenos vencem mesmo com prêmio alto
regra1 = ctrl.Rule(
    aus["g1"] & con["g1"] & imp["g1"],
    payoff["nao_compensa"],
)

# Regra 2 (âncora): colapso total, havendo algo em jogo
regra2 = ctrl.Rule(
    aus["g4"] & con["g4"] & imp["g4"] & ~pre["g1"],
    payoff["compensa"],
)

# Regra 3 (contrapeso único): impunidade garantida sozinha já destrava
regra3 = ctrl.Rule(
    imp["g4"] & ~pre["g1"],
    payoff["compensa"],
)

# Regra 4 (contrapeso único): poder absoluto sozinho já destrava
regra4 = ctrl.Rule(
    con["g4"] & ~pre["g1"],
    payoff["compensa"],
)

# Regra 5 (contrapeso único): fiscalização ausente sozinha pesa menos
regra5 = ctrl.Rule(
    aus["g4"] & ~pre["g1"],
    payoff["zona_risco"],
)

# Regra 6 (portão do prêmio): sem nada em jogo, as instituições são irrelevantes
regra6 = ctrl.Rule(
    pre["g1"],
    payoff["nao_compensa"],
)

# Regra 7 (tendência): dois contrapesos deteriorados + prêmio relevante
regra7 = ctrl.Rule(
    con["g3"] & imp["g3"] & (pre["g3"] | pre["g4"]),
    payoff["compensa"],
)

# Regra 8 (tendência): dois contrapesos fortes seguram tentação moderada
regra8 = ctrl.Rule(
    aus["g1"] & con["g1"] & (pre["g2"] | pre["g3"]),
    payoff["nao_compensa"],
)

# Regra 9 (tendência): poder absoluto reforçado por impunidade alta
regra9 = ctrl.Rule(
    con["g4"] & imp["g3"] & ~pre["g1"],
    payoff["compensa"],
)

# Regra 10 (tendência): dois contrapesos fortes seguram um terceiro moderado
regra10 = ctrl.Rule(
    aus["g1"] & imp["g1"] & con["g2"],
    payoff["nao_compensa"],
)

# Regra 11 (tendência): prêmio máximo + os três já bem deteriorados, sem grau 4
regra11 = ctrl.Rule(
    pre["g4"] & aus["g3"] & con["g3"] & imp["g3"],
    payoff["compensa"],
)

# Regra 12 (zona de risco genuína): um fator ruim, outro ok — ambiguidade real
regra12 = ctrl.Rule(
    imp["g3"] & con["g2"],
    payoff["zona_risco"],
)

# Regra 13 (zona de risco genuína): fiscalização fraca + prêmio alto
regra13 = ctrl.Rule(
    aus["g3"] & pre["g3"],
    payoff["zona_risco"],
)

# Regra 14 (zona de risco genuína): deterioração leve e uniforme nos três
regra14 = ctrl.Rule(
    aus["g2"] & con["g2"] & imp["g2"],
    payoff["zona_risco"],
)

REGRAS = [
    regra1,
    regra2,
    regra3,
    regra4,
    regra5,
    regra6,
    regra7,
    regra8,
    regra9,
    regra10,
    regra11,
    regra12,
    regra13,
    regra14,
]

assert len(REGRAS) == 14, "A base deve ter exatamente 14 regras (§5.2)"

sistema = ctrl.ControlSystem(REGRAS)
simulacao = ctrl.ControlSystemSimulation(sistema)

_ENTRADAS = ("premio", "ausencia_fiscalizacao", "concentracao_poder", "impunidade")


def _validar_entrada(valor, nome):
    """Valida que um valor de entrada seja um número real entre 0 e 10."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(
            f"{nome} deve ser um número real entre 0 e 10, recebido: {valor!r}"
        )
    if not 0 <= valor <= 10:
        raise ValueError(
            f"{nome} deve estar entre 0 e 10 (universo §5.1), recebido: {valor!r}"
        )


def calcular_payoff(p, f, c, i):
    """Calcula o payoff líquido de agir corruptamente (§5.1/§5.2).

    Argumentos (universo 0-10; grau 1 = mais favorável à conformidade,
    grau 4 = mais favorável à corrupção):
        p: prêmio — valor do poder ou benefício em disputa.
        f: ausência de fiscalização (mídia/povo).
        c: concentração de poder / ausência de separação de poderes.
        i: impunidade (ausência de punição certa e coerente).

    Retorna: payoff líquido estimado, float no universo -10 a +10
    (defuzzificação por centroide).

    Lança ValueError se qualquer entrada está fora da faixa 0-10.
    """
    for nome, valor in zip(_ENTRADAS, (p, f, c, i)):
        _validar_entrada(valor, nome)

    simulacao.input["premio"] = p
    simulacao.input["ausencia_fiscalizacao"] = f
    simulacao.input["concentracao_poder"] = c
    simulacao.input["impunidade"] = i
    simulacao.compute()

    return float(simulacao.output["payoff"])


def classificar_payoff(valor):
    """Classifica um valor de payoff em um dos 3 termos linguísticos.

    Usa interp_membership sobre o valor defuzzificado e elege o termo com
    maior pertinência (argmax entre os 3 termos de saída, §5.1).

    Argumentos:
        valor: payoff no universo -10 a +10.

    Retorna: label PT-BR do termo ("Não compensa", "Zona de risco" ou
    "Compensa se corromper").
    """
    pertinencias = {
        termo: fuzz.interp_membership(UNIVERSO_SAIDA, payoff[termo].mf, valor)
        for termo in LABELS_TERMOS_PAYOFF
    }
    melhor_termo = max(pertinencias, key=pertinencias.get)
    return LABELS_TERMOS_PAYOFF[melhor_termo]


def debug_membership():
    """Diagnóstico das funções de pertinência (verificação de Etapa 2).

    Imprime, para cada antecedente e para os pontos 1, 4, 6 e 9, a pertinência
    de cada grau. Verificação esperada: picos de pertinência em g1=1, g2=4,
    g3=6, g4=9 (o grau com maior valor em cada ponto).
    """
    print("Pertinência dos antecedentes (picos esperados: g1=1, g2=4, g3=6, g4=9)")
    for nome, antecedente in zip(_ENTRADAS, (premio, ausencia_fiscalizacao, concentracao_poder, impunidade)):
        print(f"\n{LABELS_VARIAVEIS[nome]} ({nome})")
        for ponto in (1, 4, 6, 9):
            pertinencias = {
                grau: fuzz.interp_membership(UNIVERSO_ENTRADA, antecedente[grau].mf, ponto)
                for grau in ("g1", "g2", "g3", "g4")
            }
            maior = max(pertinencias, key=pertinencias.get)
            valores = ", ".join(f"{grau}={pertinencias[grau]:.3f}" for grau in ("g1", "g2", "g3", "g4"))
            print(f"  x={ponto}: {valores}  -> pico em {maior}")