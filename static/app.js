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

const REGRAS_TEXTO = {1:{se:"aus[g1] E con[g1] E imp[g1]",entao:"Não compensa"}, 2:{se:"aus[g4] E con[g4] E imp[g4] E NÃO pre[g1]",entao:"Compensa"}, 3:{se:"imp[g4] E NÃO pre[g1]",entao:"Compensa"}, 4:{se:"con[g4] E NÃO pre[g1]",entao:"Compensa"}, 5:{se:"aus[g4] E NÃO pre[g1]",entao:"Zona de risco"}, 6:{se:"pre[g1]",entao:"Não compensa"}, 7:{se:"con[g3] E imp[g3] E (pre[g3] OU pre[g4])",entao:"Compensa"}, 8:{se:"aus[g1] E con[g1] E (pre[g2] OU pre[g3])",entao:"Não compensa"}, 9:{se:"con[g4] E imp[g3] E NÃO pre[g1]",entao:"Compensa"}, 10:{se:"aus[g1] E imp[g1] E con[g2]",entao:"Não compensa"}, 11:{se:"pre[g4] E aus[g3] E con[g3] E imp[g3]",entao:"Compensa"}, 12:{se:"imp[g3] E con[g2]",entao:"Zona de risco"}, 13:{se:"aus[g3] E pre[g3]",entao:"Zona de risco"}, 14:{se:"aus[g2] E con[g2] E imp[g2]",entao:"Zona de risco"}, 15:{se:"pre[g2] OU aus[g2] OU con[g2] OU imp[g2] (fallback peso 0.1)",entao:"Zona de risco"}};

const CORES_GRAUS_ENTRADA = { g1: "#d9c9a8", g2: "#c9a227", g3: "#b03a2e", g4: "#7a1f16" };

const TERMOS_SAIDA = [
    { chave: "nao_compensa", rotulo: "Não compensa", cor: "#2e7d32", params: [-10, -10, -6, -2] },
    { chave: "zona_risco", rotulo: "Zona de risco", cor: "#e08e00", params: [-4, 0, 4] },
    { chave: "compensa", rotulo: "Compensa", cor: "#c62828", params: [2, 6, 10, 10] },
];

function pertinenciaSaida(x, params) {
    return params.length === 3
        ? trimf(x, params[0], params[1], params[2])
        : trapmf(x, params[0], params[1], params[2], params[3]);
}

function caminhoDaCurva(pontos) {
    return pontos.map(function (p, i) {
        return (i === 0 ? "M" : "L") + p[0].toFixed(1) + " " + p[1].toFixed(1);
    }).join(" ");
}

function estruturaSvgBase(largura, altura, margem) {
    return { largura: largura, altura: altura, margem: margem,
        utilW: largura - margem.esq - margem.dir,
        utilH: altura - margem.topo - margem.base };
}

function desenharGraficoEntrada(svgId, valor) {
    const svg = document.getElementById(svgId);
    if (!svg) return;
    const g = estruturaSvgBase(300, 160, { esq: 28, dir: 10, topo: 10, base: 22 });
    const num = parseFloat(valor);
    const v = isNaN(num) ? 0 : Math.min(10, Math.max(0, num));
    function X(x) { return g.margem.esq + (x / 10) * g.utilW; }
    function Y(y) { return g.margem.topo + (1 - y) * g.utilH; }
    let s = "";
    [0, 0.5, 1].forEach(function (yy) {
        s += '<line class="grade" x1="' + g.margem.esq + '" y1="' + Y(yy).toFixed(1) +
            '" x2="' + (g.margem.esq + g.utilW) + '" y2="' + Y(yy).toFixed(1) + '"/>';
    });
    GRAUS.forEach(function (grau) {
        const pontos = [];
        for (let x = 0; x <= 10.001; x += 0.1) {
            pontos.push([X(x), Y(pertinenciaDoGrau(x, grau))]);
        }
        s += '<path d="' + caminhoDaCurva(pontos) + '" fill="none" stroke="' +
            CORES_GRAUS_ENTRADA[grau] + '" stroke-width="2"/>';
    });
    s += '<line class="eixo" x1="' + g.margem.esq + '" y1="' + Y(0) + '" x2="' +
        (g.margem.esq + g.utilW) + '" y2="' + Y(0) + '"/>';
    s += '<line class="eixo" x1="' + g.margem.esq + '" y1="' + g.margem.topo + '" x2="' +
        g.margem.esq + '" y2="' + Y(0) + '"/>';
    [0, 5, 10].forEach(function (tick) {
        s += '<text x="' + X(tick) + '" y="' + (g.altura - 8) + '" text-anchor="middle">' + tick + "</text>";
    });
    s += '<text x="' + (g.margem.esq - 4) + '" y="' + (Y(1) + 3) + '" text-anchor="end">1</text>';
    const xm = X(v);
    s += '<line class="marcador-valor" x1="' + xm.toFixed(1) + '" y1="' + g.margem.topo +
        '" x2="' + xm.toFixed(1) + '" y2="' + Y(0) + '"/>';
    s += '<text x="' + xm.toFixed(1) + '" y="' + (g.margem.topo - 1) + '" text-anchor="middle">' +
        String(valor).replace(".", ",") + "</text>";
    svg.innerHTML = s;
}

