# Lógica Fuzzy Aplicada aos Incentivos da Corrupção Institucional

Projeto acadêmico da disciplina de Sistemas de Informação. Demonstra, de forma funcional e aplicada, os principais conceitos de lógica fuzzy (fuzzificação, variáveis linguísticas, inferência baseada em regras e defuzzificação) em um domínio fora do uso técnico convencional.

## Tese central

Seguir as regras é a estratégia racionalmente dominante quando os contrapesos institucionais operam de forma independente. A corrupção só se torna vantajosa quando um agente passa a ter controle arbitrário sobre essas próprias variáveis institucionais — o caso-limite sendo um poder absoluto e sem restrição. A teoria dos jogos entra apenas como framework conceitual (não há cálculo de equilíbrio de Nash); o núcleo do projeto é o sistema de inferência fuzzy.

## Entradas e saída

Quatro entradas canônicas, cada uma em universo 0 a 10 (grau 1 = mais favorável à conformidade, grau 4 = mais favorável à corrupção, §5.1):

- `premio` — valor do poder ou benefício em disputa
- `ausencia_fiscalizacao` — ausência/captura da fiscalização (mídia/povo)
- `concentracao_poder` — concentração de poder / ausência de separação de poderes
- `impunidade` — impunidade (ausência de punição certa e coerente)

Saída: `payoff` — payoff líquido estimado de agir corruptamente, em universo -10 a +10, classificado em três termos: *Não compensa*, *Zona de risco* ou *Compensa se corromper* (§5.1).

## Demo núcleo: comparação A/B

Manter o valor do prêmio constante e variar apenas os fatores institucionais — Cenário A (contrapesos fortes, payoff baixo ou negativo) vs. Cenário B (contrapesos capturados, payoff que cruza o limiar). É esse contraste que evidencia a tese: o incentivo perverso nasce da degradação dos contrapesos institucionais, não de uma mudança na natureza ou na ganância do agente (§6).

## Stack e arquitetura

- **Motor fuzzy:** Python + [scikit-fuzzy](https://pypi.org/project/scikit-fuzzy/)
- **Backend:** Flask
- **Frontend:** HTML, CSS e JavaScript (sem framework adicional)

Sem banco de dados e sem autenticação — o sistema é *stateless*: cada cálculo é independente, não há histórico a salvar (§5.3, §9).

Dependência entre camadas: `presentation -> application -> domain`. Nenhum `import skfuzzy` fora de `src/domain`.

```
app.py                          # composition root: cria Flask, registra blueprint
src/domain/fuzzy_engine.py      # motor fuzzy (universos, MFs, regras)
src/application/payoff_service.py
src/presentation/routes.py      # Blueprint api: GET / e POST /api/calcular
templates/index.html
static/style.css
static/app.js
tests/
requirements.txt
```

## Como rodar

```bash
python3 --version        # 3.10 ou superior
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrir http://127.0.0.1:5000/ no navegador.

## Interface (Etapa 5)

A página final combina os 4 sliders de entrada — `premio`, `ausencia_fiscalizacao`, `concentracao_poder` e `impunidade`, cada um no universo 0–10 com passo 0,5 — e um medidor contínuo (pista verde/âmbar/vermelho) que posiciona o payoff entre −10 e +10, com número decimal em formato PT-BR ("9,5") e termo classificado: *Não compensa*, *Zona de risco* ou *Compensa se corromper*.

Cenários prontos (presets):

- **Cenário A** — (8, 1, 1, 1): contrapesos plenos, payoff negativo
- **Cenário B** — (8, 9, 9, 9): mesmo prêmio, instituições capturadas, payoff positivo
- **1519** — (9.5, 9, 9, 9): prêmio altíssimo e colapso total (Fugger, sete eleitores, trono imperial)

## API: POST /api/calcular

Contrato JSON:

```json
{
  "premio": 8,
  "ausencia_fiscalizacao": 1,
  "concentracao_poder": 1,
  "impunidade": 1
}
```

Resposta 200:

```json
{"valor": -6.8889, "termo": "Não compensa"}
```

`valor` é o payoff arredondado a 4 decimais (JSON com ponto decimal); `termo` é uma das três classificações. Campos ausentes, não numéricos ou fora de 0–10 respondem 400 com `{"erro": "..."}` em PT-BR.

## Estado atual

Etapas 1 a 5 concluídas: motor fuzzy completo (universos, funções de pertinência, 14 regras em 5 grupos, defuzzificação por centroide), serviço de aplicação, API real, bateria de testes e interface final temática. O projeto está pronto para a demo.

## Testes

```bash
python -m pytest tests/ -q
```

Bateria de 22 testes que validam os cenários canônicos A/B/1519, a cobertura de um vetor por regra da base (§5.2) e os casos de borda do contrato de entrada.

## Documentação

A documentação conceitual completa — contexto histórico, tese, justificativa do uso de lógica fuzzy, universos de discurso, funções de pertinência e base de regras — está em [`docs/documentacao-conceitual.md`](docs/documentacao-conceitual.md).

## Contexto acadêmico

Projeto desenvolvido para a disciplina de Sistemas de Informação, inspirado no material de referência do Prof. Marcelo C. Mussel sobre sistemas fuzzy.