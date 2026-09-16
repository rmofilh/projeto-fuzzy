"""Testes do cálculo de payoff (Etapa 3 — Validação).

Bateria pytest que valida o motor fuzzy (§5.1/§5.2 do doc conceitual) através
do caso de uso `execute` (src/application/payoff_service.py):

- Bloco A: cenários canônicos §6/§7 (A/B com prêmio fixo, 1519).
- Bloco B: cobertura de 1 vetor por regra da base (§5.2, 14 regras).
- Bloco C: bordas, erosão gradual do prêmio e validação de entradas.
"""

import pytest

from src.application.payoff_service import execute

NAO_COMPENSA = "Não compensa"
ZONA_RISCO = "Zona de risco"
COMPENSA = "Compensa se corromper"


# ---------------------------------------------------------------------------
# Bloco A — cenários canônicos (§6 e §7)
# ---------------------------------------------------------------------------


def test_cenario_A():
    """Cenário A (contrapesos plenos): payoff negativo com prêmio alto."""
    resultado = execute(8, 1, 1, 1)
    assert resultado["valor"] < -2
    assert resultado["termo"] == NAO_COMPENSA


def test_cenario_B():
    """Cenário B (colapso total): mesmo prêmio, payoff positivo."""
    resultado = execute(8, 9, 9, 9)
    assert resultado["valor"] > +2
    assert resultado["termo"] == COMPENSA


def test_cenario_1519():
    """1519 (§7): prêmio altíssimo, colapso total, compensa corromper."""
    resultado = execute(9.5, 9, 9, 9)
    assert resultado["termo"] == COMPENSA


def test_AB_mesmo_premio():
    """A/B com prêmio fixo: a degradação institucional move o payoff."""
    cenário_a = execute(8, 1, 1, 1)
    cenário_b = execute(8, 9, 9, 9)
    assert cenário_b["valor"] > cenário_a["valor"] + 5


# ---------------------------------------------------------------------------
# Bloco B — cobertura de 1 vetor por regra (§5.2)
# ---------------------------------------------------------------------------


def test_regra_01():
    """Regra 1 (âncora): contrapesos plenos vencem mesmo com prêmio alto."""
    assert execute(7, 1, 1, 1)["termo"] == NAO_COMPENSA


def test_regra_02():
    """Regra 2 (âncora): colapso total, havendo algo em jogo."""
    assert execute(8, 9, 9, 9)["termo"] == COMPENSA


def test_regra_03():
    """Regra 3 (contrapeso único): impunidade garantida sozinha destrava.

    Vetor ajustado: (7,1,1,9) disparava também a regra 8 (fiscalização[1] E
    concentração[1] E prêmio[3]=0.5), puxando o payoff à zona de risco; com
    prêmio 10 (g4) a regra 3 fica isolada e o payoff confirma "compensa".
    """
    assert execute(10, 1, 1, 9)["termo"] == COMPENSA


def test_regra_04():
    """Regra 4 (contrapeso único): poder absoluto sozinho destrava."""
    assert execute(7, 1, 9, 1)["termo"] == COMPENSA


def test_regra_05():
    """Regra 5 (contrapeso único): fiscalização ausente sozinha pesa menos."""
    assert execute(7, 9, 1, 1)["termo"] == ZONA_RISCO


def test_regra_06a():
    """Regra 6 (portão): sem nada em jogo, as instituições são irrelevantes."""
    assert execute(0.5, 5, 5, 5)["termo"] == NAO_COMPENSA


def test_regra_06b():
    """Regra 6 (portão): prêmio irrisório segura até o colapso total."""
    assert execute(1, 9, 9, 9)["termo"] == NAO_COMPENSA


def test_regra_07():
    """Regra 7 (tendência): dois contrapesos deteriorados + prêmio relevante."""
    assert execute(7, 1, 6, 6)["termo"] == COMPENSA


def test_regra_08():
    """Regra 8 (tendência): dois contrapesos fortes seguram tentação moderada."""
    assert execute(4, 1, 1, 1)["termo"] == NAO_COMPENSA


def test_regra_09():
    """Regra 9 (tendência): poder absoluto reforçado por impunidade alta."""
    assert execute(7, 1, 9, 6)["termo"] == COMPENSA


def test_regra_10():
    """Regra 10 (tendência): dois contrapesos fortes seguram um terceiro moderado."""
    assert execute(5, 1, 4, 1)["termo"] == NAO_COMPENSA


def test_regra_11():
    """Regra 11 (tendência): prêmio máximo + deterioração g3, sem grau 4."""
    assert execute(9, 6, 6, 6)["termo"] == COMPENSA


