# Plano geral — Fuzzy Corrupção Institucional (registro)

## 0. Norte e decisões fixas
- Doc norte: `docs/documentacao-conceitual.md` (§5.1 universos/MFs, §5.2 15 regras em 6 grupos, §5.3 stack, §6 demo A/B, §9 escopo).
- Tese: conformidade domina com contrapesos independentes; corrupção compensa sob controle arbitrário (limite: poder absoluto).
- Stack: Python + scikit-fuzzy + Flask + HTML/CSS/JS puro. Stateless, sem DB/auth.
- Clean-lite: `presentation -> application -> domain`; `skfuzzy` só em `src/domain`.
- Nomes canônicos: `premio, ausencia_fiscalizacao, concentracao_poder, impunidade` → `payoff`.
- Estrutura: `app.py, src/{domain,application,presentation}, templates/, static/, tests/, requirements.txt`.
- Restrições: prazo médio incremental (sem MVP), demo ao vivo em Linux com venv, interface temática, validação completa (A/B + 15 regras + bordas). PT-BR obrigatório.

## 1. Etapa 1 — Fundação + README (done)
- Esqueleto executável: stubs `fuzzy_engine`/`payoff_service` (`NotImplementedError`), `routes` (`GET / 200` placeholder, `POST /api/calcular 501`), `requirements` pinado (+ `scipy/networkx/packaging` descobertos via venv limpo), `.gitignore` (`.venv/, __pycache__/, *.pyc`).
- README corrigido: link → `docs/documentacao-conceitual.md`, "Como rodar" venv-first real.
- Aceite: `pip install` limpo, `imports OK`, `GET 200`, `POST 501`, `grep skfuzzy` fora do domain vazio.

## 2. Etapa 2 — Motor fuzzy (done)
- `domain/fuzzy_engine.py`: universos `0–10`/`−10–+10`, MFs `trap[0,0,2,4]/tri[2,4,6]/tri[4,6,8]/trap[6,8,10,10]`, saída `trap[-10,-10,-6,-2]/tri[-4,0,4]/trap[2,6,10,10]`, 15 `ctrl.Rule` (14 em 5 grupos + 1 fallback Zona peso 0,1; `~` só onde há NÃO, `|` nas regras 7–8 e 15), centroide; `classificar_payoff` por argmax.
- `application/payoff_service.py`: `execute() -> {valor, termo, regras}`, valida 0–10.
- Aceite: picos `1→g1/4→g2/6→g3/9→g4`; smoke `A(8,1,1,1)=-6.8889`, `B(8,9,9,9)=+4.1624`, gate `(0,10,10,10)` negativo; 15 regras; isolamento Clean.

## 3. Etapa 3 — Validação (done, 22/22)
- `tests/test_payoff.py`: A/B mesmo prêmio (`Δ>5`), 1519 `Compensa`, 1 vetor/regra (ajustes justificados: regra 3 `7→10` evita regra 8 espúria; borda `5→4` evita regra 7 espúria), bordas + varredura monotônica 0→10 (erosão gradual) + `ValueError`.
- Aceite: `pytest 22 passed`, greps idioma/isolamento vazios.

## 4. Etapa 4 — Backend (done)
- `routes.py`: `GET /` template; `POST /api/calcular` valida 4 chaves canônicas 0–10 → `execute()` → `200 {valor 4 casas, termo}`; erro → `400 {erro}` PT-BR. `pytest` pinado `==9.1.1`.
- Aceite: regressão 22/22, `GET 200`, A/B/1519 iguais à Etapa 3, 3× `400` PT-BR.

## 5. Etapa 5 — Frontend + ensaio (done)
- `templates/index.html` + `static/*`: 4 sliders 0–10 passo 0.5 com labels de grau, medidor −10→+10 colorido, presets `A(8,1,1,1)/B(8,9,9,9)/1519(9.5,9,9,9)`, `fetch` sem reload + `400` visível, bloco pedagógico (fuzzificação→regras→defuzzificação), tema selo/coroa/moeda, responsivo. Fix `null` via DevTools.
- Roteiro 60s: A verde → arrastar instituições → B vermelho (mesmo prêmio) → 1519.
- Aceite: 3 presets corretos, console zero erros, regressão 22/22.

## 6. Etapa 6 — Cobertura total + explicabilidade (done)
- `domain/fuzzy_engine.py`: regra 15 fallback curinga Zona (`g2 OU g2 OU g2 OU g2 → zona_risco`, peso 0,1; `% 0,1` se `weight` indisponível), `nova_simulacao()` por chamada (thread-safe), guarda `0.0` sem `KeyError`, clampe `10,0→9,99` em `classificar_payoff`, helper `regras_ativas()` (disparo >0, sem expor `skfuzzy`).
- `application/payoff_service.py`: `execute() -> {valor, termo, regras}` (índices 1-based).
- `routes.py`: `200 {valor 4 casas, termo, regras}`; `400` PT-BR sem vazar chave interna; `500` só falha interna real; fallback `0.0` é `200` válido.
- `templates/index.html` + `static/*`: linha `Regras ativas: …` + pertinências por slider (`g1…g4 %` PT-BR).
- `tests/test_payoff.py`: Bloco D (2 vetores de cobertura do fallback em Zona, varredura `p×f` sem `KeyError`, borda `10`, contrato `regras` via `test_client`) → total 27.
- Aceite: A/B/1519 e `Δ>5` inalterados (`A=-6,8889`, `B=+4,1624`); fallback engolido onde há regra forte (desloc. <0,8, termo igual); varredura sem `KeyError`; regressão 27/27.

## 7. Patches aplicados
- Venv-first + pins extras; `# Regla→# Regra`, `REGLAS→REGRAS`, `cruce→cruzamento`; CSS `--pergamino/oscuro/carmesi→pergaminho/escuro/carmesim`, `deterioro→deterioração`, `capas→camadas`, `término→termo`, `compartem→compartilham`.
- Higiene sugerida: adicionar `.pytest_cache/` ao `.gitignore`.

## 8. Checklist sala (Linux, internet, venv)
- `unzip` (sem `.venv`) → `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python -m pytest tests/ -q` (27 passed) → `python app.py` → abrir `http://127.0.0.1:5000/`.
- Usar sempre `.venv/bin/python` (nunca o global). Se porta ocupada, trocar porta do `app.run`.
