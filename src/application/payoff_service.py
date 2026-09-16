"""Caso de uso: calcular payoff (capa de aplicação).

Responsabilidade: validar tipos e faixa das entradas e delegar o cálculo no
motor fuzzy do domínio, devolvendo um dicionário com o valor numérico e o
termo linguístico PT-BR. Sem conhecimento de HTTP, Flask nem da biblioteca
fuzzy de domínio (importação restrita à capa de domínio).

Referência conceitual (docs/documentacao-conceitual.md): §5.1 (universos e
graus), §5.2 (base de regras).
"""

from src.domain.fuzzy_engine import calcular_payoff, classificar_payoff, regras_ativas


def execute(p, f, c, i):
    """Calcula o payoff para os 4 fatores de entrada (universo 0-10).

    Argumentos:
        p: prêmio — valor do poder ou benefício em disputa.
        f: ausência de fiscalização (mídia/povo).
        c: concentração de poder / ausência de separação de poderes.
        i: impunidade (ausência de punição certa e coerente).

    Retorna: dicionário com:
        valor: payoff líquido estimado, float no universo -10 a +10 (§5.1).
        termo: "Não compensa", "Zona de risco" ou "Compensa se corromper".
        regras: lista de ints 1-based com as regras que dispararam >0
            (helper regras_ativas do domínio; vazio se nada disparar).

    Lança ValueError se alguma entrada está fora da faixa 0-10.
    """
    for nome, valor in (("prêmio", p), ("ausência de fiscalização", f),
                        ("concentração de poder", c), ("impunidade", i)):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError(
                f"{nome} deve ser um número real entre 0 e 10, recebido: {valor!r}"
            )
        if not 0 <= valor <= 10:
            raise ValueError(
                f"{nome} deve estar entre 0 e 10 (universo §5.1), recebido: {valor!r}"
            )

    valor_payoff = calcular_payoff(p, f, c, i)
    return {
        "valor": valor_payoff,
        "termo": classificar_payoff(valor_payoff),
        "regras": regras_ativas(p, f, c, i),
    }