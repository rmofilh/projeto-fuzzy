"""Motor fuzzy skfuzzy (§5.1/§5.2).

Bloco movido byte a byte de `src/domain/fuzzy_engine.py`: antecedentes,
consequente, base de 15 regras (14 + 1 fallback curinga Zona) e sistema.
Único módulo que importa `skfuzzy.control`.
"""

import skfuzzy as fuzz
import skfuzzy.control as ctrl

from src.domain.universos import UNIVERSO_ENTRADA, UNIVERSO_SAIDA, _PARAMETROS_GRAUS

# ---------------------------------------------------------------------------
# Antecedents: 4 entradas canônicas, cada uma com 4 graus (§5.1)
# ---------------------------------------------------------------------------
premio = ctrl.Antecedent(UNIVERSO_ENTRADA, "premio")
ausencia_fiscalizacao = ctrl.Antecedent(UNIVERSO_ENTRADA, "ausencia_fiscalizacao")
concentracao_poder = ctrl.Antecedent(UNIVERSO_ENTRADA, "concentracao_poder")
impunidade = ctrl.Antecedent(UNIVERSO_ENTRADA, "impunidade")

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
# Base de regras (§5.2): 14 regras em 5 grupos lógicos + 1 fallback curinga
# (14+1 = 15). Alias locais para manter as expressões das regras fiéis à
# notação da especificação.
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

# Regra 15 (fallback curinga §5.2, 14+1): cobre os ~6% de buracos onde nenhuma
# das 14 dispara (ex: 8,4,1,1). Antecedente curinga g2 em OR → zona_risco com
# peso baixo (0.1), para só preencher o vazio sem puxar os 14 casos existentes
# (deslocamento <0.8, termo inalterado). Usa `weight` se disponível, senão
# consequente ponderado (%) como antecedente fraco equivalente.
try:
    regra15 = ctrl.Rule(
        pre["g2"] | aus["g2"] | con["g2"] | imp["g2"],
        payoff["zona_risco"],
        weight=0.1,
        label="regra15 fallback curinga Zona",
    )
except TypeError:
    # skfuzzy 0.5.0: ctrl.Rule sem parâmetro `weight` → consequente ponderado
    # (%) como antecedente fraco equivalente (peso baixo).
    regra15 = ctrl.Rule(
        pre["g2"] | aus["g2"] | con["g2"] | imp["g2"],
        payoff["zona_risco"] % 0.1,
        label="regra15 fallback curinga Zona",
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
    regra15,
]

assert len(REGRAS) == 15, "A base deve ter exatamente 15 regras §5.2 (14+1 fallback)"

sistema = ctrl.ControlSystem(REGRAS)


def nova_simulacao():
    """Cria uma simulação nova por chamada (thread-safe, §5.2).

    Retorna: ctrl.ControlSystemSimulation nova ligada a `sistema`. Nunca
    reutilizar instância global entre chamadas/threads.
    """
    return ctrl.ControlSystemSimulation(sistema)