function desenharGraficoSaida(svgId, valorPayoff) {
    const svg = document.getElementById(svgId);
    if (!svg) return;
    const g = estruturaSvgBase(300, 160, { esq: 28, dir: 10, topo: 10, base: 22 });
    function X(x) { return g.margem.esq + ((x + 10) / 20) * g.utilW; }
    function Y(y) { return g.margem.topo + (1 - y) * g.utilH; }
    let s = "";
    [0, 0.5, 1].forEach(function (yy) {
        s += '<line class="grade" x1="' + g.margem.esq + '" y1="' + Y(yy).toFixed(1) +
            '" x2="' + (g.margem.esq + g.utilW) + '" y2="' + Y(yy).toFixed(1) + '"/>';
    });
    TERMOS_SAIDA.forEach(function (termo) {
        const pontos = [];
        for (let x = -10; x <= 10.001; x += 0.2) {
            pontos.push([X(x), Y(pertinenciaSaida(x, termo.params))]);
        }
        s += '<path d="' + caminhoDaCurva(pontos) + '" fill="none" stroke="' +
            termo.cor + '" stroke-width="2"/>';
    });
    s += '<line class="eixo" x1="' + g.margem.esq + '" y1="' + Y(0) + '" x2="' +
        (g.margem.esq + g.utilW) + '" y2="' + Y(0) + '"/>';
    s += '<line class="eixo" x1="' + g.margem.esq + '" y1="' + g.margem.topo + '" x2="' +
        g.margem.esq + '" y2="' + Y(0) + '"/>';
    [[-10, "-10"], [0, "0"], [10, "+10"]].forEach(function (tick) {
        s += '<text x="' + X(tick[0]) + '" y="' + (g.altura - 8) + '" text-anchor="middle">' + tick[1] + "</text>";
    });
    s += '<text x="' + (g.margem.esq - 4) + '" y="' + (Y(1) + 3) + '" text-anchor="end">1</text>';
    const num = parseFloat(valorPayoff);
    if (!isNaN(num)) {
        const vc = Math.min(10, Math.max(-10, num));
        const xm = X(vc);
        s += '<line class="marcador-valor" x1="' + xm.toFixed(1) + '" y1="' + g.margem.topo +
            '" x2="' + xm.toFixed(1) + '" y2="' + Y(0) + '"/>';
        s += '<text x="' + xm.toFixed(1) + '" y="' + (g.margem.topo - 1) + '" text-anchor="middle">' +
            (vc >= 0 ? "+" : "") + String(Math.round(vc * 100) / 100).replace(".", ",") + "</text>";
    }
    svg.innerHTML = s;
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
    desenharGraficoEntrada("graf-" + chave, parseFloat(input.value));
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
    const caixa = document.getElementById("regras-tabela");
    if (caixa) caixa.innerHTML = '<p class="regras-vazio">—</p>';
}

function atualizarRegras(regras) {
    const linha = document.getElementById("regras");
    const caixa = document.getElementById("regras-tabela");
    // Contrato Prompts 1-2: API retorna {valor, termo, regras}. Se a chave
    // estiver ausente (backend antigo), esconde sem erro.
    if (!Array.isArray(regras)) {
        if (linha) linha.hidden = true;
        if (caixa) caixa.innerHTML = '<p class="regras-vazio">—</p>';
        return;
    }
    if (linha) linha.hidden = true;
    if (!caixa) return;
    const validas = regras.filter(function (n) { return REGRAS_TEXTO[n]; });
    if (!validas.length) {
        caixa.innerHTML = '<p class="regras-vazio">Nenhuma regra forte — fallback Zona</p>';
        return;
    }
    let html = '<table class="tabela-regras"><thead><tr><th class="col-num">Nº</th><th>SE</th><th>ENTÃO</th></tr></thead><tbody>';
    validas.forEach(function (n) {
        html += "<tr><td class=\"col-num\">R" + n + "</td><td>" + REGRAS_TEXTO[n].se +
            "</td><td>" + REGRAS_TEXTO[n].entao + "</td></tr>";
    });
    html += "</tbody></table>";
    caixa.innerHTML = html;
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
    desenharGraficoSaida("graf-payoff", dados.valor);
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
    desenharGraficoSaida("graf-payoff", NaN);
    calcular();
});