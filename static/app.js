"use strict";

const CHAVES = ["premio", "ausencia_fiscalizacao", "concentracao_poder", "impunidade"];

// Rótulos dos graus por variável (§5.1): grau 1 = mais favorável à
// conformidade, grau 4 = mais favorável à corrupção.
const GRAUS_POR_CHAVE = {
    premio: ["Irrisório", "Moderado", "Alto", "Altíssimo"],
    ausencia_fiscalizacao: ["Fiscalização Plena", "Fiscalização Parcial", "Fiscalização Enfraquecida", "Fiscalização Inexistente"],
    concentracao_poder: ["Poder Distribuído", "Poder Moderado", "Poder Concentrado", "Poder Absoluto"],
    impunidade: ["Punição Certa", "Punição Parcial", "Punição Rara", "Impunidade"],
};

const PRESETS = {
    a: { premio: 8, ausencia_fiscalizacao: 1, concentracao_poder: 1, impunidade: 1 },
    b: { premio: 8, ausencia_fiscalizacao: 9, concentracao_poder: 9, impunidade: 9 },
    "1519": { premio: 9.5, ausencia_fiscalizacao: 9, concentracao_poder: 9, impunidade: 9 },
};

const CORES_TERMOS = {
    "Não compensa": "#2e7d32",
    "Zona de risco": "#e08e00",
    "Compensa se corromper": "#c62828",
};

// Funções de pertinência espelhadas do motor (§5.1): mesmo template
// trapezoidal/triangular e os mesmos picos (g1=1, g2=4, g3=6, g4=9).
function trapmf(x, a, b, c, d) {
    if (x >= b && x <= c) return 1;
    if (x > a && x < b) return (x - a) / (b - a);
    if (x > c && x < d) return (d - x) / (d - c);
    return 0;
}

function trimf(x, a, b, c) {
    if (x === b) return 1;
    if (x > a && x < b) return (x - a) / (b - a);
    if (x > b && x < c) return (c - x) / (c - b);
    return 0;
}

const PARAMETROS_GRAUS = {
    g1: [0, 0, 2, 4],
    g2: [2, 4, 6],
    g3: [4, 6, 8],
    g4: [6, 8, 10, 10],
};

const GRAUS = ["g1", "g2", "g3", "g4"];

function nomeGrau(chave, valor) {
    let melhor = "g1";
    let maior = -1;
    for (const grau of GRAUS) {
        const parametros = PARAMETROS_GRAUS[grau];
        const pertinencia = parametros.length === 3
            ? trimf(valor, parametros[0], parametros[1], parametros[2])
            : trapmf(valor, parametros[0], parametros[1], parametros[2], parametros[3]);
        if (pertinencia > maior) {
            maior = pertinencia;
            melhor = grau;
        }
    }
    return GRAUS_POR_CHAVE[chave][GRAUS.indexOf(melhor)];
}

// Pertinência 0–1 de um valor em um grau, reaproveitando trapmf/trimf do motor.
function pertinenciaDoGrau(valor, grau) {
    const parametros = PARAMETROS_GRAUS[grau];
    if (!parametros) return 0;
    return parametros.length === 3
        ? trimf(valor, parametros[0], parametros[1], parametros[2])
        : trapmf(valor, parametros[0], parametros[1], parametros[2], parametros[3]);
}

function formatarPorcentagem(fracao) {
    return (fracao * 100).toFixed(1).replace(".", ",") + "%";
}

function textoPertinencias(valor) {
    return GRAUS.map(function (grau) {
        return grau + " " + formatarPorcentagem(pertinenciaDoGrau(valor, grau));
    }).join(" · ");
}

let temporizador = null;

function lerEntradas() {
    const entradas = {};
    for (const chave of CHAVES) {
        const entrada = document.getElementById(chave);
        // Se o campo foi removido (por exemplo, via DevTools), enviamos
        // null para que o servidor responda 400 com mensagem em PT-BR.
        entradas[chave] = entrada ? parseFloat(entrada.value) : null;
    }
    return entradas;
}