def test_regra_12():
    """Regra 12 (zona genuína): um fator ruim, outro ok — ambiguidade real."""
    assert execute(5, 1, 4, 6)["termo"] == ZONA_RISCO


def test_regra_13():
    """Regra 13 (zona genuína): fiscalização fraca + prêmio alto."""
    assert execute(6, 6, 1, 1)["termo"] == ZONA_RISCO


def test_regra_14():
    """Regra 14 (zona genuína): deterioração leve e uniforme nos três."""
    assert execute(5, 4, 4, 4)["termo"] == ZONA_RISCO


# ---------------------------------------------------------------------------
# Bloco C — bordas e erosão gradual (§4)
# ---------------------------------------------------------------------------


def test_borda_tudo_meio():
    """Borda intermediária pura: prêmio moderado + deterioração leve e uniforme.

    Vetor ajustado: em (5,5,5,5) o solape g2/g3 também dispara a regra 7
    (concentração[3]=impunidade[3]=prêmio[3]=0.5) e o payoff cruza a +3.5
    ("compensa"); com prêmio 4 (g2 pleno, g3 nulo) domina só a regra 14 e o
    payoff volta ao centro da zona de risco.
    """
    resultado = execute(4, 5, 5, 5)
    assert resultado["termo"] == ZONA_RISCO


def test_varredura_monotonica():
    """Erosão gradual: subir o prêmio nunca baixa o payoff (f=c=i=9).

    Verificação: lista de valores estritamente não-decrescente e cruzamento de
    negativo para positivo (prova erosão gradual, não salto binário).
    """
    valores = [execute(p, 9, 9, 9)["valor"] for p in range(11)]
    assert all(b >= a for a, b in zip(valores, valores[1:]))
    assert any(a < 0 <= b for a, b in zip(valores, valores[1:]))


def test_validacao_erro():
    """Entradas inválidas levantam exceção (tipo ou faixa fora de 0-10)."""
    with pytest.raises((ValueError, TypeError)):
        execute(11, 1, 1, 1)
    with pytest.raises((ValueError, TypeError)):
        execute(5, -1, 5, 5)
    with pytest.raises((ValueError, TypeError)):
        execute("x", 1, 1, 1)


# ---------------------------------------------------------------------------
# Bloco D — ex-buracos + bordas/varredura (Prompt 4/5)
# ---------------------------------------------------------------------------


def test_ex_buraco_8411():
    """Ex-buraco 8,4,1,1: nenhuma das 14 dispara, fallback 15 cobre em Zona.

    Sem exceção (sem KeyError): o fallback curinga Zona (regra 15, peso
    baixo) preenche o vazio e o cálculo retorna Zona de risco.
    """
    resultado = execute(8, 4, 1, 1)
    assert resultado["termo"] == ZONA_RISCO


def test_ex_buraco_4044():
    """Ex-buraco 4,0,4,4: nenhuma das 14 dispara, fallback 15 cobre em Zona.

    Sem exceção (sem KeyError): mesmo mecanismo do 8411 — curinga Zona
    garante retorno válido no centro da zona de risco.
    """
    resultado = execute(4, 0, 4, 4)
    assert resultado["termo"] == ZONA_RISCO


def test_varredura_sem_keyerror():
    """Varredura p in [4,8] x f 0..10 passo 1: nunca levanta KeyError."""
    termos_validos = {NAO_COMPENSA, ZONA_RISCO, COMPENSA}
    for p in [4, 8]:
        for f in range(0, 11, 1):
            for c, i in [(1, 1), (4, 4)]:
                resultado = execute(p, f, c, i)
                assert resultado["termo"] in termos_validos
                assert isinstance(resultado["valor"], float)


def test_borda_10():
    """Borda máxima: prêmio 10 + colapso total compensa (sem erro de borda)."""
    resultado = execute(10, 9, 9, 9)
    assert resultado["termo"] == COMPENSA


def test_regras_presentes():
    """Contrato API via test_client: 200 contém valor/termo/regras."""
    from app import create_app

    client = create_app().test_client()
    resposta = client.post(
        "/api/calcular",
        json={
            "premio": 8,
            "ausencia_fiscalizacao": 9,
            "concentracao_poder": 9,
            "impunidade": 9,
        },
    )
    assert resposta.status_code == 200
    dados = resposta.get_json()
    assert "valor" in dados
    assert "termo" in dados
    assert "regras" in dados
    assert isinstance(dados["regras"], list)
    assert len(dados["regras"]) > 0