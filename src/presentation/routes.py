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
    except (KeyError, TypeError, ValueError) as erro:
        return jsonify({"erro": str(erro)}), 400

    return jsonify({
        "valor": round(float(resultado["valor"]), 4),
        "termo": resultado["termo"],
    }), 200