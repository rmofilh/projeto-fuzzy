"""Rotas HTTP (capa de apresentação).

Responsabilidade: expor a interface web e o contrato da API. Sem lógica de
negócio: só delega (Etapa 4) em src.application.payoff_service.
"""

from flask import Blueprint, jsonify, render_template, request

from src.application.payoff_service import execute

api = Blueprint("api", __name__)

CHAVES_CANONICAS = (
    "premio",
    "ausencia_fiscalizacao",
    "concentracao_poder",
    "impunidade",
)


@api.get("/")
def index():
    return render_template("index.html")


@api.post("/api/calcular")
def calcular():
    try:
        dados = request.get_json(silent=True)
        if not isinstance(dados, dict):
            raise ValueError(
                "O corpo da requisição deve ser um JSON com as 4 chaves: "
                + ", ".join(CHAVES_CANONICAS)
            )
        for chave in CHAVES_CANONICAS:
            if chave not in dados:
                raise ValueError(
                    f"Campo '{chave}' ausente. Envie as 4 chaves canônicas: "
                    + ", ".join(CHAVES_CANONICAS)
                )
        numeros = {}
        for chave in CHAVES_CANONICAS:
            valor = dados[chave]
            if isinstance(valor, bool) or not isinstance(valor, (int, float)):
                raise ValueError(
                    f"Campo '{chave}' deve ser um número entre 0 e 10, "
                    f"recebido: {valor!r}"
                )
            numeros[chave] = float(valor)

        p = numeros["premio"]
        f = numeros["ausencia_fiscalizacao"]
        c = numeros["concentracao_poder"]
        i = numeros["impunidade"]
        if not all(0 <= v <= 10 for v in (p, f, c, i)):
            raise ValueError(
                "Os 4 campos (premio, ausencia_fiscalizacao, "
                "concentracao_poder, impunidade) devem estar entre 0 e 10."
            )

        resultado = execute(p, f, c, i)
    except ValueError as erro:
        # Validação de tipo/faixa: mensagens já são PT-BR no service/routes.
        return jsonify({"erro": str(erro)}), 400
    except TypeError:
        return jsonify({
            "erro": "Os 4 campos (premio, ausencia_fiscalizacao, "
                    "concentracao_poder, impunidade) devem ser números entre 0 e 10."
        }), 400
    except KeyError:
        # Nunca vazar "'payoff'" ou nome interno de chave.
        return jsonify({
            "erro": "Falha interna ao calcular o payoff. Tente novamente com outros valores."
        }), 500
    except Exception:
        return jsonify({
            "erro": "Erro inesperado ao calcular o payoff. Tente novamente."
        }), 500

    # Fallback Zona (valor 0.0) é resultado válido: retorna 200 normal.
    try:
        valor = round(float(resultado["valor"]), 4)
        termo = resultado["termo"]
    except (KeyError, TypeError, ValueError):
        return jsonify({
            "erro": "Falha interna ao calcular o payoff. Tente novamente com outros valores."
        }), 500

    resposta = {"valor": valor, "termo": termo}
    regras = resultado.get("regras") if isinstance(resultado, dict) else None
    if isinstance(regras, list):
        try:
            resposta["regras"] = [int(r) for r in regras]
        except (TypeError, ValueError):
            pass
    return jsonify(resposta), 200