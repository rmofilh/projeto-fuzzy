"""Fachada fina de domínio (§5.1/§5.2): validação, cálculo e explicação."""

import skfuzzy as fuzz

from src.domain.universos import LABELS_GRAUS, LABELS_TERMOS_PAYOFF, LABELS_VARIAVEIS, UNIVERSO_ENTRADA, UNIVERSO_SAIDA, _ENTRADAS, _PARAMETROS_GRAUS
from src.infrastructure.fuzzy.motor import REGRAS, ausencia_fiscalizacao, concentracao_poder, impunidade, nova_simulacao, payoff, premio, sistema

__all__ = ["LABELS_GRAUS", "LABELS_TERMOS_PAYOFF", "LABELS_VARIAVEIS", "REGRAS", "UNIVERSO_ENTRADA", "UNIVERSO_SAIDA", "_ENTRADAS", "_PARAMETROS_GRAUS", "ausencia_fiscalizacao", "calcular_payoff", "classificar_payoff", "concentracao_poder", "debug_membership", "impunidade", "nova_simulacao", "payoff", "premio", "regras_ativas", "sistema"]


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
    (defuzzificação por centroide). Se nenhuma regra disparar
    (output=={}), retorna 0.0 (Zona de risco) sem levantar KeyError —
    o fallback regra15 cobre ~todos os buracos, esta guarda cobre o resto.

    Usa simulação nova por chamada via nova_simulacao() (thread-safe).

    Lança ValueError se qualquer entrada está fora da faixa 0-10.
    """
    for nome, valor in zip(_ENTRADAS, (p, f, c, i)):
        _validar_entrada(valor, nome)

    sim = nova_simulacao()
    sim.input["premio"] = p
    sim.input["ausencia_fiscalizacao"] = f
    sim.input["concentracao_poder"] = c
    sim.input["impunidade"] = i
    sim.compute()

    if not sim.output or "payoff" not in sim.output:
        return 0.0

    return float(sim.output["payoff"])


def classificar_payoff(valor):
    """Classifica um valor de payoff em um dos 3 termos linguísticos.

    Usa interp_membership sobre o valor defuzzificado e elege o termo com
    maior pertinência (argmax entre os 3 termos de saída, §5.1).

    Argumentos:
        valor: payoff no universo -10 a +10.

    Retorna: label PT-BR do termo ("Não compensa", "Zona de risco" ou
    "Compensa se corromper").
    """
    # Borda interp_membership: trapmf compensa [2,6,10,10] em valor==10.0
    # sofre erro de borda; clampe só aqui (não altera inferência).
    if valor >= 10.0:
        valor = 9.99
    pertinencias = {
        termo: fuzz.interp_membership(UNIVERSO_SAIDA, payoff[termo].mf, valor)
        for termo in LABELS_TERMOS_PAYOFF
    }
    melhor_termo = max(pertinencias, key=pertinencias.get)
    return LABELS_TERMOS_PAYOFF[melhor_termo]


def regras_ativas(p, f, c, i):
    """Retorna os índices 1-based das regras cujo antecedente disparou >0.

    Não altera a inferência: apenas fuzzifica as 4 entradas e avalia o grau
    de disparo de cada antecedente (AND=min, OR=max, NOT=1-x, mesmos
    and_func/or_func de cada regra). Útil para explicar o resultado na API
    sem expor skfuzzy fora do domínio.

    Argumentos: mesmos de calcular_payoff (universo 0-10).

    Retorna: lista de ints, ex: [1] ou [15]. Pode ser vazia se nada
    disparar (caso raro; o fallback regra15 cobre ~todos os buracos).

    Lança ValueError se qualquer entrada está fora da faixa 0-10.
    """
    for nome, valor in zip(_ENTRADAS, (p, f, c, i)):
        _validar_entrada(valor, nome)

    # Import local para não mexer no topo do motor fuzzy.
    from skfuzzy.control.controlsystem import CrispValueCalculator
    from skfuzzy.control.term import TermAggregate

    sim = nova_simulacao()
    sim.input["premio"] = p
    sim.input["ausencia_fiscalizacao"] = f
    sim.input["concentracao_poder"] = c
    sim.input["impunidade"] = i

    CrispValueCalculator(premio, sim).fuzz(p)
    CrispValueCalculator(ausencia_fiscalizacao, sim).fuzz(f)
    CrispValueCalculator(concentracao_poder, sim).fuzz(c)
    CrispValueCalculator(impunidade, sim).fuzz(i)

    ativas = []
    for indice, regra in enumerate(REGRAS, start=1):
        antecedente = regra.antecedent
        if isinstance(antecedente, TermAggregate):
            antecedente.agg_methods = regra._aggregation_methods
        try:
            disparo = float(antecedente.membership_value[sim])
        except (TypeError, ValueError):
            continue
        if disparo > 0:
            ativas.append(indice)
    return ativas


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