function atualizarRotulos(chave) {
    const input = document.getElementById(chave);
    if (!input) return;
    const rotulo = document.getElementById("valor-" + chave);
    if (rotulo) rotulo.textContent = input.value.replace(".", ",");
    const grau = document.getElementById("grau-" + chave);
    if (grau) grau.textContent = nomeGrau(chave, parseFloat(input.value));
    const pert = document.getElementById("pert-" + chave);
    if (pert) pert.textContent = textoPertinencias(parseFloat(input.value));
    const porcentagem = parseFloat(input.value) / 10 * 100;
    input.style.background =
        "linear-gradient(90deg, var(--carmesim) " + porcentagem + "%, #e0d4b8 " + porcentagem + "%)";
}

function atualizarResultado(valor, termo) {
    const cor = CORES_TERMOS[termo] || "#6b5636";
    document.getElementById("numero").textContent =
        (valor >= 0 ? "+" : "") + valor.toFixed(2).replace(".", ",");
    document.getElementById("numero").style.color = cor;
    document.getElementById("termo").textContent = termo;
    document.getElementById("termo").style.background = cor;
    const posicao = Math.min(100, Math.max(0, (valor + 10) / 20 * 100));
    document.getElementById("marcador").style.left = posicao + "%";
}

function mostrarErro(mensagem) {
    document.getElementById("erro").textContent = mensagem;
    document.getElementById("erro").hidden = false;
    document.getElementById("numero").textContent = "–";
    document.getElementById("numero").style.color = "";
    esconderRegras();
}

function esconderRegras() {
    const linha = document.getElementById("regras");
    if (linha) linha.hidden = true;
}

function atualizarRegras(regras) {
    const linha = document.getElementById("regras");
    const lista = document.getElementById("regras-lista");
    if (!linha || !lista) return;
    // Contrato Prompts 1-2: API retorna {valor, termo, regras}. Se a chave
    // estiver ausente (backend antigo), esconde a linha sem erro.
    if (!Array.isArray(regras)) {
        linha.hidden = true;
        return;
    }
    linha.hidden = false;
    lista.textContent = regras.length ? regras.join(", ") : "—";
}

function botoes(estado) {
    document.querySelectorAll(".btn-preset").forEach(function (botao) {
        botao.disabled = estado;
    });
}

async function calcular() {
    const numero = document.getElementById("numero");
    botoes(true);
    numero.textContent = "calculando…";
    numero.style.color = "";
    document.getElementById("erro").hidden = true;

    let resposta;
    try {
        resposta = await fetch("/api/calcular", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(lerEntradas()),
        });
    } catch (causa) {
        botoes(false);
        mostrarErro("Falha de comunicação com o servidor. Confirme que app.py está ativo.");
        return;
    }

    let dados = null;
    try {
        dados = await resposta.json();
    } catch (causa) {
        botoes(false);
        mostrarErro("Resposta do servidor ilegível.");
        return;
    }

    botoes(false);
    if (!resposta.ok) {
        mostrarErro(dados && dados.erro ? dados.erro : "Não foi possível calcular o payoff.");
        return;
    }

    atualizarResultado(dados.valor, dados.termo);
    atualizarRegras(dados ? dados.regras : undefined);
}

document.addEventListener("DOMContentLoaded", function () {
    for (const chave of CHAVES) {
        document.getElementById(chave).addEventListener("input", function () {
            atualizarRotulos(chave);
            if (temporizador) clearTimeout(temporizador);
            temporizador = setTimeout(calcular, 250);
        });
    }

    document.querySelectorAll(".btn-preset").forEach(function (botao) {
        botao.addEventListener("click", function () {
            const valores = PRESETS[botao.dataset.preset];
            for (const chave of CHAVES) {
                const input = document.getElementById(chave);
                if (!input) continue;
                input.value = valores[chave];
                atualizarRotulos(chave);
            }
            if (temporizador) clearTimeout(temporizador);
            calcular();
        });
    });

    for (const chave of CHAVES) atualizarRotulos(chave);
    calcular();
});